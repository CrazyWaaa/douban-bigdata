"""璞嗙摚鎶撳彇涓婚€昏緫锛歝url_cffi 妯℃嫙娴忚鍣?TLS 鎸囩汗 + requests 鍏滃簳 + 淇濆畧闄愰€熴€?
璞嗙摚璇嗗埆鐖櫕涓昏闈犱笁鏉★細
  1) requests / urllib3 鐨?JA3 鎸囩汗 鈮?鐪熷疄娴忚鍣?  2) 璇锋眰澶寸己 Sec-Fetch-* / Priority 绛夌幇浠ｅ瓧娈?  3) 1~3 绉掑氨缈婚〉锛岃繙瓒呯湡浜烘祻瑙堣妭濂?"""
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

# curl_cffi锛氱洿鎺ユā鎷?Chrome/Edge 绛夋祻瑙堝櫒 TLS 鎸囩汗锛屾槸瀵逛粯 429 鐨勬牳蹇冩墜娈?# 鏈畨瑁呭垯鑷姩閫€鍥?requests
try:
    from curl_cffi import requests as cffi_requests  # type: ignore
    _HAS_CFFI = True
except Exception:
    _HAS_CFFI = False


class DoubanCrawler:
    def __init__(self, config: CrawlerConfig | None = None) -> None:
        self.cfg = config or CONFIG
        self.pool = ProxyPool(self.cfg)
        # 杩涚▼绾?UA 鍥哄畾锛岄伩鍏嶆瘡娆¤姹傞兘鎹?        self.ua = pick_user_agent()
        # 涓€涓?requests Session锛岀敤鏉ヤ繚鎸?cookie锛堢涓€娆¤闂悗鐨?cookie 寰堥噸瑕侊級
        self._requests_session = requests.Session()
        os.makedirs(self.cfg.output_dir, exist_ok=True)

        # 淇濆畧闄愰€燂細璞嗙摚瀵圭炕椤靛緢鏁忔劅锛屾妸榛樿 1~3s 鎷夊埌 4~8s
        self.cfg.request_interval_min = max(self.cfg.request_interval_min, 6.0)
        self.cfg.request_interval_max = max(self.cfg.request_interval_max, 15.0)

    def _headers(self, referer: str | None = None) -> dict:
        """杩斿洖鎺ヨ繎鐪熷疄娴忚鍣ㄧ殑瀹屾暣璇锋眰澶达紙UA 鍏ㄧ▼鍥哄畾锛夈€?""
        return common_headers(referer=referer)

    def _sleep(self, base: float | None = None, jitter: float = 1.5) -> None:
        """鍦ㄤ袱娆¤姹備箣闂?sleep锛涘け璐ユ椂浼氫紶鍏ユ洿澶х殑 base 鍋氶€€閬裤€?""
        if base is None:
            base = random.uniform(self.cfg.request_interval_min, self.cfg.request_interval_max)
        secs = base + random.uniform(0, jitter)
        time.sleep(secs)

    def _fetch(self, url: str, referer: str | None = None) -> str | None:
        """
        鍗曟鎶撳彇锛?          - curl_cffi 浼樺厛锛堟ā鎷熸祻瑙堝櫒 TLS锛岃繃 429 涓绘墜娈碉級
          - 澶辫触 / 鏈畨瑁呭垯閫€鍥?requests
          - 閬囧埌 429/403 鏃舵媺闀块€€閬匡紝5 娆￠噸璇曢噷鎹?UA 涓€娆?        """
        headers = self._headers(referer)
        proxy = self.pool.pick()

        for attempt in range(self.cfg.max_retries):
            try:
                if _HAS_CFFI:
                    kwargs = dict(
                        headers=headers,
                        timeout=30,
                        impersonate="chrome",   # 鍏抽敭锛氭ā鎷?Chrome 鐨?TLS 鎸囩汗
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

                # 429 / 403 / 5xx锛氶€€閬垮悗閲嶈瘯
                if resp.status_code in (429, 403) or resp.status_code >= 500:
                    # 429 鑷冲皯绛?10s 璧锋锛屾寚鏁伴€€閬?                    wait = max(10.0, self.cfg.backoff_base ** attempt * 2)
                    LOGGER.warning(
                        "retry %s for %s after %.1fs (status=%s)",
                        attempt + 1, url, wait, resp.status_code,
                    )
                    time.sleep(wait)
                    if attempt == self.cfg.max_retries // 2:
                        # 涓€旀崲涓€娆?UA锛岄伩鍏嶈鍚屼竴鎸囩汗杩炵画闄愬埗
                        self.ua = reset_user_agent()
                        headers = self._headers(referer)
                    continue

                # 鍏朵粬鐘舵€佺爜锛堝 418銆?04锛夛細鐩存帴鏀惧純
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
            # 绗竴椤垫病 referer锛屽悗闈竴椤电殑 referer 灏辨槸涓婁竴椤?            referer = f"{self.cfg.top250_url}?start={(page - 1) * 25}&filter=" if page > 0 else self.cfg.top250_url
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

