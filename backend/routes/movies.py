"""影片查询接口。"""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request

from auth import require_api_key
from services import movies as service

bp = Blueprint("movies", __name__, url_prefix="/api")


@require_api_key
@bp.get("/movies/count_by_genre")
def count_by_genre():
    return jsonify(data=service.count_by_genre())


@require_api_key
@bp.get("/movies/count_by_country")
def count_by_country():
    return jsonify(data=service.count_by_country())


@require_api_key
@bp.get("/movies/count_by_year")
def count_by_year():
    return jsonify(data=service.count_by_year())


@require_api_key
@bp.get("/movies/top_rated")
def top_rated():
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        limit = 50
    limit = max(1, min(limit, 200))
    return jsonify(data=service.top_rated(limit))


@require_api_key
@bp.get("/movies/<douban_id>")
def detail(douban_id: str):
    movie = service.detail(douban_id)
    if movie is None:
        abort(404, description="movie not found")
    return jsonify(data=movie)


# ====== 新增:分布/榜单/分页/搜索/相关/导航 ======
@require_api_key
@bp.get("/movies/count_by_avg")
def count_by_avg():
    try:
        dim = request.args.get("dim", "genre")
        limit = int(request.args.get("limit", 10))
    except ValueError:
        dim, limit = "genre", 10
    if dim not in ("genre", "country", "year"):
        dim = "genre"
    limit = max(1, min(limit, 50))
    return jsonify(data=service.count_by_avg(limit=limit, dim=dim))


@require_api_key
@bp.get("/movies/rating_distribution")
def rating_distribution():
    return jsonify(data=service.rating_distribution())


@require_api_key
@bp.get("/movies/runtime_distribution")
def runtime_distribution():
    return jsonify(data=service.runtime_distribution())


@require_api_key
@bp.get("/movies/count_by_director")
def count_by_director():
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        limit = 10
    return jsonify(data=service.count_by_dimension("director", limit=max(1, min(limit, 50))))


@require_api_key
@bp.get("/movies/count_by_language")
def count_by_language():
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        limit = 10
    return jsonify(data=service.count_by_dimension("language", limit=max(1, min(limit, 50))))


@require_api_key
@bp.get("/movies/count_by_decade")
def count_by_decade():
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20
    return jsonify(data=service.count_by_dimension("decade", limit=max(1, min(limit, 50))))


@require_api_key
@bp.get("/movies/paged")
def paged():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 20))
    except ValueError:
        page, size = 1, 20
    sort = request.args.get("sort", "rating")
    order = request.args.get("order", "desc")
    genre = request.args.get("genre") or None
    country = request.args.get("country") or None
    try:
        year_from = int(request.args["year_from"]) if request.args.get("year_from") else None
        year_to = int(request.args["year_to"]) if request.args.get("year_to") else None
    except (ValueError, KeyError):
        year_from, year_to = None, None
    return jsonify(data=service.paged_movies(
        page=page, size=size, sort=sort, order=order,
        genre=genre, country=country,
        year_from=year_from, year_to=year_to,
    ))


@require_api_key
@bp.get("/movies/search")
def search():
    q = request.args.get("q", "")
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20
    return jsonify(data=service.search_movies(q, limit))


@require_api_key
@bp.get("/movies/<douban_id>/related")
def related(douban_id: str):
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        limit = 10
    return jsonify(data=service.related_movies(douban_id, max(1, min(limit, 20))))


@require_api_key
@bp.get("/movies/<douban_id>/neighbors")
def neighbors(douban_id: str):
    return jsonify(data=service.neighbor_movies(douban_id))

