"""一键补齐 movie 表详情页字段

数据流:
    1. 从 MySQL movie 表导出全部 douban_id
    2. 读取 data/raw/movies.jsonl(若存在), 跳过 detail 已完整的 ID
    3. 调用 crawler.douban.DoubanCrawler.enrich_only() 补抓详情
    4. 追加/合并写回 data/raw/movies.jsonl
    5. 调用 spark/etl.py 的 write_movies 逻辑(通过 docker compose etl profile)

用法:
    # 默认: 从 MySQL 导ID, 补抓到 data/raw/movies.jsonl
    python scripts/enrich_all_details.py

    # 指定输出文件
    python scripts/enrich_all_details.py --out data/raw/movies.jsonl

    # 不写库(只爬)
    python scripts/enrich_all_details.py --no-write

    # 强制全量重抓(忽略 JSONL 中已存在的记录)
    python scripts/enrich_all_details.py --force

    # 自定义 ID 来源(跳过 MySQL 查询)
    python scripts/enrich_all_details.py --ids-file data/raw/my_ids.txt

设计要点:
    - 断点: 通过 JSONL 中 douban_id 判重, 已存在的会 enrich+merge 覆盖
    - 跳过阈值: summary / runtime_minutes / languages / imdb_id 任意 NULL 即认为缺失
    - 速率: 单 IP, 间隔 6-15s/条, 250 条约 30-50 分钟
    - 失败重试: enrich_only 内部走同一套 retry + bad_ids 机制
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from crawler.config import CONFIG
from crawler.douban import DoubanCrawler

LOGGER = logging.getLogger("enrich_all")

# === 跳过的关键字段: 任一为空即视为未抓详 ===
KEY_DETAIL_FIELDS = ("summary", "runtime_minutes", "languages", "imdb_id")


def query_douban_ids_from_mysql(host: str, port: int, user: str,
                                 password: str, database: str) -> list[str]:
    """从 MySQL movie 表导出全部 douban_id"""
    import pymysql  # noqa: PLC0415
    conn = pymysql.connect(host=host, port=port, user=user, password=password,
                           database=database, charset="utf8mb4")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT douban_id FROM movie ORDER BY id")
            return [str(r[0]) for r in cur.fetchall()]
    finally:
        conn.close()


def load_existing_jsonl(path: Path) -> dict[str, dict]:
    """读已有 JSONL, 返回 {douban_id: record}"""
    if not path.exists():
        return {}
    result: dict[str, dict] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            did = str(obj.get("douban_id", "")).strip()
            if did:
                result[did] = obj
    return result


def is_detail_complete(rec: dict) -> bool:
    """判断详情页字段是否完整"""
    for f in KEY_DETAIL_FIELDS:
        v = rec.get(f)
        if v is None or v == "" or v == 0:
            return False
    return True


def merge_record(old: dict, new: dict) -> dict:
    """合并新旧记录: 以 new 为主, 保留 old 中 new 没有的字段"""
    merged = dict(old)
    merged.update({k: v for k, v in new.items() if v not in (None, "", 0)})
    return merged


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(ROOT / "data" / "raw" / "movies.jsonl"),
                        help="输出 JSONL 路径")
    parser.add_argument("--ids-file", default=None,
                        help="自定义 douban_id 列表文件, 每行一个; 留空则从 MySQL 导出")
    parser.add_argument("--force", action="store_true",
                        help="强制重抓, 忽略 JSONL 中已存在的记录")
    parser.add_argument("--no-write", action="store_true",
                        help="只爬不写库(默认会合并写回 JSONL)")
    parser.add_argument("--min-interval", type=float, default=6.0)
    parser.add_argument("--max-interval", type=float, default=15.0)

    # MySQL 连接参数(从 .env 读, 也可手动覆盖)
    parser.add_argument("--db-host", default=os.environ.get("MYSQL_HOST_PORT_HOST", "127.0.0.1"))
    parser.add_argument("--db-port", type=int, default=int(os.environ.get("MYSQL_HOST_PORT", "33306")))
    parser.add_argument("--db-user", default=os.environ.get("MYSQL_DB_USER", "douban"))
    parser.add_argument("--db-password", default=os.environ.get("MYSQL_DB_PASSWORD", "douban_pwd"))
    parser.add_argument("--db-name", default=os.environ.get("MYSQL_DB_NAME", "douban"))

    args = parser.parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. 拿 ID 清单
    if args.ids_file:
        ids_file = Path(args.ids_file)
        if not ids_file.exists():
            LOGGER.error("ids file not found: %s", ids_file)
            return 2
        ids = [line.strip() for line in ids_file.read_text(encoding="utf-8").splitlines()
               if line.strip()]
        LOGGER.info("loaded %d ids from %s", len(ids), ids_file)
    else:
        try:
            ids = query_douban_ids_from_mysql(
                args.db_host, args.db_port, args.db_user,
                args.db_password, args.db_name,
            )
            LOGGER.info("loaded %d ids from MySQL %s.%s", len(ids), args.db_host, args.db_name)
        except Exception as exc:
            LOGGER.error("query MySQL failed: %s", exc)
            LOGGER.error("hint: --ids-file data/raw/all_ids.txt 也可手动指定")
            return 2

    # 2. 读已有 JSONL, 计算需要重抓的 ID
    existing = load_existing_jsonl(out_path)
    if existing:
        LOGGER.info("existing records in %s: %d", out_path, len(existing))

    if args.force:
        to_crawl = ids
        LOGGER.info("[force] will recrawl all %d ids", len(to_crawl))
    else:
        to_crawl = []
        for did in ids:
            rec = existing.get(did)
            if rec is None:
                to_crawl.append(did)  # JSONL 里没有
            elif not is_detail_complete(rec):
                to_crawl.append(did)  # JSONL 有但详情不全
        LOGGER.info("need to recrawl: %d (already complete: %d)",
                    len(to_crawl), len(ids) - len(to_crawl))

    if not to_crawl:
        LOGGER.info("nothing to do, exit")
        return 0

    # 3. 跑爬虫
    cfg = CONFIG
    cfg.request_interval_min = args.min_interval
    cfg.request_interval_max = args.max_interval

    crawler = DoubanCrawler(cfg)
    # enrich_only 内部 sleep 是 base + jitter, 这里我们限制最小间隔
    LOGGER.info("crawling %d ids with interval %s-%ss",
                len(to_crawl), args.min_interval, args.max_interval)
    # enrich_only 会 append 到自己的文件, 我们让它写到 .enriched.jsonl,
    # 再合并回主 JSONL。这样主文件可以安全断点续传。
    enriched_path = out_path.with_suffix('.enriched.jsonl')
    if enriched_path.exists():
        enriched_path.unlink()  # 清掉上次的中间产物
    crawler.enrich_only(to_crawl, out_name=enriched_path.name)

    # 4. 合并回 out_path
    if not args.no_write:
        # 主文件提供'基础字段'(title/rating/poster 等), 中间文件提供'新详情字段'
        new_records = load_existing_jsonl(enriched_path)
        # enrich_only 写的文件名是 out_name, 但默认会 append 到同名文件
        # 所以这里我们做一次 merge: 把已存在的覆盖旧字段
        final = dict(existing)
        for did, rec in new_records.items():
            if did in final:
                final[did] = merge_record(final[did], rec)
            else:
                final[did] = rec

        # 按 ID 排序写回, 方便 diff
        with out_path.open("w", encoding="utf-8") as f:
            for did in sorted(final.keys(), key=lambda x: int(x) if x.isdigit() else x):
                f.write(json.dumps(final[did], ensure_ascii=False) + "\n")
        LOGGER.info("merged %d records to %s", len(final), out_path)
    else:
        LOGGER.info("--no-write: skip JSONL merge")

    return 0


if __name__ == "__main__":
    sys.exit(main())