"""健康检查。"""
from __future__ import annotations

from flask import Blueprint, jsonify
from sqlalchemy import text

from ..db import get_session

bp = Blueprint("health", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    s = get_session()
    try:
        s.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    finally:
        s.close()
    return jsonify(status="ok" if db_ok else "degraded", db=db_ok)