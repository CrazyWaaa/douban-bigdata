"""业务层：聚合与查询，统一返回字典而非 ORM 对象，便于 JSON 序列化。"""
from __future__ import annotations

from typing import Any
from sqlalchemy import func, select

from ..db import get_session
from ..models import AggCountry, AggGenre, AggYear, Movie


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
        rows = s.execute(
            select(Movie).order_by(Movie.rating.desc().nulls_last(), Movie.rating_count.desc().nulls_last()).limit(limit)
        ).scalars().all()
        return [_serialize_movie(m, rank=i + 1) for i, m in enumerate(rows)]
    finally:
        s.close()


def _serialize_movie(m: Movie, rank: int | None = None) -> dict:
    return {
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


def detail(douban_id: str) -> dict | None:
    s = get_session()
    try:
        m = s.execute(select(Movie).where(Movie.douban_id == douban_id)).scalar_one_or_none()
        if m is None:
            return None
        return _serialize_movie(m)
    finally:
        s.close()