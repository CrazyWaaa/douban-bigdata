# -*- coding: utf-8 -*-
"""稳健版:替换 movie 表数据。

输出 4 个 Navicat 可执行的 SQL + 1 个报告:
  01-create-protected-table.sql   建 movie_protected 表
  02-extract-protected.sql         从 movie 抽 9 个保护字段
  03-replace-movie.sql             TRUNCATE + INSERT 朋友 250 行
  04-restore-protected.sql         回填保护字段
  50-replace-report.txt            覆盖率 + 执行后预期

保护字段 (朋友 SQL 没数据,丢不起):
  director, quote, better_than, also_know_as,
  imdb_id, official_sites, comment_short_count,
  comment_review_count, discussion_count

策略:
  1) 解析 data/douban.sql (movie 28 列) -> {douban_id: row}
  2) 解析 data/movies.sql (movies 19 列) -> [row]
  3) 朋友 douban_id 从 detail_url 提取
  4) 你的 douban_id NULL 的 2 行 (教父/末代皇帝) 用 title 匹配朋友的 1291841/1293172
  5) 字段映射 + 类型/格式转换
  6) 生成 4 个 SQL,每个独立可执行
"""
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_YOUR_SQL = ROOT / "data" / "douban.sql"
DEFAULT_FRIEND_SQL = ROOT / "data" / "movies.sql"
OUT_DIR = ROOT / "scripts" / "seed-data"

YOUR_COLUMNS = [
    "id", "douban_id", "title", "director", "actors", "genre", "country",
    "year", "rating", "rating_count", "summary", "poster_url",
    "detail_url", "languages", "release_date", "runtime", "runtime_minutes",
    "quote", "better_than", "also_know_as", "imdb_id", "official_sites",
    "comment_short_count", "comment_review_count", "discussion_count",
    "rating_stars", "related_pics", "created_at",
]
# 19 个字段中朋友有的 17 个
FRIEND_COLUMNS = [
    "id", "directors", "movie_rating", "title", "detail_url", "actors", "cover_url",
    "release_year", "genres", "regions", "languages", "release_dates", "runtime",
    "comment_count", "star_ratios", "summary", "detail_images",
    "created_at", "updated_at",
]
PROTECTED_COLUMNS = [
    "director", "quote", "better_than", "also_know_as", "imdb_id", "official_sites",
    "comment_short_count", "comment_review_count", "discussion_count",
]

# ============ SQL 解析 ============
def split_tuples(body):
    out, depth, cur, quote, i = [], 0, "", None, 0
    while i < len(body):
        c = body[i]
        if quote:
            if c == "\\" and i + 1 < len(body):
                cur += c + body[i+1]; i += 2; continue
            cur += c
            if c == quote: quote = None
        elif c in ("\u0027", '"'):
            quote = c; cur += c
        elif c == "(":
            depth += 1
            if depth == 1: cur = ""
            else: cur += c
        elif c == ")":
            depth -= 1
            if depth == 0: out.append(cur.strip()); cur = ""
            else: cur += c
        else:
            cur += c
        i += 1
    return out

def parse_row(row):
    out, depth, cur, quote, i = [], 0, "", None, 0
    while i < len(row):
        c = row[i]
        if quote:
            if c == "\\" and i + 1 < len(row):
                cur += c + row[i+1]; i += 2; continue
            cur += c
            if c == quote: quote = None
        elif c in ("\u0027", '"'):
            quote = c; cur += c
        elif c == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += c
        i += 1
    if cur.strip(): out.append(cur.strip())
    return out

def strip_sql_value(v):
    if v == "NULL" or v == "": return None
    if len(v) >= 2 and v[0] == "\u0027" and v[-1] == "\u0027":
        return v[1:-1].replace("\\'", "'").replace("\\\\", "\\")
    try:
        if "." in v: return float(v)
        return int(v)
    except ValueError:
        return v

def parse_table(path, table_name, columns):
    t = Path(path).read_text(encoding="utf-8", errors="replace")
    pattern = r"INSERT INTO `" + re.escape(table_name) + r"` VALUES\s*\(.*?\);\s*"
    blocks = re.findall(pattern, t, flags=re.DOTALL)
    rows = []
    for b in blocks:
        # b 是 "INSERT INTO ... VALUES " + 第一个 tuple 的内容
        # split_tuples 需要 ( ... )( ... )... 形式,所以我们要包装
        wrapped = "(" + b + ")"
        tuples = split_tuples(wrapped)
        if not tuples: continue
        cells = [strip_sql_value(c) for c in parse_row(tuples[0])]
        if len(cells) < len(columns):
            cells += [None] * (len(columns) - len(cells))
        rec = dict(zip(columns, cells))
        rows.append(rec)
    return rows

