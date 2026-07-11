"""PySpark ETL 主任务：从 HDFS 读取 JSONL，规范化、写 MySQL。"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime

from pyspark.sql import SparkSession

from spark.etl.aggregator import agg_country, agg_genre, agg_year
from spark.etl.reader import read_raw
from spark.etl.settings import SETTINGS
from spark.etl.transformer import filter_valid, transform
from spark.etl.writer import write_aggregates, write_movie


def build_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("DoubanETL")
        .master(SETTINGS.spark_master)
        .config("spark.sql.shuffle.partitions", SETTINGS.shuffle_partitions)
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def run(input_override: str | None = None, only_aggregates: bool = False, skip_writes: bool = False) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    spark = build_spark()

    input_path = input_override or SETTINGS.hdfs_input_dir
    logging.info("read input: %s", input_path)

    raw = (
        spark.read.option("mode", "PERMISSIVE").json(f"{input_path}/*.jsonl")
        if input_override
        else read_raw(spark)
    )

    cleaned = transform(raw)
    cleaned = filter_valid(cleaned)
    cleaned = cleaned.cache()
    logging.info("cleaned row count: %s", cleaned.count())

    agg_g = agg_genre(cleaned)
    agg_c = agg_country(cleaned)
    agg_y = agg_year(cleaned)

    if skip_writes:
        logging.info("skip writes by flag; showing aggregate previews instead")
        agg_g.show(20, False)
        agg_c.show(20, False)
        agg_y.show(20, False)
        return

    if not only_aggregates:
        write_movie(cleaned)

    write_aggregates(agg_g, agg_c, agg_y)

    logging.info("ETL 完成 at %s", datetime.now().isoformat(timespec="seconds"))
    spark.stop()


def main() -> int:
    p = argparse.ArgumentParser(description="豆瓣电影 ETL")
    p.add_argument("--input", help="覆盖默认 HDFS 输入路径（可指向本地目录做本地验证）")
    p.add_argument("--only-aggregates", action="store_true", help="跳过主表写入，只写聚合表")
    p.add_argument("--skip-writes", action="store_true", help="不写 MySQL，仅在 stdout 预览聚合结果")
    args = p.parse_args()
    run(input_override=args.input, only_aggregates=args.only_aggregates, skip_writes=args.skip_writes)
    return 0


if __name__ == "__main__":
    sys.exit(main())