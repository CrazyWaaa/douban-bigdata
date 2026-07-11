"""PySpark ETL：从 HDFS 读取 JSONL，规范化字段后按多维度聚合，结果写回 MySQL。"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def build_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("DoubanETL")
        .master("spark://localhost:7077")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def main() -> None:
    spark = build_spark()
    print("[spark] 占位实现：待补充 ETL 逻辑")
    spark.stop()


if __name__ == "__main__":
    main()