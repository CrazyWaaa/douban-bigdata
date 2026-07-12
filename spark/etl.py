"""纯 Python ETL：读取 /data/raw/*.jsonl，清洗后写入 MySQL。"""
from __future__ import annotations

import argparse
import glob
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Any

import pymysql
from pymysql.cursors import DictCursor

LOGGER = logging.getLogger(__name__)

MOVIE_COLS = [
    "douban_id", "title", "director", "actors", "genre", "country",
    "year", "rating", "rating_count", "summary", "poster_url",
    "detail_url", "languages", "release_date", "runtime", "runtime_minutes",
    "quote", "better_than", "also_know_as", "imdb_id", "official_sites",
    "comment_short_count", "comment_review_count", "discussion_count",
    "rating_stars", "related_pics",
]


# ---------- 数据库连接 ----------
def get_conn() -> pymysql.Connection:
    host = os.getenv("ETL_DB_HOST", "127.0.0.1")
    port = int(os.getenv("ETL_DB_PORT", "3306"))
    user = os.getenv("ETL_DB_USER", "douban")
    password = os.getenv("ETL_DB_PASSWORD", "douban_pwd")
    db = os.getenv("ETL_DB_NAME", "douban")
    return pymysql.connect(
        host=host, port=port, user=user, password=password, db=db,
        charset="utf8mb4", cursorclass=DictCursor,
    )


# ---------- 数据清洗 ----------
def _safe_int(v: Any) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None


