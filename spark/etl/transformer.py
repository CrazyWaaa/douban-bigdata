"""清洗与规范化：类型转换、去空、去重、字段清洗。"""
from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


def _safe_int(col_name: str) -> Column:
    return F.when(F.col(col_name).isNull(), None).otherwise(F.col(col_name).cast("int"))


def _safe_double(col_name: str) -> Column:
    return F.when(F.col(col_name).isNull(), None).otherwise(F.col(col_name).cast("double"))


def _trim(col_name: str) -> Column:
    return F.when(F.col(col_name).isNull(), None).otherwise(F.trim(F.col(col_name)))


def transform(df: DataFrame) -> DataFrame:
    """统一字段、转换类型、按 douban_id 去重。"""
    cleaned = (
        df
        .filter(F.col("douban_id").isNotNull())
        .withColumn("douban_id", F.trim(F.col("douban_id")))
        .filter(F.col("douban_id").rlike("^[0-9]+$"))
        .withColumn("title", _trim("title"))
        .withColumn("director", _trim("director"))
        .withColumn("actors", _trim("actors"))
        .withColumn("genre", _trim("genre"))
        .withColumn("country", _trim("country"))
        .withColumn("year", _safe_int("year"))
        .withColumn("rating", _safe_double("rating"))
        .withColumn("rating_count", _safe_int("rating_count"))
        .withColumn("summary", _trim("summary"))
        .withColumn("poster_url", _trim("poster_url"))
        .dropna(subset=["douban_id", "title"])
        .dropDuplicates(["douban_id"])
    )
    return cleaned


def filter_valid(df: DataFrame) -> DataFrame:
    """过滤掉明显异常的行，例如 year 超出合理范围。"""
    return df.filter(
        (F.col("year").isNull()) | ((F.col("year") >= 1888) & (F.col("year") <= F.year(F.current_date()) + 1))
    )