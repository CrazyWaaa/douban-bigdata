"""业务层：聚合与查询，统一返回字典而非 ORM 对象，便于 JSON 序列化。"""
from __future__ import annotations

import json
from typing import Any
from sqlalchemy import func, select, case, or_, text

from db import get_session
from models import AggCountry, AggGenre, AggYear, Movie

# ============ 通用工具 ============
# CSV/分隔字段拆行:用于把 "A / B / C" 拆成多行,在 SQL 层做聚合
_DELIMITED_RE = None
def _split_delimited_sql(col: str, sep: str = "/") -> str:
    """生成可在 SELECT 列表里展开多值的 SQL 片段(JOIN 一个 1..N 序号辅助表)。"""
    return (
        "TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(" + col + ", '" + sep + "', n.n), '" + sep + "', -1))"
    )


def _split_terms(value: str | None, sep: str = "/") -> list[str]:
    if not value:
        return []
    return [t.strip() for t in str(value).split(sep) if t and t.strip()]


def _try_parse_json(value):
    """rating_stars / related_pics 等字段存的是 JSON 字符串，前端需要结构。"""
    if value is None or value == "":
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return value


def dashboard_summary() -> dict[str, Any]:
    s = get_session()
    try:
        total = s.execute(select(func.count(Movie.id))).scalar() or 0
        avg = s.execute(select(func.avg(Movie.rating))).scalar()
        genres = s.execute(select(func.count(func.distinct(Movie.genre)))).scalar() or 0
        countries = s.execute(select(func.count(func.distinct(Movie.country)))).scalar() or 0
        years = s.execute(select(func.count(func.distinct(Movie.year)))).scalar() or 0
        return {
            "total": int(total),
            "avg_rating": float(avg) if avg is not None else None,
            "distinct_genre": int(genres),
            "distinct_country": int(countries),
            "distinct_year": int(years),
        }
    finally:
        s.close()


def _to_float(value) -> float | None:
    if value is None:
        return None
    return float(value)


def _serialize_agg_genre(rows) -> list[dict]:
    return [
        {"name": r.genre, "count": int(r.movie_count), "avg_rating": _to_float(r.avg_rating)}
        for r in rows if r.genre
    ]


def _serialize_agg_country(rows) -> list[dict]:
    return [
        {"name": r.country, "count": int(r.movie_count), "avg_rating": _to_float(r.avg_rating)}
        for r in rows if r.country
    ]


def _serialize_agg_year(rows) -> list[dict]:
    return [
        {"year": int(r.year), "count": int(r.movie_count), "avg_rating": _to_float(r.avg_rating)}
        for r in rows
    ]


def count_by_genre() -> list[dict]:
    s = get_session()
    try:
        rows = s.execute(select(AggGenre).order_by(AggGenre.movie_count.desc())).scalars().all()
        return _serialize_agg_genre(rows)
    finally:
        s.close()


def count_by_country() -> list[dict]:
    s = get_session()
    try:
        rows = s.execute(select(AggCountry).order_by(AggCountry.movie_count.desc())).scalars().all()
        return _serialize_agg_country(rows)
    finally:
        s.close()


def count_by_year() -> list[dict]:
    s = get_session()
    try:
        rows = s.execute(select(AggYear).order_by(AggYear.year.asc())).scalars().all()
        return _serialize_agg_year(rows)
    finally:
        s.close()


def top_rated(limit: int = 50) -> list[dict]:
    s = get_session()
    try:
        rating_null = Movie.rating.is_(None)
        count_null = Movie.rating_count.is_(None)
        rows = s.execute(
            select(Movie).order_by(
                rating_null.asc(), Movie.rating.desc(),
                count_null.asc(), Movie.rating_count.desc(),
            ).limit(limit)
        ).scalars().all()
        return [_serialize_movie(m, rank=i + 1) for i, m in enumerate(rows)]
    finally:
        s.close()


