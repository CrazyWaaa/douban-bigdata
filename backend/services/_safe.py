# -*- coding: utf-8 -*-
"""对 services/movies.py 的小补丁:
- _try_parse_json 容错:遇到 None 或非字符串直接返回 None
- _serialize_movie:对扩展字段即使非空也加 try 包,任何字段异常只丢弃该字段,不影响整行
"""
from __future__ import annotations
import json


def safe_json(value):
    if value is None or value == "":
        return None
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, (str, bytes, bytearray)):
        return None
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return None


def safe_text(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            return None
    return str(value)


def merge_extras(m):
    """把 Movie 模型上扩展字段都安全序列化,单字段错误不抛"""
    extras = {}
    fields = [
        ("detail_url", str),
        ("languages", str),
        ("release_date", str),
        ("runtime", str),
        ("runtime_minutes", int),
        ("quote", str),
        ("better_than", str),
        ("also_know_as", str),
        ("imdb_id", str),
        ("official_sites", str),
        ("comment_short_count", int),
        ("comment_review_count", int),
        ("discussion_count", int),
        ("rating_stars", dict),   # dict/list 期望,字符串会被尝试解析
        ("related_pics", list),   # 同上
    ]
    for name, typ in fields:
        v = getattr(m, name, None)
        if v is None:
            continue
        try:
            if typ in (dict, list):
                parsed = safe_json(v)
                if parsed is None:
                    continue
                extras[name] = parsed
            else:
                extras[name] = typ(v) if not isinstance(v, typ) else v
        except (TypeError, ValueError):
            continue
    return extras


def split_related_pics(value):
    """兼容旧的字符串,空格分隔/JSON 都解析"""
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        if s.startswith("["):
            try:
                arr = json.loads(s)
                if isinstance(arr, list):
                    return arr
            except (TypeError, ValueError):
                pass
        return [t for t in s.replace(",", " ").split() if t]
    return None