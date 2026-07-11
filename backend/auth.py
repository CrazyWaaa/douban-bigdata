"""API 鉴权：从环境变量 DOUBAN_API_KEY 读取共享密钥，
未配置则跳过鉴权（开发友好）；配了就强制要求 X-API-Key 头。"""
from __future__ import annotations

import os
from functools import wraps
from typing import Callable

from flask import jsonify, request


def get_api_key() -> str:
    return os.getenv("DOUBAN_API_KEY", "").strip()


def is_auth_enabled() -> bool:
    return bool(get_api_key())


def require_api_key(fn: Callable) -> Callable:
    """装饰器：保护需要鉴权的接口。/api/health 不挂此装饰器。

    - 未配置 DOUBAN_API_KEY：直接放行（开发模式）
    - 已配置：要求请求头 X-API-Key 与环境变量一致
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_auth_enabled():
            return fn(*args, **kwargs)
        provided = request.headers.get("X-API-Key", "").strip()
        if not provided or provided != get_api_key():
            return jsonify(error="unauthorized", message="missing or invalid X-API-Key"), 401
        return fn(*args, **kwargs)
    return wrapper