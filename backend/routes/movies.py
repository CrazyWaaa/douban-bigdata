"""影片查询接口。"""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request

from ..services import movies as service

bp = Blueprint("movies", __name__, url_prefix="/api")


@bp.get("/movies/count_by_genre")
def count_by_genre():
    return jsonify(data=service.count_by_genre())


@bp.get("/movies/count_by_country")
def count_by_country():
    return jsonify(data=service.count_by_country())


@bp.get("/movies/count_by_year")
def count_by_year():
    return jsonify(data=service.count_by_year())


@bp.get("/movies/top_rated")
def top_rated():
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        limit = 50
    limit = max(1, min(limit, 200))
    return jsonify(data=service.top_rated(limit))


@bp.get("/movies/<douban_id>")
def detail(douban_id: str):
    movie = service.detail(douban_id)
    if movie is None:
        abort(404, description="movie not found")
    return jsonify(data=movie)