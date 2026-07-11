"""Flask 后端入口：注册蓝图、CORS、鉴权、限流、错误处理。"""
from __future__ import annotations

import logging

from flask import Flask, jsonify
from flask_cors import CORS

from .auth import get_api_key, is_auth_enabled

# 限流可选：flask-limiter 装不上时跳过（不影响鉴权主功能）
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    _HAS_LIMITER = True
except ImportError:
    _HAS_LIMITER = False
from .routes.dashboard import bp as dashboard_bp
from .routes.health import bp as health_bp
from .routes.movies import bp as movies_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 限流：默认 60 次/分钟/IP；可被 DOUBAN_RATE_LIMIT 环境变量覆盖
    # 若 flask-limiter 未安装则跳过限流（开发/受限环境兼容）
    import os as _os
    if _HAS_LIMITER:
        rate = _os.getenv("DOUBAN_RATE_LIMIT", "60/minute")
        Limiter(get_remote_address, app=app, default_limits=[rate], storage_uri="memory://")
    else:
        logging.warning("flask-limiter not installed; rate limiting disabled")

    app.register_blueprint(health_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(movies_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="not_found", message=str(e.description)), 404

    @app.errorhandler(429)
    def too_many(e):
        return jsonify(error="rate_limited", message=str(e.description)), 429

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="server_error", message=str(e)), 500

    if is_auth_enabled():
        logging.info("API key auth ENABLED (key length=%d)", len(get_api_key()))
    else:
        logging.info("API key auth disabled (set DOUBAN_API_KEY to enable)")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)