"""爬虫入口：调度 DoubanCrawler，生成 JSONL 到 data/raw。"""
from __future__ import annotations

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
    crawler = DoubanCrawler()
    total = crawler.run()
    print(f"[crawler] 完成，共写入 {total} 条")


if __name__ == "__main__":
    main()