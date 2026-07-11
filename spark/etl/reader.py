"""读取 HDFS 上的爬虫 JSONL 数据。"""
from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession

from .settings import SETTINGS


def read_raw(spark: SparkSession) -> DataFrame:
    """HDFS 路径下所有 JSONL，读入后字段为嵌套 row。"""
    return (
        spark.read
        .option("mode", "PERMISSIVE")
        .option("multiline", "false")
        .json(f"{SETTINGS.hdfs_input_dir}/*.jsonl")
    )