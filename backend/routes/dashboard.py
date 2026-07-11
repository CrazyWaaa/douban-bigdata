"""大屏总览。"""
from __future__ import annotations

from flask import Blueprint, jsonify

from ..services import movies as service

bp = Blueprint("dashboard", __name__, url_prefix="/api")


@bp.get("/dashboard/summary")
def summary():
    return jsonify(service.dashboard_summary())