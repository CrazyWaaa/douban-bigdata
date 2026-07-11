"""一次性脚本:把 crawler/data/raw/*.jsonl 转成 SQL INSERT,放进 scripts/seed-data/

docker compose 的 mysql 容器会在首次启动时自动执行 docker-entrypoint-initdb.d 下的 *.sql,
这样 docker compose up 后,数据库里就有数据,不必手动跑 ETL。

设计:
- 一个表一个 SQL 文件:01-schema.sql 自动建表;10-movie.sql 灌入主表;
  20-aggregates.sql 写入聚合表;30-dim-tables.sql 写入维度表
- truncate + insert,避免重复跑出错
- 文件 utf8mb4 编码,可被 MySQL 容器直接吃

用法:
    python scripts/generate_seed_data.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
SCHEMA_SRC = ROOT / "docs" / "schema.sql"
OUT_DIR = ROOT / "scripts" / "seed-data"

MOVIE_COLS = [
    "douban_id", "title", "director", "actors", "genre", "country", "year",
    "rating", "rating_count", "summary", "poster_url",
    "detail_url", "languages", "release_date", "runtime", "runtime_minutes",
    "quote", "better_than", "also_know_as", "imdb_id", "official_sites",
    "comment_short_count", "comment_review_count", "discussion_count",
    "rating_stars", "related_pics",
]


def _flatten(obj: dict) -> dict:
    out = {}
    for k, v in obj.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v, ensure_ascii=False)
        else:
            out[k] = v
    return out


def _esc(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value).replace("\\", "\\\\").replace("'", "\\''")
    return f"'{s}'"


def _build_movie_inserts() -> list[str]:
    sql: list[str] = ["DELETE FROM movie;"]
    if not RAW_DIR.exists():
        return sql
    for fp in sorted(RAW_DIR.glob("*.jsonl")):
        with fp.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                obj = _flatten(json.loads(line))
                values = [_esc(obj.get(c)) for c in MOVIE_COLS]
                sql.append(f"INSERT INTO movie ({','.join(MOVIE_COLS)}) VALUES ({','.join(values)});")
    return sql


def _build_aggregates_sql() -> list[str]:
    return [
        "DELETE FROM agg_genre;",
        "INSERT INTO agg_genre (genre, movie_count, avg_rating)",
        "SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(genre, '/', n.n), '/', -1)) AS g,",
        "       COUNT(*) AS movie_count, ROUND(AVG(rating), 2) AS avg_rating",
        "FROM movie m JOIN (SELECT 1 n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) n",
        "  ON CHAR_LENGTH(m.genre) - CHAR_LENGTH(REPLACE(m.genre, '/', '')) >= n.n - 1",
        "WHERE genre IS NOT NULL AND genre <> '' AND rating IS NOT NULL",
        "GROUP BY g ORDER BY movie_count DESC;",
        "",
        "DELETE FROM agg_country;",
        "INSERT INTO agg_country (country, movie_count, avg_rating)",
        "SELECT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(country, '/', n.n), '/', -1)) AS c,",
        "       COUNT(*) AS movie_count, ROUND(AVG(rating), 2) AS avg_rating",
        "FROM movie m JOIN (SELECT 1 n UNION SELECT 2 UNION SELECT 3) n",
        "  ON CHAR_LENGTH(m.country) - CHAR_LENGTH(REPLACE(m.country, '/', '')) >= n.n - 1",
        "WHERE country IS NOT NULL AND country <> '' AND rating IS NOT NULL",
        "GROUP BY c ORDER BY movie_count DESC;",
        "",
        "DELETE FROM agg_year;",
        "INSERT INTO agg_year (year, movie_count, avg_rating)",
        "SELECT year, COUNT(*), ROUND(AVG(rating), 2)",
        "FROM movie WHERE year IS NOT NULL GROUP BY year ORDER BY year;",
    ]


def _build_dim_sql() -> list[str]:
    return [
        "DELETE FROM dim_genre;",
        "INSERT INTO dim_genre (name)",
        "SELECT DISTINCT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(genre, '/', n.n), '/', -1))",
        "FROM movie m JOIN (SELECT 1 n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) n",
        "  ON CHAR_LENGTH(m.genre) - CHAR_LENGTH(REPLACE(m.genre, '/', '')) >= n.n - 1",
        "WHERE genre IS NOT NULL AND genre <> '';",
        "",
        "DELETE FROM dim_country;",
        "INSERT INTO dim_country (name)",
        "SELECT DISTINCT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(country, '/', n.n), '/', -1))",
        "FROM movie m JOIN (SELECT 1 n UNION SELECT 2 UNION SELECT 3) n",
        "  ON CHAR_LENGTH(m.country) - CHAR_LENGTH(REPLACE(m.country, '/', '')) >= n.n - 1",
        "WHERE country IS NOT NULL AND country <> '';",
        "",
        "DELETE FROM dim_year;",
        "INSERT INTO dim_year (year) SELECT DISTINCT year FROM movie WHERE year IS NOT NULL ORDER BY year;",
    ]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "01-schema.sql").write_text(SCHEMA_SRC.read_text(encoding="utf-8"), encoding="utf-8")
    (OUT_DIR / "10-movie.sql").write_text("\n".join(_build_movie_inserts()) + "\n", encoding="utf-8")
    (OUT_DIR / "20-aggregates.sql").write_text("\n".join(_build_aggregates_sql()) + "\n", encoding="utf-8")
    (OUT_DIR / "30-dim.sql").write_text("\n".join(_build_dim_sql()) + "\n", encoding="utf-8")
    n = sum(1 for _ in ROOT.glob("data/raw/*.jsonl"))
    print(f"[OK] seed data generated under {OUT_DIR} ({n} jsonl source files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())