"""ETL 任务环境配置：HDFS / MySQL JDBC 连接串。"""
from __future__ import annotations

import os


class EtlSettings:
    @property
    def hdfs_input_dir(self) -> str:
        return os.getenv("ETL_HDFS_INPUT", "hdfs://localhost:9000/raw/douban/movies")

    @property
    def jdbc_url(self) -> str:
        host = os.getenv("ETL_DB_HOST", "127.0.0.1")
        port = os.getenv("ETL_DB_PORT", "3306")
        db = os.getenv("ETL_DB_NAME", "douban")
        return f"jdbc:mysql://{host}:{port}/{db}?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=UTC"

    @property
    def jdbc_user(self) -> str:
        return os.getenv("ETL_DB_USER", "douban")

    @property
    def jdbc_password(self) -> str:
        return os.getenv("ETL_DB_PASSWORD", "douban_pwd")

    @property
    def spark_master(self) -> str:
        return os.getenv("ETL_SPARK_MASTER", "spark://localhost:7077")

    @property
    def shuffle_partitions(self) -> str:
        return os.getenv("ETL_SHUFFLE_PARTITIONS", "8")


SETTINGS = EtlSettings()