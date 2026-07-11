"""聚合维度：生成按类型 / 地区 / 年份的统计表（写入 agg_*）。"""
from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def agg_genre(movies: DataFrame) -> DataFrame:
    exploded = (
        movies
        .filter(F.col("genre").isNotNull())
        .select(F.explode(F.split(F.col("genre"), "/")).alias("genre_name"), "rating")
        .withColumn("genre_name", F.trim(F.col("genre_name")))
        .filter(F.col("genre_name") != "")
    )
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
    exploded = (
        movies
        .filter(F.col("country").isNotNull())
        .select(F.explode(F.split(F.col("country"), "/")).alias("country_name"), "rating")
        .withColumn("country_name", F.trim(F.col("country_name")))
        .filter(F.col("country_name") != "")
    )
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


def dim_genre() -> DataFrame:
    """维度表来自电影数据中拆分后的全部 genre 名称，写入 dim_genre。"""
    raise NotImplementedError


def dim_country() -> DataFrame:
    raise NotImplementedError


def dim_year(min_year: int = 1900, max_year: int | None = None) -> DataFrame:
    """生成年份维度表，max_year 默认取当前年。"""
    if max_year is None:
        max_year = 2025
    years = list(range(min_year, max_year + 1))
    return None  # 实际由 job.py 通过 createDataFrame 实现