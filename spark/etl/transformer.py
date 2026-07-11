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


def _ensure_col(df: DataFrame, name: str, default=None) -> Column:
    """若 JSON 里根本没有该字段（老格式爬虫输出），提供一个空占位，防止 DAG 报错。"""
    if name in df.columns:
        return F.col(name)
    return F.lit(default)


def transform(df: DataFrame) -> DataFrame:
    """统一字段、转换类型、按 douban_id 去重。"""
    # 先补齐所有可能缺失的扩展字段，避免老数据报错
    enriched = (
        df
        .withColumn("_douban_id", _ensure_col(df, "douban_id"))
        .withColumn("_title", _ensure_col(df, "title"))
    )
    cleaned = (
        enriched
        .filter(F.col("_douban_id").isNotNull())
        .withColumn("douban_id", F.trim(F.col("_douban_id")))
        .filter(F.col("douban_id").rlike("^[0-9]+$"))
        .withColumn("title", F.when(F.col("_title").isNull(), None).otherwise(F.trim(F.col("_title"))))
        .withColumn("director", _trim("director"))
        .withColumn("actors", _trim("actors"))
        .withColumn("genre", _trim("genre"))
        .withColumn("country", _trim("country"))
        .withColumn("year", _safe_int("year"))
        .withColumn("rating", _safe_double("rating"))
        .withColumn("rating_count", _safe_int("rating_count"))
        .withColumn("summary", _trim("summary"))
        .withColumn("poster_url", _trim("poster_url"))
        # ===== 扩展字段 =====
        .withColumn("detail_url", _trim("detail_url"))
        .withColumn("languages", _trim("languages"))
        .withColumn("release_date", _trim("release_date"))
        .withColumn("runtime", _trim("runtime"))
        .withColumn("runtime_minutes", _safe_int("runtime_minutes"))
        .withColumn("quote", _trim("quote"))
        .withColumn("better_than", _trim("better_than"))
        .withColumn("also_know_as", _trim("also_know_as"))
        .withColumn("imdb_id", _trim("imdb_id"))
        .withColumn("official_sites", _trim("official_sites"))
        .withColumn("comment_short_count", _safe_int("comment_short_count"))
        .withColumn("comment_review_count", _safe_int("comment_review_count"))
        .withColumn("discussion_count", _safe_int("discussion_count"))
        # rating_stars：如果是 dict/JSON，序列化为字符串写入
        .withColumn("rating_stars", _ensure_col(df, "rating_stars"))
        .withColumn(
            "rating_stars",
            F.when(
                F.col("rating_stars").isNull(), None
            ).when(
                F.col("rating_stars").cast("string").isin("{}", "null", "[]"), None
            ).otherwise(
                F.to_json(F.col("rating_stars"))
            )
        )
        # related_pics：如果是 list，序列化为 JSON 字符串
        .withColumn("related_pics", _ensure_col(df, "related_pics"))
        .withColumn(
            "related_pics",
            F.when(
                F.col("related_pics").isNull(), None
            ).when(
                F.col("related_pics").cast("string").isin("[]", "null"), None
            ).otherwise(
                F.to_json(F.col("related_pics"))
            )
        )
        .drop("_douban_id", "_title")
        .dropna(subset=["douban_id", "title"])
        .dropDuplicates(["douban_id"])
    )
    return cleaned


def filter_valid(df: DataFrame) -> DataFrame:
    """过滤掉明显异常的行，例如 year 超出合理范围。"""
    return df.filter(
        (F.col("year").isNull()) | ((F.col("year") >= 1888) & (F.col("year") <= F.year(F.current_date()) + 1))
    )