# ============ 工具 ============
def sql_escape(v):
    if v is None: return "NULL"
    if isinstance(v, bool): return "1" if v else "0"
    if isinstance(v, (int, float)):
        if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
            return "NULL"
        return str(v)
    s = str(v).replace("\\", "\\\\").replace("\u0027", "\\'")
    return "\u0027" + s + "\u0027"

def split_tuples_safe(body):
    # 给一段裸 VALUES 内容,返回每行 tuple 的纯内容
    return split_tuples("(" + body + ")" if not body.startswith("(") else body)

def parse_runtime_minutes(rt):
    if not rt: return None
    s = str(rt)
    h = re.search(r"(\d+)\s*(?:小时|h)", s, re.IGNORECASE)
    m = re.search(r"(\d+)\s*(?:分钟|分|min)", s, re.IGNORECASE)
    total = 0
    if h: total += int(h.group(1)) * 60
    if m: total += int(m.group(1))
    if total == 0:
        d = re.search(r"(\d+)", s)
        if d: total = int(d.group(1))
    return total or None

def normalize_sep(s):
    if s is None: return None
    out = str(s).replace(",", "/").replace("、", "/").replace(" ", "")
    while "//" in out: out = out.replace("//", "/")
    return out.strip("/") or None

def parse_star_ratios(s):
    if not s: return None
    out = {}
    for part in str(s).replace("，", ",").split(","):
        part = part.strip()
        if not part: continue
        m = re.match(r"(\d)星\s*[:：]\s*([\d.]+)\s*%?", part)
        if m: out[m.group(1)] = float(m.group(2))
    return json.dumps(out, ensure_ascii=False) if out else None

def parse_related_pics(s):
    if not s: return None
    parts = [p.strip() for p in str(s).split(",") if p.strip()]
    return json.dumps(parts, ensure_ascii=False) if parts else None

def normalize_url(u):
    if not u: return None
    s = str(u).strip()
    if not s: return None
    return s if s.endswith("/") else s + "/"

def truncate_text(s, max_len):
    if s is None: return None
    s = str(s)
    return s[:max_len] if len(s) > max_len else s

