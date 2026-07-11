"""豆瓣抓取主逻辑：curl_cffi 模拟浏览器 TLS 指纹 + requests 兜底 + 保守限速。
豆瓣识别爬虫主要靠三条：
  1) requests / urllib3 的 JA3 指纹与真实浏览器不同；  2) 请求头缺 Sec-Fetch-* / Priority 等现代字段；  3) 1~3 秒就翻页，远超真人浏览节奏"""
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
from .ua import common_headers, pick_user_agent, reset_user_agent

LOGGER = logging.getLogger(__name__)

# curl_cffi：直接模拟 Chrome/Edge 等浏览器 TLS 指纹，是对付 429 的核心手段；# 未安装则自动退回 requests
try:
    from curl_cffi import requests as cffi_requests  # type: ignore
    _HAS_CFFI = True
except Exception:
    _HAS_CFFI = False


class DoubanCrawler:
    def __init__(self, config: CrawlerConfig | None = None) -> None:
        self.cfg = config or CONFIG
        self.pool = ProxyPool(self.cfg)
        # 进程内 UA 固定，避免每次请求都换        self.ua = pick_user_agent()
        # 一个 requests Session，用来保持 cookie（第一次访问后的 cookie 很重要）
        self._requests_session = requests.Session()
        os.makedirs(self.cfg.output_dir, exist_ok=True)

        # 保守限速：豆瓣对翻页很敏感，把默认 1~3s 拉到 4~8s
        self.cfg.request_interval_min = max(self.cfg.request_interval_min, 6.0)
        self.cfg.request_interval_max = max(self.cfg.request_interval_max, 15.0)

    def _headers(self, referer: str | None = None) -> dict:
        """返回接近真实浏览器的完整请求头（UA 全程固定）。"""
        return common_headers(referer=referer)

    def _sleep(self, base: float | None = None, jitter: float = 1.5) -> None:
        """在两次请求之间 sleep；失败时会传入更大的 base 做退避。"""
        if base is None:
            base = random.uniform(self.cfg.request_interval_min, self.cfg.request_interval_max)
        secs = base + random.uniform(0, jitter)
        time.sleep(secs)

    def _fetch(self, url: str, referer: str | None = None) -> str | None:
        """
        单次抓取：
          - curl_cffi 优先（模拟浏览器 TLS，过 429 主手段）
          - 失败 / 未安装则退回 requests
          - 遇到 429/403 时拉长退避，5 次重试里会换 UA 一次
        """
        headers = self._headers(referer)
        proxy = self.pool.pick()

        for attempt in range(self.cfg.max_retries):
            try:
                if _HAS_CFFI:
                    kwargs = dict(
                        headers=headers,
                        timeout=30,
                        impersonate="chrome",   # 关键：模拟 Chrome 的 TLS 指纹
                    )
                    if proxy:
                        kwargs["proxies"] = proxy
                    resp = cffi_requests.get(url, **kwargs)
                else:
                    kwargs = dict(headers=headers, timeout=30)
                    if proxy:
                        kwargs["proxies"] = proxy
                    resp = self._requests_session.get(url, **kwargs)

                if resp.status_code == 200:
                    return resp.text

                # 429 / 403 / 5xx：退避后重试
                if resp.status_code in (429, 403) or resp.status_code >= 500:
                    # 429 至少从 10s 起步，指数退避                    wait = max(10.0, self.cfg.backoff_base ** attempt * 2)
                    LOGGER.warning(
                        "retry %s for %s after %.1fs (status=%s)",
                        attempt + 1, url, wait, resp.status_code,
                    )
                    time.sleep(wait)
                    if attempt == self.cfg.max_retries // 2:
                        # 中途换一个 UA，避免被同一指纹连续限制
                        self.ua = reset_user_agent()
                        headers = self._headers(referer)
                    continue

                # 其他状态码（如 418 / 404）：直接放弃
                LOGGER.error("non-retry status %s for %s", resp.status_code, url)
                return None
            except Exception as exc:
                wait = max(8.0, self.cfg.backoff_base ** attempt * 2)
                LOGGER.warning("network error %s on %s, retry after %.1fs", exc, url, wait)
                time.sleep(wait)
        return None

    def crawl_top250(self) -> Iterable[Movie]:
        for page in range(self.cfg.top250_pages):
            url = f"{self.cfg.top250_url}?start={page * 25}&filter="
            # 第一页没 referer，后面一页的 referer 就是上一页            referer = f"{self.cfg.top250_url}?start={(page - 1) * 25}&filter=" if page > 0 else self.cfg.top250_url
            html = self._fetch(url, referer=referer)
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

    def run(
        self,
        enrich_top_n: int = 250,
        out_name: str = "movies.jsonl",
        enrich_all: bool = False,
    ) -> int:
        out_path = os.path.join(self.cfg.output_dir, out_name)
        seen: set[str] = set()
        total = 0
        with open(out_path, "w", encoding="utf-8") as fout:
            for movie in self.crawl_top250():
                if movie.douban_id in seen:
                    continue
                seen.add(movie.douban_id)
                if enrich_all or total < enrich_top_n:
                    self.enrich(movie)
                fout.write(json.dumps(to_dict(movie), ensure_ascii=False) + "\n")
                fout.flush()
                total += 1
                if total >= self.cfg.target_count:
                    break
        LOGGER.info("wrote %s records to %s", total, out_path)
        return total

    def enrich_only(self, ids: list[str], out_name: str = "movies_enriched.jsonl") -> int:
        out_path = os.path.join(self.cfg.output_dir, out_name)
        rewritten = 0
        for douban_id in ids:
            movie = Movie(douban_id=douban_id, title="")
            self.enrich(movie)
            if movie.summary or movie.runtime or movie.languages:
                with open(out_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(to_dict(movie), ensure_ascii=False) + "\n")
                rewritten += 1
        LOGGER.info("enriched %s records -> %s", rewritten, out_path)
        return rewritten

