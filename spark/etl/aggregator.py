"""聚合维度：生成按类型 / 地区 / 年份的统计表（写入 agg_*）与 3 张维度表（写入 dim_*）。"""
from __future__ import annotations

from datetime import datetime

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, StringType, StructField, StructType


def _explode_delimited(df: DataFrame, source_col: str, alias: str) -> DataFrame:
    """把 "A / B / C" 这种分隔字段拆成多行并 trim / 去空。"""
    return (
        df
        .filter(F.col(source_col).isNotNull())
        .select(F.explode(F.split(F.col(source_col), "/")).alias(alias))
        .withColumn(alias, F.trim(F.col(alias)))
        .filter((F.col(alias) != "") & F.col(alias).isNotNull())
        .dropDuplicates([alias])
    )


def agg_genre(movies: DataFrame) -> DataFrame:
    exploded = _explode_delimited(movies, "genre", "genre_name").select("genre_name", "rating")
    return (
        exploded.groupBy("genre_name")
        .agg(
            F.count("*").alias("movie_count"),
            F.round(F.avg("rating"), 2).alias("avg_rating"),
        )
        .withColumnRenamed("genre_name", "genre")
        .orderBy(F.col("movie_count").desc())
    )


def agg_country(movies: DataFrame) -> DataFrame:
    exploded = _explode_delimited(movies, "country", "country_name").select("country_name", "rating")
    return (
        exploded.groupBy("country_name")
        .agg(
            F.count("*").alias("movie_count"),
            F.round(F.avg("rating"), 2).alias("avg_rating"),
        )
        .withColumnRenamed("country_name", "country")
        .orderBy(F.col("movie_count").desc())
    )


def agg_year(movies: DataFrame) -> DataFrame:
    return (
        movies
        .filter(F.col("year").isNotNull())
        .groupBy("year")
        .agg(
            F.count("*").alias("movie_count"),
            F.round(F.avg("rating"), 2).alias("avg_rating"),
        )
        .orderBy(F.col("year").asc())
    )


def dim_genre(movies: DataFrame) -> DataFrame:
    """维度表 dim_genre(id, name)：从 movie 中拆分出的全部 genre 名称，唯一去重。"""
    rows = _explode_delimited(movies, "genre", "name").orderBy("name")
    return rows.withColumn("id", F.monotonically_increasing_id().cast(IntegerType())).select("id", "name")


def dim_country(movies: DataFrame) -> DataFrame:
    """维度表 dim_country(id, name)：从 movie 中拆分出的全部 country 名称，唯一去重。"""
    rows = _explode_delimited(movies, "country", "name").orderBy("name")
    return rows.withColumn("id", F.monotonically_increasing_id().cast(IntegerType())).select("id", "name")


def dim_year(min_year: int = 1900, max_year: int | None = None) -> DataFrame:
    """维度表 dim_year(year)：默认 1900 至当前年（自然年维度，方便前端年代筛选）。"""
    if max_year is None:
        max_year = datetime.now().year
    schema = StructType([StructField("year", IntegerType(), nullable=False)])
    # createDataFrame 需要 SparkSession，从环境取不到就延迟到调用方注入；这里直接通过 Range 构造
    from pyspark.sql import SparkSession
    spark = SparkSession.getActiveSession() or SparkSession.builder.getOrCreate()
    return spark.createDataFrame([(y,) for y in range(min_year, max_year + 1)], schema=schema)