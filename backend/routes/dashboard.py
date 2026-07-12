"""大屏总览。"""
from __future__ import annotations

from flask import Blueprint, jsonify

from auth import require_api_key
from services import movies as service

bp = Blueprint("dashboard", __name__, url_prefix="/api")


@require_api_key
@bp.get("/dashboard/summary")
def summary():
    return jsonify(service.dashboard_summary())

@require_api_key
@bp.get("/dashboard/summary_extended")
def summary_extended():
    return jsonify(service.summary_extended())
