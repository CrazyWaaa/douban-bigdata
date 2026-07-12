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
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from .config import CONFIG, CrawlerConfig
from .parser import Movie, parse_top250_item, parse_explore_card, parse_subject_page, to_dict
from .proxy import ProxyPool
from .ua import common_headers, pick_user_agent, reset_user_agent
from .config import load_proxies_from_file

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
        # 运行时再注入代理文件加载(在 CLI 阶段调用)
        # 进程内 UA 固定，避免每次请求都换        self.ua = pick_user_agent()
        # 一个 requests Session，用来保持 cookie（第一次访问后的 cookie 很重要）
        self._requests_session = requests.Session()
        os.makedirs(self.cfg.output_dir, exist_ok=True)
        # 豆瓣对 cookie 校验很严,首次访问必须给一个 bid,后续会话会自动维持
        import random as _r
        _bid = ''.join(_r.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=11))
        self._requests_session.cookies.set('bid', _bid, domain='.douban.com')
        LOGGER.info("injected bid cookie: %s", _bid)

        # 保守限速：豆瓣对翻页很敏感，把默认 1~3s 拉到 4~8s
        self.cfg.request_interval_min = max(self.cfg.request_interval_min, 6.0)
        self.cfg.request_interval_max = max(self.cfg.request_interval_max, 15.0)

    def load_extra_proxies(self, file_path: str) -> int:
        """从文件加载代理,追加到现有 pool。返回新加入的数量。"""
        new_proxies = load_proxies_from_file(file_path)
        if not new_proxies:
            return 0
        before = len(self.pool._proxies)
        # 去重
        existing = set(self.pool._proxies)
        for p in new_proxies:
            if p not in existing:
                self.pool._proxies.append(p)
                existing.add(p)
        added = len(self.pool._proxies) - before
        LOGGER.info("loaded %d proxies from %s (pool size=%d)", added, file_path, self.pool.size)
        return added

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
                    # 解压:gzip / br / deflate
                    import gzip as _gzip
                    try:
                        import brotli as _brotli
                        _HAS_BROTLI = True
                    except ImportError:
                        _brotli = None
                        _HAS_BROTLI = False
                    import zlib as _zlib
                    raw = resp.content
                    enc = (resp.headers.get("Content-Encoding") or "").lower()
                    if "br" in enc and _HAS_BROTLI:
                        try: raw = _brotli.decompress(raw)
                        except Exception as _e: LOGGER.warning("brotli fail: %s", _e)
                    elif "gzip" in enc or (raw[:2] == b"\x1f\x8b"):
                        try: raw = _gzip.decompress(raw)
                        except Exception as _e: LOGGER.warning("gzip fail: %s", _e)
                    elif "deflate" in enc:
                        try: raw = _zlib.decompress(raw, -_zlib.MAX_WBITS)
                        except Exception as _e: LOGGER.warning("deflate fail: %s", _e)
                    text = raw.decode("utf-8", errors="replace")

                    # 调试:打印长度 + 前 80 字符 + 保存最近响应
                    import os as _os
                    _dbg_dir = _os.path.join(self.cfg.output_dir, "_debug")
                    _os.makedirs(_dbg_dir, exist_ok=True)
                    _dbg_file = _os.path.join(_dbg_dir, "last_response.html")
                    try:
                        with open(_dbg_file, "w", encoding="utf-8") as _df:
                            _df.write(text)
                    except Exception:
                        pass
                    LOGGER.info("DBG status=200 url=%s enc=%s len=%d preview=%r",
                                url, enc or "(none)", len(text),
                                text[:80].replace(chr(10), " "))
                    return text

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
            # 第一页没 referer，后面一页的 referer 就是上一页
            referer = f"{self.cfg.top250_url}?start={(page - 1) * 25}&filter=" if page > 0 else self.cfg.top250_url
            html = self._fetch(url, referer=referer)
            if not html:
                LOGGER.warning("Top250 page=%s fetch failed", page)
                continue
            soup = BeautifulSoup(html, "lxml")
            count = 0
            for li in soup.select("ol.grid_view > div.item, ol.grid_view > li"):
                movie = parse_top250_item(li)
                if movie is None:
                    continue
                yield movie
                count += 1
            LOGGER.info("Top250 page=%s movies=%s", page, count)
            self._sleep()


    def crawl_by_genre(self) -> Iterable[Movie]:
        """按 config.genres 中定义的标签，从豆瓣 explore 页抓取电影卡片。
        每个标签最多翻 max_pages_per_tag 页，每页请求间隔 6~15s。
        """
        for genre in self.cfg.genres:
            count = 0
            for page in range(self.cfg.max_pages_per_tag):
                # tag 的 URL 形态：movie.douban.com/explore?genres=剧情&page=N
                url = f"{self.cfg.genre_base}?genres={quote(genre)}&page={page}"
                referer = self.cfg.genre_base if page == 0 else f"{self.cfg.genre_base}?genres={quote(genre)}&page={page - 1}"
                html = self._fetch(url, referer=referer)
                if not html:
                    LOGGER.warning("genre=%s page=%s fetch failed", genre, page)
                    break
                soup = BeautifulSoup(html, "lxml")
                items = soup.select("a.item.subject-item, div.subject-item, li.subject-item")
                if not items:
                    break
                for el in items:
                    movie = parse_explore_card(el, default_genre=genre)
                    if movie is None:
                        continue
                    yield movie
                    count += 1
                LOGGER.info("genre=%s page=%s movies=%s", genre, page, count)
                self._sleep()
            if count == 0:
                LOGGER.warning("genre=%s yielded 0 movies; check selector or rate limit", genre)

    def crawl_by_country(self) -> Iterable[Movie]:
        """按 config.countries 中定义的地区，从豆瓣 explore 页抓取电影卡片。"""
        for country in self.cfg.countries:
            count = 0
            for page in range(self.cfg.max_pages_per_tag):
                url = f"{self.cfg.genre_base}?countries={quote(country)}&page={page}"
                referer = self.cfg.genre_base if page == 0 else f"{self.cfg.genre_base}?countries={quote(country)}&page={page - 1}"
                html = self._fetch(url, referer=referer)
                if not html:
                    LOGGER.warning("country=%s page=%s fetch failed", country, page)
                    break
                soup = BeautifulSoup(html, "lxml")
                items = soup.select("a.item.subject-item, div.subject-item, li.subject-item")
                if not items:
                    break
                for el in items:
                    movie = parse_explore_card(el, default_country=country)
                    if movie is None:
                        continue
                    yield movie
                    count += 1
                LOGGER.info("country=%s page=%s movies=%s", country, page, count)
                self._sleep()
            if count == 0:
                LOGGER.warning("country=%s yielded 0 movies; check selector or rate limit", country)
    def enrich(self, movie: Movie) -> Movie:
        url = f"{self.cfg.movie_detail_base}{movie.douban_id}/"
        html = self._fetch(url, referer=self.cfg.top250_url)
        if html:
            try:
                parse_subject_page(html, movie)
                # 至少要有标题/导演才算"成功 enrich"
                if not (movie.title or movie.director):
                    self._record_bad_id(movie.douban_id, "no_fields_after_parse")
            except Exception as exc:
                LOGGER.debug("enrich fail %s: %s", movie.douban_id, exc)
                self._record_bad_id(movie.douban_id, f"parse_error:{exc!s}"[:80])
        else:
            self._record_bad_id(movie.douban_id, "fetch_failed")
        self._sleep()
        return movie

    def _record_bad_id(self, douban_id: str, reason: str) -> None:
        path = os.path.join(self.cfg.output_dir, self.cfg.bad_ids_file)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"{douban_id}\t{reason}\n")
        except Exception as e:
            LOGGER.debug("record bad_id fail: %s", e)

    def run(
        self,
        enrich_top_n: int = 250,
        out_name: str = "movies.jsonl",
        enrich_all: bool = False,
        sources: list[str] | None = None,
        resume: bool = True,
    ) -> int:
        """断点续爬版 run():
        - resume=True:启动时扫描已存在的 out_name,把 douban_id 加入 seen,跳过
        - 每条记录 enrich 失败写一行到 bad_ids.txt,方便后续补抓
        - 写入模式为追加('a'),崩了重跑不丢数据
        """
        if sources is None:
            sources = ["top250"]
        out_path = os.path.join(self.cfg.output_dir, out_name)
        os.makedirs(self.cfg.output_dir, exist_ok=True)

        # ====== 断点续爬:加载已有 douban_id ======
        seen: set[str] = set()
        total = 0
        if resume and os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8") as fin:
                for line in fin:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        did = obj.get("douban_id")
                        if did:
                            seen.add(str(did))
                            total += 1
                    except json.JSONDecodeError:
                        continue
            if seen:
                LOGGER.info("resume: loaded %d existing records from %s", len(seen), out_path)

        # ====== 按 sources 顺序串行抓取 ======
        iterables = []
        if "top250" in sources:
            iterables.append(self.crawl_top250())
        if "genres" in sources and self.cfg.genres:
            iterables.append(self.crawl_by_genre())
        if "countries" in sources and self.cfg.countries:
            iterables.append(self.crawl_by_country())

        # ====== 追加写入 ======
        with open(out_path, "a", encoding="utf-8") as fout:
            for it in iterables:
                for movie in it:
                    if movie.douban_id in seen:
                        continue
                    seen.add(movie.douban_id)
                    if enrich_all or total < enrich_top_n:
                        self.enrich(movie)
                    fout.write(json.dumps(to_dict(movie), ensure_ascii=False) + "\n")
                    fout.flush()
                    total += 1
                    if total % 10 == 0:
                        LOGGER.info("progress: total=%d/%d (last=%s)", total, self.cfg.target_count, movie.title)
                    if total >= self.cfg.target_count:
                        LOGGER.info("hit target_count=%s, stop early", self.cfg.target_count)
                        LOGGER.info("wrote %s records to %s", total, out_path)
                        return total

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

