"""本地验证脚本（无需 Hadoop/Spark 集群）。

用法：
    # 1) 先跑爬虫（可选；已有 crawler/data/raw/*.jsonl 可跳过）
    python scripts/verify_local.py crawl

    # 2) 把 JSONL 直接写进 MySQL（不用 spark-submit）
    python scripts/verify_local.py load --db-host 127.0.0.1 --db-user douban --db-password douban_pwd

    # 3) 打印统计（给前端看字段）
    python scripts/verify_local.py stats

依赖： pip install requests beautifulsoup4 lxml pymysql fake-useragent
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

# 允许本脚本能 import 顶层包 crawler
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _find_jsonl() -> list[Path]:
    folder = ROOT / "crawler" / "data" / "raw"
    if not folder.exists():
        # 也尝试 data/raw
        folder2 = ROOT / "data" / "raw"
        if folder2.exists():
            folder = folder2
    files = sorted(folder.glob("*.jsonl")) if folder.exists() else []
    return files


def cmd_crawl(args) -> None:
    from crawler.douban import DoubanCrawler
    c = DoubanCrawler()
    total = c.run(enrich_top_n=args.enrich)
    print(f"[OK] 共写入 {total} 条，输出目录: {c.cfg.output_dir}")


def cmd_stats(args) -> None:
    files = _find_jsonl()
    if not files:
        print("[WARN] 未找到 *.jsonl，请先执行 'python scripts/verify_local.py crawl'")
        return
    fields_seen: set[str] = set()
    per_file_counts: list[tuple[str, int]] = []
    for fp in files:
        count = 0
        with fp.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                fields_seen.update(obj.keys())
                count += 1
        per_file_counts.append((fp.name, count))

    print("=== 文件统计 ===")
    for name, count in per_file_counts:
        print(f"  {name}: {count} 行")
    print()
    print("=== 解析到的字段（按字母序）===")
    for fld in sorted(fields_seen):
        print(f"  - {fld}")
    print()
    print("=== 你期望的字段 vs 解析到的字段 ===")
    expected = {
        "title", "director", "rating", "rating_count", "year",
        "country", "genre", "actors", "poster_url", "summary",
        "languages", "release_date", "runtime", "runtime_minutes",
        "quote", "rating_stars", "better_than", "comment_short_count",
        "comment_review_count", "discussion_count", "also_know_as",
        "imdb_id", "official_sites", "related_pics", "detail_url",
    }
    missing = expected - fields_seen
    extra = fields_seen - expected
    if missing:
        print("  未出现:", sorted(missing))
    else:
        print("  期望字段全部存在 ✓")
    if extra:
        print("  额外字段:", sorted(extra))


def _flatten(obj: dict) -> dict:
    out: dict[str, Any] = {}
    for k, v in obj.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v, ensure_ascii=False)
        else:
            out[k] = v
    return out


def cmd_load(args) -> None:
    import pymysql

    files = _find_jsonl()
    if not files:
        print("[WARN] 未找到 *.jsonl，先跑爬虫或把 JSONL 放到 crawler/data/raw/")
        return

    # 先不指定数据库：避免 douban 数据库还没建时就报 "Unknown database"
    conn = pymysql.connect(
        host=args.db_host, port=args.db_port, user=args.db_user,
        password=args.db_password, charset="utf8mb4",
        connect_timeout=10,
    )
    try:
        db_name = args.db_name or "douban"
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cur.execute(f"USE {db_name}")
            cur.execute(
                """CREATE TABLE IF NOT EXISTS movie (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    douban_id VARCHAR(32) NOT NULL UNIQUE,
                    title VARCHAR(255) NOT NULL,
                    director VARCHAR(512), actors TEXT,
                    genre VARCHAR(128), country VARCHAR(256),
                    year SMALLINT, rating DECIMAL(3,1), rating_count INT,
                    summary TEXT, poster_url VARCHAR(512),
                    detail_url VARCHAR(512), languages VARCHAR(256),
                    release_date VARCHAR(512), runtime VARCHAR(128),
                    runtime_minutes INT, quote VARCHAR(1024),
                    better_than VARCHAR(512), also_know_as VARCHAR(512),
                    imdb_id VARCHAR(64), official_sites VARCHAR(512),
                    comment_short_count INT, comment_review_count INT,
                    discussion_count INT, rating_stars VARCHAR(512),
                    related_pics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_year(year), INDEX idx_rating(rating),
                    INDEX idx_runtime(runtime_minutes)
                ) DEFAULT CHARSET=utf8mb4"""
            )

            # upsert 写入
            cols = [
                "douban_id", "title", "director", "actors", "genre",
                "country", "year", "rating", "rating_count", "summary",
                "poster_url", "detail_url", "languages", "release_date",
                "runtime", "runtime_minutes", "quote", "better_than",
                "also_know_as", "imdb_id", "official_sites",
                "comment_short_count", "comment_review_count",
                "discussion_count", "rating_stars", "related_pics",
            ]
            placeholders = ",".join(["%s"] * len(cols))
            updates = ",".join([f"{c}=VALUES({c})" for c in cols if c != "douban_id"])
            sql = (
                f"INSERT INTO movie ({','.join(cols)}) VALUES ({placeholders}) "
                f"ON DUPLICATE KEY UPDATE {updates}"
            )

            written = 0
            for fp in files:
                with fp.open("r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        obj = _flatten(json.loads(line))
                        values = [obj.get(c) for c in cols]
                        cur.execute(sql, values)
                        written += 1
                        if written % 50 == 0:
                            conn.commit()
            conn.commit()
            cur.execute("SELECT COUNT(*) FROM movie")
            (total,) = cur.fetchone()
            print(f"[OK] 写入 {written} 条；movie 表共 {total} 条")

            # 聚合
            for agg_name, col in (("agg_genre", "genre"), ("agg_country", "country"), ("agg_year", "year")):
                cur.execute(
                    f"""CREATE TABLE IF NOT EXISTS {agg_name} (
                        {col} VARCHAR(64) PRIMARY KEY, movie_count INT, avg_rating DECIMAL(3,2)
                    )"""
                )
                if col == "year":
                    cur.execute(
                        f"REPLACE INTO {agg_name} ({col}, movie_count, avg_rating) "
                        f"SELECT year, COUNT(*), ROUND(AVG(rating),2) FROM movie "
                        f"WHERE year IS NOT NULL GROUP BY year"
                    )
                else:
                    cur.execute(
                        f"SELECT {col}, COUNT(*), ROUND(AVG(rating),2) FROM movie "
                        f"WHERE {col} IS NOT NULL AND {col} <> '' GROUP BY {col}"
                    )
                    if col == "genre":
                        rows = cur.fetchall()
                        # 简单拆分，类型可能是 "剧情 / 爱情"
                        exploded: dict[str, list[float]] = {}
                        for val, cnt, avg in rows:
                            for t in [s.strip() for s in str(val).replace("/", " ").split() if s.strip()]:
                                exploded.setdefault(t, []).append(float(avg) if avg else 0.0)
                        # 写库：按 avg 简单取平均，cnt 用出现次数
                        cur.execute(f"TRUNCATE TABLE {agg_name}")
                        for t, avgs in exploded.items():
                            cur.execute(
                                f"INSERT INTO {agg_name} ({col}, movie_count, avg_rating) VALUES (%s,%s,%s)",
                                (t, len(avgs), round(sum(avgs) / len(avgs), 2)),
                            )
                    else:
                        cur.execute(
                            f"REPLACE INTO {agg_name} ({col}, movie_count, avg_rating) "
                            f"SELECT {col}, COUNT(*), ROUND(AVG(rating),2) FROM movie "
                            f"WHERE {col} IS NOT NULL AND {col} <> '' GROUP BY {col}"
                        )
                conn.commit()
                cur.execute(f"SELECT COUNT(*) FROM {agg_name}")
                (n,) = cur.fetchone()
                print(f"  - {agg_name}: {n} 行")
    finally:
        conn.close()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(description="Douban 本地验证：爬虫 / 写 MySQL / 统计")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_crawl = sub.add_parser("crawl", help="跑一次 Top250 爬虫 + enrich")
    p_crawl.add_argument("--enrich", type=int, default=250, help="对前 N 条做详情 enrich，默认 250 全量")

    p_load = sub.add_parser("load", help="把 JSONL 直接写进 MySQL（不走 Spark）")
    p_load.add_argument("--db-host", default=os.getenv("DOUBAN_DB_HOST", "127.0.0.1"))
    p_load.add_argument("--db-port", type=int, default=int(os.getenv("DOUBAN_DB_PORT", "3306")))
    p_load.add_argument("--db-user", default=os.getenv("DOUBAN_DB_USER", "douban"))
    p_load.add_argument("--db-password", default=os.getenv("DOUBAN_DB_PASSWORD", "douban_pwd"))
    p_load.add_argument("--db-name", default=os.getenv("DOUBAN_DB_NAME", "douban"))

    sub.add_parser("stats", help="打印本地 JSONL 的字段统计")

    args = parser.parse_args()
    if args.cmd == "crawl": cmd_crawl(args)
    elif args.cmd == "load": cmd_load(args)
    elif args.cmd == "stats": cmd_stats(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
