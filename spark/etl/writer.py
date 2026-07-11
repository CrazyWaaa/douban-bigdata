"""JDBC 写入：把清洗后的 movie 主表与 3 张聚合表写入 MySQL。"""
from __future__ import annotations

import logging
from typing import Iterable

from pyspark.sql import DataFrame

from .settings import SETTINGS

LOGGER = logging.getLogger(__name__)


def _write(df: DataFrame, table: str, mode: str = "overwrite") -> None:
    LOGGER.info("writing %s rows to %s (mode=%s)", df.count(), table, mode)
    (
        df.write
        .mode(mode)
        .option("url", SETTINGS.jdbc_url)
        .option("user", SETTINGS.jdbc_user)
        .option("password", SETTINGS.jdbc_password)
        .option("dbtable", table)
        .option("batchsize", 1000)
        .option("rewriteBatchedStatements", "true")
        .option("createTableIfNotExist", "true")
        .format("jdbc")
        .save()
    )


def write_movie(movies: DataFrame) -> None:
    select_cols = [
        "douban_id", "title", "director", "actors", "genre", "country",
        "year", "rating", "rating_count", "summary", "poster_url",
    ]
    _write(movies.select(*select_cols), "movie")


def write_aggregates(
    agg_genre: DataFrame,
    agg_country: DataFrame,
    agg_year: DataFrame,
    dim_genre: DataFrame | None = None,
    dim_country: DataFrame | None = None,
    dim_year: DataFrame | None = None,
) -> None:
    _write(agg_genre, "agg_genre")
    _write(agg_country, "agg_country")
    _write(agg_year, "agg_year")
    if dim_genre is not None:
        _write(dim_genre, "dim_genre")
    if dim_country is not None:
        _write(dim_country, "dim_country")
    if dim_year is not None:
        _write(dim_year, "dim_year")