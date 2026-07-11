"""代理池：从 config 传入的 proxies 列表中轮换选择。"""
from __future__ import annotations

import random
import threading

from .config import CrawlerConfig


class ProxyPool:
    def __init__(self, config: CrawlerConfig) -> None:
        self._lock = threading.Lock()
        self._proxies = list(config.proxies)

    def pick(self) -> dict | None:
        with self._lock:
            if not self._proxies:
                return None
            url = random.choice(self._proxies)
            return {"http": url, "https": url}

    @property
    def size(self) -> int:
        return len(self._proxies)