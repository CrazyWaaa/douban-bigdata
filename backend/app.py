"""Flask 后端入口：注册蓝图、CORS、错误处理。"""
from __future__ import annotations

from flask import Flask, jsonify
from flask_cors import CORS

from .routes.dashboard import bp as dashboard_bp
from .routes.health import bp as health_bp
from .routes.movies import bp as movies_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(health_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(movies_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="not_found", message=str(e.description)), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="server_error", message=str(e)), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)