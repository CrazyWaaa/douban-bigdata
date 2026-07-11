"""影片查询接口。"""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request

from ..auth import require_api_key
from ..services import movies as service

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