def _serialize_movie(m: Movie, rank: int | None = None) -> dict:
    data = {
        "rank": rank,
        "douban_id": m.douban_id,
        "title": m.title,
        "director": m.director,
        "actors": m.actors,
        "genre": m.genre,
        "country": m.country,
        "year": int(m.year) if m.year is not None else None,
        "rating": _to_float(m.rating),
        "rating_count": int(m.rating_count) if m.rating_count is not None else None,
        "summary": m.summary,
        "poster_url": m.poster_url,
    }
    # 扩展字段：只在有值时返回（避免列表接口被大量空字段稀释）
    extras = {
        "detail_url": getattr(m, "detail_url", None),
        "languages": getattr(m, "languages", None),
        "release_date": getattr(m, "release_date", None),
        "runtime": getattr(m, "runtime", None),
        "runtime_minutes": int(m.runtime_minutes) if getattr(m, "runtime_minutes", None) is not None else None,
        "quote": getattr(m, "quote", None),
        "better_than": getattr(m, "better_than", None),
        "also_know_as": getattr(m, "also_know_as", None),
        "imdb_id": getattr(m, "imdb_id", None),
        "official_sites": getattr(m, "official_sites", None),
        "comment_short_count": int(m.comment_short_count) if getattr(m, "comment_short_count", None) is not None else None,
        "comment_review_count": int(m.comment_review_count) if getattr(m, "comment_review_count", None) is not None else None,
        "discussion_count": int(m.discussion_count) if getattr(m, "discussion_count", None) is not None else None,
        "rating_stars": _try_parse_json(getattr(m, "rating_stars", None)),
        "related_pics": _try_parse_json(getattr(m, "related_pics", None)),
    }
    for k, v in extras.items():
        if v not in (None, "", "null", "[]", "{}"):
            data[k] = v
    return data


def detail(douban_id: str) -> dict | None:
    s = get_session()
    try:
        m = s.execute(select(Movie).where(Movie.douban_id == douban_id)).scalar_one_or_none()
        if m is None:
            return None
        return _serialize_movie(m)
    finally:
        s.close()


# ============ 新增业务函数 ============
def summary_extended() -> dict[str, Any]:
    """聚合概览:总数/均分/最高分/单部最高评分人数/平均评分人数/维度数。"""
    s = get_session()
    try:
        total = s.execute(select(func.count(Movie.id))).scalar() or 0
        avg = s.execute(select(func.avg(Movie.rating))).scalar()
        max_rating = s.execute(select(func.max(Movie.rating))).scalar()
        avg_count = s.execute(select(func.avg(Movie.rating_count))).scalar()
        top_rating_row = s.execute(
            select(Movie.title, Movie.rating_count)
            .where(Movie.rating_count.isnot(None))
            .order_by(Movie.rating_count.desc())
            .limit(1)
        ).first()
        distinct_year = s.execute(select(func.count(func.distinct(Movie.year)))).scalar() or 0
        distinct_genre = s.execute(select(func.count(func.distinct(Movie.genre)))).scalar() or 0
        distinct_country = s.execute(select(func.count(func.distinct(Movie.country)))).scalar() or 0
        return {
            "total": int(total),
            "avg_rating": float(avg) if avg is not None else None,
            "max_rating": float(max_rating) if max_rating is not None else None,
            "avg_rating_count": int(avg_count) if avg_count is not None else None,
            "top_rating_count_title": top_rating_row[0] if top_rating_row else None,
            "top_rating_count": int(top_rating_row[1]) if top_rating_row and top_rating_row[1] is not None else None,
            "distinct_year": int(distinct_year),
            "distinct_genre": int(distinct_genre),
            "distinct_country": int(distinct_country),
        }
    finally:
        s.close()


def count_by_avg(limit: int = 10, dim: str = "genre") -> list[dict]:
    """双轴数据:每个维度返回 top N + avg_rating,用于柱+折线复合图。
    dim: 'genre' | 'country' | 'year'
    """
    s = get_session()
    try:
        model = {"genre": AggGenre, "country": AggCountry, "year": AggYear}[dim]
        col_name = {"genre": "genre", "country": "country", "year": "year"}[dim]
        rows = (
            s.execute(select(model).order_by(model.movie_count.desc()).limit(limit))
            .scalars()
            .all()
        )
        out = []
        for r in rows:
            item = {
                "name": getattr(r, col_name),
                "count": int(r.movie_count) if r.movie_count is not None else 0,
                "avg_rating": float(r.avg_rating) if r.avg_rating is not None else None,
            }
            if dim == "year":
                item["name"] = int(item["name"]) if item["name"] is not None else None
            out.append(item)
        return out
    finally:
        s.close()


