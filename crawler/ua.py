"""UA 与浏览器指纹：提供稳定、真实的桌面端 UA，避免每次请求轮换。

豆瓣对"UA 反复变化 + requests 默认 TLS 指纹"非常敏感，429 基本来自这两条。
"""
from __future__ import annotations

import random


# 一组真实的桌面端浏览器 UA；启动后随机挑一个 **全程固定** 使用
_BROWSER_UAS = (
    # Chrome / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    # Chrome / macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    # Firefox / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    # Safari / macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    # Edge / Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
)


# 进程级 UA；在爬虫实例的生命周期内固定，模拟"同一个人用同一个浏览器"
_PICKED: str | None = None


def pick_user_agent() -> str:
    """返回一个稳定的桌面端浏览器 UA（进程内不会变）。"""
    global _PICKED
    if _PICKED is None:
        _PICKED = random.choice(_BROWSER_UAS)
    return _PICKED


def reset_user_agent() -> str:
    """强制换一个 UA（当检测到长时间 429 时调用）。"""
    global _PICKED
    _PICKED = random.choice(_BROWSER_UAS)
    return _PICKED


def common_headers(referer: str | None = None) -> dict:
    """给一个接近真实浏览器的完整请求头。

    关键点：
    - 不用 `Cache-Control: no-cache`（真实浏览器也不会每次都发）
    - 补齐 `Sec-Fetch-*` / `Priority` 等现代浏览器字段
    - UA 固定；`Accept*` 与真实浏览器一致
    """
    ua = pick_user_agent()
    h = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": ("same-origin" if referer else "none"),
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
    }
    if referer:
        h["Referer"] = referer
    return h