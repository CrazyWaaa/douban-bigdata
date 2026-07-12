"""爬虫入口:调度 DoubanCrawler,生成 JSONL 到 data/raw。
支持断点续爬(--resume)、失败名单(--bad-ids)、代理文件(--proxy-file)。
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.douban import DoubanCrawler  # noqa: E402


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="豆瓣电影爬虫(降速 + 断点续爬 + 代理友好)",
    )
    parser.add_argument(
        "--target", type=int, default=250,
        help="目标抓取数量(默认 250,Top250 全量)",
    )
    parser.add_argument(
        "--out", default="movies.jsonl",
        help="输出文件名(默认 movies.jsonl)",
    )
    parser.add_argument(
        "--sources", default="top250",
        help="数据源,逗号分隔: top250,genres,countries(默认只 top250)",
    )
    parser.add_argument(
        "--enrich-all", action="store_true",
        help="对全部记录做详情页 enrich(默认只 enrich 前 N 条,N = target)",
    )
    parser.add_argument(
        "--no-resume", action="store_true",
        help="禁用断点续爬(默认开启,会跳过已存在的 douban_id)",
    )
    parser.add_argument(
        "--proxy-file", default=None,
        help="代理列表文件路径,每行一个,支持 # 注释",
    )
    parser.add_argument(
        "--min-interval", type=float, default=5.0,
        help="请求最小间隔秒数(默认 5)",
    )
    parser.add_argument(
        "--max-interval", type=float, default=10.0,
        help="请求最大间隔秒数(默认 10)",
    )
    args = parser.parse_args()

    crawler = DoubanCrawler()
    # 覆盖配置
    crawler.cfg.target_count = args.target
    crawler.cfg.request_interval_min = args.min_interval
    crawler.cfg.request_interval_max = args.max_interval
    # 自适应:如果用户没显式覆盖,根据代理数量调整间隔(有代理=可以更快)
    if not args.proxy_file and args.min_interval == 5.0 and args.max_interval == 10.0:
        # 单 IP 跑 250 条,稍微再稳一点
        pass
    crawler.cfg.request_interval_max = args.max_interval

    # 加载代理文件
    if args.proxy_file:
        n = crawler.load_extra_proxies(args.proxy_file)
        if n == 0:
            print(f"[warn] --proxy-file {args.proxy_file} 加载了 0 条代理,继续裸跑")

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    total = crawler.run(
        enrich_top_n=args.target,
        out_name=args.out,
        enrich_all=args.enrich_all,
        sources=sources,
        resume=not args.no_resume,
    )

    print(f"[crawler] 完成,共写入 {total} 条到 {crawler.cfg.output_dir}\\{args.out}")
    bad_path = os.path.join(crawler.cfg.output_dir, crawler.cfg.bad_ids_file)
    if os.path.exists(bad_path):
        with open(bad_path, "r", encoding="utf-8") as f:
            bad_lines = f.readlines()
        print(f"[crawler] 失败名单 {len(bad_lines)} 条: {bad_path}")
    print(f"[crawler] 估算耗时: 250 条 × ~{int((args.min_interval + args.max_interval)/2)}s ≈ {int(250 * (args.min_interval + args.max_interval)/2 / 60)} 分钟")


if __name__ == "__main__":
    main()