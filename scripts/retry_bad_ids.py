"""补抓失败名单(bad_ids.txt)里的 douban_id。

用法:
    # 补抓 bad_ids.txt 里所有失败的 id(写到 movies_retry.jsonl)
    python scripts/retry_bad_ids.py

    # 自定义输出文件名
    python scripts/retry_bad_ids.py --out movies_retry2.jsonl

    # 用代理
    python scripts/retry_bad_ids.py --proxy-file crawler/proxies.txt
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


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument("--bad-ids", default=str(ROOT / "data" / "raw" / "bad_ids.txt"))
    parser.add_argument("--out", default="movies_retry.jsonl")
    parser.add_argument("--proxy-file", default=None)
    parser.add_argument("--min-interval", type=float, default=15.0)
    parser.add_argument("--max-interval", type=float, default=35.0)
    args = parser.parse_args()

    bad_path = Path(args.bad_ids)
    if not bad_path.exists():
        print(f"[err] {bad_path} 不存在")
        return 1

    ids: list[str] = []
    with bad_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            did = line.split("\t")[0].strip()
            if did:
                ids.append(did)
    if not ids:
        print("[ok] 没有失败 id")
        return 0

    print(f"[info] 将补抓 {len(ids)} 个失败 id,间隔 {args.min_interval}-{args.max_interval}s")

    cfg = CONFIG
    cfg.request_interval_min = args.min_interval
    cfg.request_interval_max = args.max_interval

    crawler = DoubanCrawler(cfg)
    if args.proxy_file:
        crawler.load_extra_proxies(args.proxy_file)

    out_path = ROOT / "data" / "raw" / args.out
    seen: set[str] = set()
    if out_path.exists():
        with out_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    did = obj.get("douban_id")
                    if did:
                        seen.add(str(did))
                except Exception:
                    pass

    with out_path.open("a", encoding="utf-8") as f:
        ok = 0
        for did in ids:
            if did in seen:
                continue
            from crawler.parser import Movie
            m = Movie(douban_id=did, title="")
            crawler.enrich(m)
            if m.title or m.director:
                f.write(json.dumps({
                    "douban_id": m.douban_id, "title": m.title, "director": m.director,
                    "actors": m.actors, "genre": m.genre, "country": m.country,
                    "year": m.year, "rating": m.rating, "rating_count": m.rating_count,
                    "summary": m.summary, "poster_url": m.poster_url,
                    "detail_url": m.detail_url, "languages": m.languages,
                    "release_date": m.release_date, "runtime": m.runtime,
                    "runtime_minutes": m.runtime_minutes, "quote": m.quote,
                    "better_than": m.better_than, "also_know_as": m.also_know_as,
                    "imdb_id": m.imdb_id, "official_sites": m.official_sites,
                    "comment_short_count": m.comment_short_count,
                    "comment_review_count": m.comment_review_count,
                    "discussion_count": m.discussion_count,
                    "rating_stars": m.rating_stars, "related_pics": m.related_pics,
                }, ensure_ascii=False) + "\n")
                ok += 1
                print(f"[ok] {did} -> {m.title}")
            else:
                print(f"[fail] {did} 仍未抓到")

    print(f"[done] 补抓完成,新增 {ok} 条 -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main() or 0)