def _safe_float(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _json_str(v: Any) -> str | None:
    """rating_stars / related_pics 等复合字段，序列化为 JSON 字符串或 None。"""
    if v is None or v == "" or v == {} or v == []:
        return None
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    s = str(v).strip()
    if s in ("{}", "[]", "null"):
        return None
    return s


def clean_row(raw: dict[str, Any]) -> dict[str, Any] | None:
    douban_id = _safe_str(raw.get("douban_id"))
    if not douban_id or not douban_id.isdigit():
        return None

    title = _safe_str(raw.get("title"))
    if not title:
        return None

    year = _safe_int(raw.get("year"))
    current_year = datetime.now().year
    if year is not None and (year < 1888 or year > current_year + 1):
        year = None

    return {
        "douban_id": douban_id,
        "title": title,
        "director": _safe_str(raw.get("director")),
        "actors": _safe_str(raw.get("actors")),
        "genre": _safe_str(raw.get("genre")),
        "country": _safe_str(raw.get("country")),
        "year": year,
        "rating": _safe_float(raw.get("rating")),
        "rating_count": _safe_int(raw.get("rating_count")),
        "summary": _safe_str(raw.get("summary")),
        "poster_url": _safe_str(raw.get("poster_url")),
        "detail_url": _safe_str(raw.get("detail_url")),
        "languages": _safe_str(raw.get("languages")),
        "release_date": _safe_str(raw.get("release_date")),
        "runtime": _safe_str(raw.get("runtime")),
        "runtime_minutes": _safe_int(raw.get("runtime_minutes")),
        "quote": _safe_str(raw.get("quote")),
        "better_than": _safe_str(raw.get("better_than")),
        "also_know_as": _safe_str(raw.get("also_know_as")),
        "imdb_id": _safe_str(raw.get("imdb_id")),
        "official_sites": _safe_str(raw.get("official_sites")),
        "comment_short_count": _safe_int(raw.get("comment_short_count")),
        "comment_review_count": _safe_int(raw.get("comment_review_count")),
        "discussion_count": _safe_int(raw.get("discussion_count")),
        "rating_stars": _json_str(raw.get("rating_stars")),
        "related_pics": _json_str(raw.get("related_pics")),
    }


# ---------- 读取 ----------
def load_raw(input_dir: str) -> list[dict[str, Any]]:
    files = sorted(glob.glob(os.path.join(input_dir, "*.jsonl")))
    if not files:
        LOGGER.warning("no .jsonl files found in %s", input_dir)
        return []
    rows: list[dict[str, Any]] = []
    for fp in files:
        LOGGER.info("reading %s", fp)
        with open(fp, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                    if isinstance(raw, dict):
                        rows.append(raw)
                except json.JSONDecodeError as e:
                    LOGGER.warning("skip invalid JSON line %d in %s: %s", lineno, fp, e)
    return rows


# ---------- 写入 ----------
def write_movies(conn: pymysql.Connection, movies: list[dict[str, Any]]) -> None:
    placeholders = ", ".join(["%s"] * len(MOVIE_COLS))
    col_list = ", ".join(MOVIE_COLS)
    updates = ", ".join([f"{c}=VALUES({c})" for c in MOVIE_COLS if c != "douban_id"])
    sql = (
        f"INSERT INTO movie ({col_list}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {updates}"
    )
    values = [tuple(m[c] for c in MOVIE_COLS) for m in movies]
    with conn.cursor() as cur:
        affected = cur.executemany(sql, values)
    conn.commit()
    LOGGER.info("wrote %d rows to movie (executemany affected=%s)", len(movies), affected)


def _aggregate(movies: list[dict[str, Any]], key: str) -> list[tuple[Any, int, float | None]]:
    """按 key 聚合，返回 [(value, count, avg_rating), ...]"""
    stats: dict[str, list[int, float]] = defaultdict(lambda: [0, 0.0])
    for m in movies:
        v = m.get(key)
        if not v:
            continue
        for part in str(v).split():
            part = part.strip()
            if not part:
                continue
            stats[part][0] += 1
            rating = m.get("rating")
            if rating is not None:
                stats[part][1] += rating
    result = []
    for k, (cnt, total_rating) in stats.items():
        avg = round(total_rating / cnt, 2) if cnt > 0 else None
        result.append((k, cnt, avg))
    return result


def write_aggregates(conn: pymysql.Connection, movies: list[dict[str, Any]]) -> None:
    tables = {
        "agg_genre": (_aggregate(movies, "genre"), "genre"),
        "agg_country": (_aggregate(movies, "country"), "country"),
        "agg_year": (
            [(str(m["year"]), 1, m["rating"]) for m in movies if m.get("year") is not None],
            "year",
        ),
    }
    # 对 agg_year 做归并（上面是逐行，需要按 year 聚合）
    year_agg: dict[str, list[int, float]] = defaultdict(lambda: [0, 0.0])
    for m in movies:
        y = m.get("year")
        if y is None:
            continue
        year_agg[str(y)][0] += 1
        if m.get("rating") is not None:
            year_agg[str(y)][1] += m["rating"]
    tables["agg_year"] = (
        [(k, v[0], round(v[1] / v[0], 2) if v[0] > 0 else None) for k, v in year_agg.items()],
        "year",
    )

    for table, (rows, key_col) in tables.items():
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {table}")
        if not rows:
            continue
        placeholders = ", ".join(["%s"] * 3)
        sql = f"INSERT INTO {table} ({key_col}, movie_count, avg_rating) VALUES ({placeholders})"
        values = [(k, cnt, avg) for k, cnt, avg in rows]
        with conn.cursor() as cur:
            cur.executemany(sql, values)
        conn.commit()
        LOGGER.info("wrote %d rows to %s", len(rows), table)

    # dim 表：写入去重后的维度值（保持与 agg_* 一致的集合）
    for dim_table, col in [("dim_genre", "genre"), ("dim_country", "country")]:
        rows_list, _ = tables[f"agg_{col}"]
        values = [(k,) for k, _, _ in rows_list]
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {dim_table}")
            if values:
                cur.executemany(f"INSERT IGNORE INTO {dim_table} (name) VALUES (%s)", values)
        conn.commit()
        LOGGER.info("wrote %d rows to %s", len(values), dim_table)

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE dim_year")
        year_values = [(int(k),) for k, _, _ in tables["agg_year"][0]]
        if year_values:
            cur.executemany("INSERT IGNORE INTO dim_year (year) VALUES (%s)", year_values)
    conn.commit()
    LOGGER.info("wrote %d rows to dim_year", len(year_values))


# ---------- 主流程 ----------
def run(input_dir: str, skip_writes: bool = False) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    raw_rows = load_raw(input_dir)
    LOGGER.info("raw rows: %d", len(raw_rows))

    cleaned: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw in raw_rows:
        row = clean_row(raw)
        if row is None:
            continue
        if row["douban_id"] in seen_ids:
            continue
        seen_ids.add(row["douban_id"])
        cleaned.append(row)
    LOGGER.info("cleaned rows: %d", len(cleaned))

    if skip_writes:
        LOGGER.info("skip writes flag; preview: %s",
                    [(m["douban_id"], m["title"], m.get("rating")) for m in cleaned[:5]])
        return

    conn = get_conn()
    try:
        if cleaned:
            write_movies(conn, cleaned)
            write_aggregates(conn, cleaned)
        LOGGER.info("ETL 完成 at %s", datetime.now().isoformat(timespec="seconds"))
    finally:
        conn.close()


def main() -> int:
    p = argparse.ArgumentParser(description="豆瓣电影 ETL")
    p.add_argument("--input", default=os.getenv("ETL_HDFS_INPUT", "/data/raw"),
                   help="输入目录（包含 *.jsonl）")
    p.add_argument("--skip-writes", action="store_true", help="仅预览，不写 MySQL")
    args = p.parse_args()
    run(args.input, skip_writes=args.skip_writes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
