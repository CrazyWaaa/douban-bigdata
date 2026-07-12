# -*- coding: utf-8 -*-
"""豆瓣图片反代：解决前端 dev / 后端无 nginx 时的防盗链限制。

请求：GET /img-proxy?url=<encoded https url>
响应：原图二进制流，带 7d 缓存。
"""
from __future__ import annotations

import logging
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from flask import Blueprint, Response, abort, request

bp = Blueprint("img_proxy", __name__)

ALLOWED_HOSTS = ("doubanio.com", "douban.com", "img1.doubanio.com", "img2.doubanio.com", "img3.doubanio.com", "img9.doubanio.com")
TIMEOUT = 15
MAX_BYTES = 10 * 1024 * 1024  # 10MB 硬上限，防止恶意大图
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36"


@bp.get("/img-proxy")
def img_proxy():
    url = request.args.get("url", "").strip()
    if not url or not re.match(r"^https?://", url):
        abort(400, description="url must be http(s)")
    host = (urlparse(url).hostname or "").lower()
    if not any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS):
        abort(400, description=f"host not allowed: {host}")
    try:
        req = Request(url, headers={
            "User-Agent": UA,
            "Referer": "https://movie.douban.com/",
            "Accept": "image/avif,image/webp,image/png,image/jpeg,image/*;q=0.8,*/*;q=0.5",
        })
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                abort(413, description="image too large")
            ct = resp.headers.get("Content-Type", "image/jpeg")
    except HTTPError as e:
        logging.warning("img-proxy upstream %s: %s", url, e)
        abort(e.code, description=f"upstream {e.code}")
    except URLError as e:
        logging.warning("img-proxy fetch %s: %s", url, e)
        abort(502, description=f"upstream unreachable: {e.reason}")
    return Response(data, mimetype=ct, headers={
        "Cache-Control": "public, max-age=604800",
        "X-Img-Proxy": "flask",
    })