"""UA 轮换：从 fake-useragent 库随机抽取，并维护兜底池。"""
from __future__ import annotations

import random

try:
    from fake_useragent import UserAgent  # type: ignore
    _UA = UserAgent()
except Exception:
    _UA = None

_FALLBACK = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:124.0) Gecko/20100101 Firefox/124.0",
)


def pick_user_agent() -> str:
    if _UA is not None:
        try:
            return _UA.random
        except Exception:
            pass
    return random.choice(_FALLBACK)