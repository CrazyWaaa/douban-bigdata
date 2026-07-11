"""后端配置：集中读取环境变量，提供给 db.py 与 services。"""
from __future__ import annotations

import os


class Settings:
    @property
    def mysql_user(self) -> str:
        return os.getenv("DOUBAN_DB_USER", "douban")

    @property
    def mysql_password(self) -> str:
        return os.getenv("DOUBAN_DB_PASSWORD", "douban_pwd")

    @property
    def mysql_host(self) -> str:
        return os.getenv("DOUBAN_DB_HOST", "127.0.0.1")

    @property
    def mysql_port(self) -> int:
        return int(os.getenv("DOUBAN_DB_PORT", "3306"))

    @property
    def mysql_db(self) -> str:
        return os.getenv("DOUBAN_DB_NAME", "douban")

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}?charset=utf8mb4"
        )


SETTINGS = Settings()