def rating_distribution() -> list[dict]:
    """评分分桶直方图: <7 / 7-8 / 8-9 / 9+ 共 4 档。"""
    s = get_session()
    try:
        buckets = [
            ("6以下", None, 7.0),
            ("7-8", 7.0, 8.0),
            ("8-9", 8.0, 9.0),
            ("9以上", 9.0, None),
        ]
        result = []
        for label, lo, hi in buckets:
            q = select(func.count(Movie.id))
            if lo is not None:
                q = q.where(Movie.rating >= lo)
            if hi is not None:
                q = q.where(Movie.rating < hi)
            cnt = s.execute(q).scalar() or 0
            result.append({"bucket": label, "count": int(cnt)})
        return result
    finally:
        s.close()


def runtime_distribution() -> list[dict]:
    """片长分桶:<90 / 90-120 / 120-150 / 150+ 分钟。runtime_minutes 为空的忽略。"""
    s = get_session()
    try:
        buckets = [
            ("<90", None, 90),
            ("90-120", 90, 120),
            ("120-150", 120, 150),
            ("150+", 150, None),
        ]
        result = []
        for label, lo, hi in buckets:
            q = select(func.count(Movie.id)).where(Movie.runtime_minutes.isnot(None))
            if lo is not None:
                q = q.where(Movie.runtime_minutes >= lo)
            if hi is not None:
                q = q.where(Movie.runtime_minutes < hi)
            cnt = s.execute(q).scalar() or 0
            result.append({"bucket": label, "count": int(cnt)})
        return result
    finally:
        s.close()


def count_by_dimension(dimension: str, limit: int = 20) -> list[dict]:
    """通用按字段聚合:dimension ∈ director | language | decade。
    director / language 用 SQL 拆分(因 '/' 分隔),
    decade 用 year // 10 * 10。
    """
    s = get_session()
    try:
        if dimension == "director":
            return _aggregate_terms_sql(s, "director", limit)
        if dimension == "language":
            return _aggregate_terms_sql(s, "languages", limit, sep="/")
        if dimension == "decade":
            return _aggregate_decade(s, limit)
        return []
    finally:
        s.close()


def _aggregate_terms_sql(s, col: str, limit: int, sep: str = "/") -> list[dict]:
    """在 SQL 里拆分并聚合 director / languages,避免把所有行拉到 Python。
    使用 CTE + 序号表(numbers),先把 movie 行按分隔符拆开,再聚合。
    """
    split_fn = _split_delimited_sql(col, sep=sep)
    numbers_sql = " UNION ALL ".join([f"SELECT {i} AS n" for i in range(1, 6)])
    # 关键:拆分行号通过 numbers CTE 提供;子查询里不能再用 n(避免和外层 FROM JOIN 冲突)
    sql = f"""
        WITH numbers AS ({numbers_sql})
        SELECT term, COUNT(*) AS cnt, ROUND(AVG(rating), 2) AS avg_rating
        FROM (
            SELECT m.rating,
                   TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(m.{col}, '{sep}', k.n), '{sep}', -1)) AS term
            FROM movie m
            JOIN numbers k
              ON CHAR_LENGTH(m.{col}) - CHAR_LENGTH(REPLACE(m.{col}, '{sep}', '')) >= k.n - 1
            WHERE m.{col} IS NOT NULL AND m.{col} <> ''
        ) t
        WHERE t.term IS NOT NULL AND TRIM(t.term) <> ''
        GROUP BY t.term
        ORDER BY cnt DESC
        LIMIT {int(limit)}
    """
    rows = s.execute(text(sql)).all()
    return [
        {"name": r[0], "count": int(r[1]), "avg_rating": float(r[2]) if r[2] is not None else None}
        for r in rows
    ]


def _aggregate_decade(s, limit: int = 20) -> list[dict]:
    sql = """
        SELECT (FLOOR(year / 10) * 10) AS decade,
               COUNT(*) AS cnt,
               ROUND(AVG(rating), 2) AS avg_rating
        FROM movie
        WHERE year IS NOT NULL AND year >= 1900 AND rating IS NOT NULL
        GROUP BY decade
        ORDER BY decade ASC
        LIMIT :limit
    """
    rows = s.execute(text(sql), {"limit": int(limit)}).all()
    return [
        {"name": int(r[0]), "count": int(r[1]), "avg_rating": float(r[2]) if r[2] is not None else None}
        for r in rows
    ]


