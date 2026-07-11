"""Flask 后端入口：注册蓝图、提供统一 JSON 响应。"""
from flask import Flask, jsonify
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    print("[backend] 占位实现：待注册业务接口")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)