"""豆瓣抓取主逻辑：限速 + UA 轮换 + 代理池 + 指数退避重试。"""
from __future__ import annotations

import json
import logging
import os
import random
import time
from typing import Iterable

import requests
from bs4 import BeautifulSoup

from .config import CONFIG, CrawlerConfig
from .parser import Movie, parse_top250_item, parse_subject_page, to_dict
from .proxy import ProxyPool
from .ua import pick_user_agent

LOGGER = logging.getLogger(__name__)


class DoubanCrawler:
    def __init__(self, config: CrawlerConfig | None = None) -> None:
        self.cfg = config or CONFIG
        self.pool = ProxyPool(self.cfg)
        self.session = requests.Session()
        os.makedirs(self.cfg.output_dir, exist_ok=True)

    def _headers(self) -> dict:
        return {
            "User-Agent": pick_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Referer": "https://movie.douban.com/",
        }

    def _sleep(self) -> None:
        secs = random.uniform(self.cfg.request_interval_min, self.cfg.request_interval_max)
        time.sleep(secs)

    def _fetch(self, url: str, referer: str | None = None) -> str | None:
        for attempt in range(self.cfg.max_retries):
            try:
                kwargs = {
                    "headers": {**self._headers(), **({"Referer": referer} if referer else {})},
                    "timeout": 15,
                }
                proxy = self.pool.pick()
                if proxy:
                    kwargs["proxies"] = proxy
                resp = self.session.get(url, **kwargs)
                if resp.status_code == 200:
                    return resp.text
                if resp.status_code in self.cfg.retry_status or resp.status_code == 418:
                    wait = self.cfg.backoff_base ** attempt
                    LOGGER.warning(
                        "retry %s for %s after %.1fs (status=%s)",
                        attempt + 1, url, wait, resp.status_code,
                    )
                    time.sleep(wait)
                    continue
                LOGGER.error("non-retry status %s for %s", resp.status_code, url)
                return None
            except requests.RequestException as exc:
                wait = self.cfg.backoff_base ** attempt
                LOGGER.warning("network error %s on %s, retry after %.1fs", exc, url, wait)
                time.sleep(wait)
        return None

    def crawl_top250(self) -> Iterable[Movie]:
        for page in range(self.cfg.top250_pages):
            url = f"{self.cfg.top250_url}?start={page * 25}&filter="
            html = self._fetch(url)
            if not html:
                LOGGER.warning("Top250 page=%s fetch failed", page)
                continue
            soup = BeautifulSoup(html, "lxml")
            count = 0
            for li in soup.select("ol.grid_view > li"):
                movie = parse_top250_item(li)
                if movie is None:
                    continue
                yield movie
                count += 1
            LOGGER.info("Top250 page=%s movies=%s", page, count)
            self._sleep()

    def enrich(self, movie: Movie) -> Movie:
        url = f"{self.cfg.movie_detail_base}{movie.douban_id}/"
        html = self._fetch(url, referer=self.cfg.top250_url)
        if html:
            try:
                parse_subject_page(html, movie)
            except Exception as exc:
                LOGGER.debug("enrich fail %s: %s", movie.douban_id, exc)
        self._sleep()
        return movie

    def run(self, enrich_top_n: int = 50, out_name: str = "movies.jsonl") -> int:
        out_path = os.path.join(self.cfg.output_dir, out_name)
        seen: set[str] = set()
        total = 0
        with open(out_path, "w", encoding="utf-8") as fout:
            for movie in self.crawl_top250():
                if movie.douban_id in seen:
                    continue
                seen.add(movie.douban_id)
                if total < enrich_top_n and total >= 0:
                    self.enrich(movie)
                fout.write(json.dumps(to_dict(movie), ensure_ascii=False) + "\n")
                fout.flush()
                total += 1
                if total >= self.cfg.target_count:
                    break
        LOGGER.info("wrote %s records to %s", total, out_path)
        return total

    def enrich_only(self, ids: list[str], out_name: str = "movies_enriched.jsonl") -> int:
        """对已有 IDs 重试详情页，成功才覆盖写。"""
        out_path = os.path.join(self.cfg.output_dir, out_name)
        rewritten = 0
        for douban_id in ids:
            movie = Movie(
                douban_id=douban_id, title="", director="", actors="",
                year=None, country="", genre="", rating=None,
                rating_count=None, summary="", poster_url="",
            )
            self.enrich(movie)
            # 只有当 summary 真正拿到才覆盖；否则保留原 movie 中的 title 等
            if movie.summary:
                with open(out_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(to_dict(movie), ensure_ascii=False) + "\n")
                rewritten += 1
        LOGGER.info("enriched %s records -> %s", rewritten, out_path)
        return rewritten