def paged_movies(
    page: int = 1,
    size: int = 20,
    sort: str = "rating",
    order: str = "desc",
    genre: str | None = None,
    country: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> dict:
    """通用列表查询:返回 {total, page, size, items[]}。"""
    s = get_session()
    try:
        # 允许的 sort/order 白名单,避免任意字段排序导致索引失效
        sort_map = {
            "rating": Movie.rating,
            "rating_count": Movie.rating_count,
            "year": Movie.year,
            "title": Movie.title,
            "id": Movie.id,
        }
        sort_col = sort_map.get(sort, Movie.rating)
        order_col = sort_col.asc() if order.lower() == "asc" else sort_col.desc()
        # NULL 处理:评分/评价数为 NULL 的排到末尾；其他字段用默认行为。
        is_asc = order.lower() == "asc"
        if sort in ("rating", "rating_count"):
            order_clauses = [sort_col.is_(None), sort_col.asc() if is_asc else sort_col.desc()]
        else:
            order_clauses = [sort_col.asc() if is_asc else sort_col.desc()]
        q = select(Movie)
        cnt_q = select(func.count(Movie.id))
        if genre:
            q = q.where(Movie.genre.like(f"%{genre}%"))
            cnt_q = cnt_q.where(Movie.genre.like(f"%{genre}%"))
        if country:
            q = q.where(Movie.country.like(f"%{country}%"))
            cnt_q = cnt_q.where(Movie.country.like(f"%{country}%"))
        if year_from is not None:
            q = q.where(Movie.year >= year_from)
            cnt_q = cnt_q.where(Movie.year >= year_from)
        if year_to is not None:
            q = q.where(Movie.year <= year_to)
            cnt_q = cnt_q.where(Movie.year <= year_to)

        total = int(s.execute(cnt_q).scalar() or 0)
        size = max(1, min(size, 100))
        page = max(1, page)
        rows = s.execute(q.order_by(*order_clauses).limit(size).offset((page - 1) * size)).scalars().all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [_serialize_movie(m) for m in rows],
        }
    finally:
        s.close()


def search_movies(q: str, limit: int = 20) -> list[dict]:
    """片名/导演/演员 模糊搜索。空字符串返回空。"""
    q = (q or "").strip()
    if not q:
        return []
    s = get_session()
    try:
        like = f"%{q}%"
        rows = s.execute(
            select(Movie)
            .where(
                or_(
                    Movie.title.like(like),
                    Movie.director.like(like),
                    Movie.actors.like(like),
                )
            )
            .order_by(Movie.rating.is_(None), Movie.rating.desc())
            .limit(min(max(limit, 1), 100))
        ).scalars().all()
        return [_serialize_movie(m) for m in rows]
    finally:
        s.close()


def related_movies(douban_id: str, limit: int = 10) -> list[dict]:
    """相关推荐:同类型 Top,排除自己。"""
    s = get_session()
    try:
        self_movie = s.execute(select(Movie).where(Movie.douban_id == douban_id)).scalar_one_or_none()
        if self_movie is None or not self_movie.genre:
            return []
        # 取第一个 genre 作为匹配关键字
        first_genre = _split_terms(self_movie.genre)[0]
        rows = s.execute(
            select(Movie)
            .where(Movie.douban_id != douban_id)
            .where(Movie.genre.like(f"%{first_genre}%"))
            .order_by(Movie.rating.is_(None), Movie.rating.desc())
            .limit(limit)
        ).scalars().all()
        return [_serialize_movie(m) for m in rows]
    finally:
        s.close()


def neighbor_movies(douban_id: str) -> dict:
    """同榜单上下部:返回上一部 / 下一部 douban_id + 标题。"""
    s = get_session()
    try:
        rows = s.execute(
            select(Movie.douban_id, Movie.title, Movie.rating)
            .order_by(Movie.rating.is_(None), Movie.rating.desc(), Movie.rating_count.is_(None), Movie.rating_count.desc())
        ).all()
        ids = [(r[0], r[1]) for r in rows]
        for i, (did, title) in enumerate(ids):
            if did == douban_id:
                return {
                    "prev": {"douban_id": ids[i - 1][0], "title": ids[i - 1][1]} if i > 0 else None,
                    "next": {"douban_id": ids[i + 1][0], "title": ids[i + 1][1]} if i + 1 < len(ids) else None,
                }
        return {"prev": None, "next": None}
    finally:
        s.close()