# ============ 主流程 ============
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--your-sql", default=str(DEFAULT_YOUR_SQL))
    parser.add_argument("--friend-sql", default=str(DEFAULT_FRIEND_SQL))
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    args = parser.parse_args()

    print(f"[1/5] 解析你的 SQL: {args.your_sql}", flush=True)
    your_rows = parse_table(args.your_sql, "movie", YOUR_COLUMNS)
    print(f"      共 {len(your_rows)} 行", flush=True)

    print(f"[2/5] 解析朋友 SQL: {args.friend_sql}", flush=True)
    friend_rows = parse_table(args.friend_sql, "movies", FRIEND_COLUMNS)
    print(f"      共 {len(friend_rows)} 行", flush=True)

    # 提取 douban_id
    for r in your_rows:
        if not r.get("douban_id"):
            # douban_id 缺失,留 None,后续用 title 匹配
            pass
    for r in friend_rows:
        url = r.get("detail_url") or ""
        m = re.search(r"subject/(\d+)", str(url))
        r["douban_id"] = m.group(1) if m else None

    your_by_id = {str(r.get("douban_id")): r for r in your_rows if r.get("douban_id")}
    your_by_title = {str(r.get("title") or "").strip(): r for r in your_rows if r.get("title")}
    friend_by_id = {str(r.get("douban_id")): r for r in friend_rows if r.get("douban_id")}

    # 你的 douban_id 缺失的行,试图用 title 从朋友拿 douban_id
    missing_id = [r for r in your_rows if not r.get("douban_id")]
    for r in missing_id:
        title = (r.get("title") or "").strip()
        # 朋友的 douban_id 也可能在 title 找
        for fr in friend_rows:
            if (fr.get("title") or "").strip() == title and fr.get("douban_id"):
                r["douban_id_resolved"] = fr["douban_id"]
                break
        else:
            r["douban_id_resolved"] = None

    your_dids = set(your_by_id.keys()) | {r["douban_id_resolved"] for r in missing_id if r.get("douban_id_resolved")}
    friend_dids = set(friend_by_id.keys())

    inter = your_dids & friend_dids
    only_friend = friend_dids - your_dids
    only_your = your_dids - friend_dids
    print(f"      交集 {len(inter)}, 仅朋友 {len(only_friend)}, 仅你的 {len(only_your)}", flush=True)

    # === 01 建表 + 02 提取保护字段 ===
    print(f"[3/5] 生成保护字段 SQL", flush=True)
    out01 = [
        "-- ============================================================",
        "-- 01: 建 movie_protected 临时表 (存 douban_id 与 9 个保护字段)",
        f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "-- ============================================================",
        "SET NAMES utf8mb4;",
        "DROP TABLE IF EXISTS `movie_protected`;",
        "CREATE TABLE `movie_protected` (",
        "  `douban_id` varchar(32) NOT NULL,",
        "  `title` varchar(255) DEFAULT NULL,",
    ]
    for col in PROTECTED_COLUMNS:
        out01.append(f"  `{col}` text,")
    out01.extend([
        "  PRIMARY KEY (`douban_id`) USING BTREE",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;",
        "",
    ])

    # === 02 提取 ===
    out02 = [
        "-- ============================================================",
        "-- 02: 从 movie 表抽 9 个保护字段到 movie_protected",
        "-- 只要 douban_id 非 NULL 且保护字段非 NULL 就保留",
        "-- ============================================================",
    ]
    extracted_count = {c: 0 for c in PROTECTED_COLUMNS}
    for r in your_rows:
        did = r.get("douban_id") or r.get("douban_id_resolved")
        if not did: continue
        cols_to_write = []
        for col in PROTECTED_COLUMNS:
            v = r.get(col)
            if v is None or v == "" or v == "null":
                continue
            cols_to_write.append((col, v))
        if not cols_to_write:
            continue
        cols_sql = ", ".join(f"`{c}`" for c, _ in cols_to_write)
        vals_sql = ", ".join(sql_escape(v) for _, v in cols_to_write)
        out02.append(
            f"INSERT INTO `movie_protected` (`douban_id`, `title`, {cols_sql}) "
            f"VALUES ({sql_escape(str(did))}, {sql_escape(r.get('title'))}, {vals_sql});"
        )
        for col, _ in cols_to_write:
            extracted_count[col] += 1
    out02.append("")

    # === 03 TRUNCATE + INSERT ===
    print(f"[4/5] 生成替换 SQL", flush=True)
    out03 = [
        "-- ============================================================",
        "-- 03: TRUNCATE movie + INSERT 朋友 250 行 (字段映射 + 转换)",
        "-- 保护字段 (director/quote/...) 暂留 NULL,下一步 04 回填",
        "-- ============================================================",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "TRUNCATE TABLE `movie`;",
        "ALTER TABLE `movie` AUTO_INCREMENT = 1;",
        "",
    ]
    insert_cols = ["douban_id", "title", "actors", "genre", "country",
                   "year", "rating", "rating_count", "summary", "poster_url",
                   "detail_url", "languages", "release_date", "runtime",
                   "runtime_minutes", "rating_stars", "related_pics"]
    insert_count = 0
    for fr in friend_rows:
        did = fr.get("douban_id")
        if not did: continue
        url = normalize_url(fr.get("detail_url"))
        rt = fr.get("runtime")
        values = {
            "douban_id": str(did),
            "title": fr.get("title"),
            "actors": fr.get("actors"),
            "genre": fr.get("genres"),
            "country": fr.get("regions"),
            "year": int(fr["release_year"]) if fr.get("release_year") and str(fr["release_year"]).isdigit() else None,
            "rating": fr.get("movie_rating"),
            "rating_count": fr.get("comment_count"),
            "summary": truncate_text(fr.get("summary"), 4000),
            "poster_url": truncate_text(fr.get("cover_url"), 500),
            "detail_url": url,
            "languages": normalize_sep(fr.get("languages")),
            "release_date": normalize_sep(fr.get("release_dates")),
            "runtime": rt,
            "runtime_minutes": parse_runtime_minutes(rt),
            "rating_stars": parse_star_ratios(fr.get("star_ratios")),
            "related_pics": parse_related_pics(fr.get("detail_images")),
        }
        cols_sql = ", ".join(f"`{c}`" for c in insert_cols)
        vals_sql = ", ".join(sql_escape(values[c]) for c in insert_cols)
        out03.append(f"INSERT INTO `movie` ({cols_sql}) VALUES ({vals_sql});")
        insert_count += 1
    out03.extend([
        "SET FOREIGN_KEY_CHECKS = 1;",
        "",
    ])

    # === 04 回填保护字段 ===
    print(f"[5/5] 生成回填 SQL", flush=True)
    out04 = [
        "-- ============================================================",
        "-- 04: 从 movie_protected 回填保护字段到 movie",
        "-- 用 douban_id JOIN,只在 movie 字段为 NULL 时回填",
        "-- ============================================================",
        "",
    ]
    restore_count = {c: 0 for c in PROTECTED_COLUMNS}
    for col in PROTECTED_COLUMNS:
        out04.append(f"-- 回填 {col}")
        out04.append(
            f"UPDATE `movie` m JOIN `movie_protected` p ON m.`douban_id` = p.`douban_id` "
            f"SET m.`{col}` = p.`{col}` "
            f"WHERE (m.`{col}` IS NULL OR m.`{col}` = '') "
            f"AND p.`{col}` IS NOT NULL;"
        )
    out04.append("")
    out04.append("DROP TABLE IF EXISTS `movie_protected`;")
    out04.append("")

    # === 写文件 ===
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "01-create-protected-table.sql": out01,
        "02-extract-protected.sql": out02,
        "03-replace-movie.sql": out03,
        "04-restore-protected.sql": out04,
    }
    for name, content in files.items():
        p = out_dir / name
        p.write_text("\n".join(content), encoding="utf-8")
        print(f"      已写入: {p} ({sum(len(c) for c in content)} chars, {len(content)} lines)", flush=True)

    # === 报告 ===
    report = []
    report.append("=" * 70)
    report.append("movie 表替换 — 报告")
    report.append("=" * 70)
    report.append(f"你的 movie 行数:    {len(your_rows)}")
    report.append(f"朋友 movies 行数:   {len(friend_rows)}")
    report.append(f"交集:               {len(inter)}")
    report.append(f"仅朋友:             {len(only_friend)}")
    report.append(f"仅你的:             {len(only_your)}")
    report.append(f"你 douban_id NULL:  {len(missing_id)} (用 title 从朋友回填)")
    for r in missing_id:
        resolved = r.get("douban_id_resolved") or "(未匹配)"
        report.append(f"    - {(r.get('title') or '').strip():20} -> {resolved}")
    report.append("")
    report.append(f"将 INSERT:          {insert_count} 行 (朋友全部)")
    report.append(f"保护字段提取:")
    for c in PROTECTED_COLUMNS:
        report.append(f"    {c:25} {extracted_count[c]:>4} 行")
    report.append("")
    report.append("=" * 70)
    report.append("Navicat 执行顺序 (按顺序执行,不要跳步)")
    report.append("=" * 70)
    report.append("  1. 备份: 在 Navicat 里对 movie 表右键 -> 转储 SQL -> 仅结构+数据")
    report.append("  2. 执行 01-create-protected-table.sql")
    report.append("  3. 执行 02-extract-protected.sql (保护字段)")
    report.append("  4. 执行 03-replace-movie.sql (TRUNCATE + INSERT 朋友数据)")
    report.append("  5. 执行 04-restore-protected.sql (回填保护字段)")
    report.append("  6. 跑 Spark ETL 重新生成 agg_*/dim_* 聚合表:")
    report.append("       cd spark && ./run_etl.sh  (或 run_local_check.sh)")
    report.append("  7. 验证: SELECT COUNT(*), COUNT(release_date), COUNT(runtime_minutes),")
    report.append("            COUNT(rating_stars), COUNT(detail_url) FROM movie;")
    report.append("")
    report.append("=" * 70)
    report.append("执行后预期")
    report.append("=" * 70)
    report.append(f"  movie 总行数:    {insert_count}")
    report.append("  detail_url 非空: ~99% (250 - 你的 douban_id NULL 行)")
    report.append("  release_date:    ~99%")
    report.append("  runtime_minutes: ~99% (取决于朋友 runtime 格式可解析)")
    report.append("  rating_stars:    ~99%")
    report.append("  related_pics:    ~99%")
    report.append("  director:        由 04 回填你的双语版 (约 250 行)")
    report.append("  quote/better_than/...: 由 04 回填你原有的非 NULL 值")
    report.append("")
    rp = out_dir / "50-replace-report.txt"
    rp.write_text("\n".join(report), encoding="utf-8")
    print(f"      已写入: {rp}", flush=True)

if __name__ == "__main__":
    main()
