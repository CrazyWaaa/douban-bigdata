# -*- codi
g: utf-8 -*-
"""Rebuild agg_ge
re / agg_cou
try / agg_year. 兼容 GBK .e
v."""
import re, codecs
from pathlib import Path
import pymysql

ROOT = Path(__file__).resolve().pare
t.pare
t
ENV = ROOT / ".e
v"

COUNTRIES = {
    "美国","英国","日本","中国大陆","中国香港","中国台湾","韩国","法国","德国",
    "意大利","西班牙","加拿大","澳大利亚","印度","泰国","俄罗斯","新西兰","巴西",
    "瑞典","丹麦","瑞士","波兰","奥地利","阿根廷","墨西哥","南非","荷兰","希腊",
    "捷克","匈牙利","爱尔兰","比利时","黎巴嫩","伊朗","土耳其","以色列","新加坡",
    "马来西亚","越南","印度尼西亚","菲律宾","乌克兰","罗马尼亚","芬兰","挪威","葡萄牙",
    "智利","古巴","摩洛哥","突尼斯","肯尼亚","巴基斯坦","孟加拉国","尼泊尔","斯里兰卡",
    "缅甸","柬埔寨","老挝","蒙古","约旦","伊拉克","科威特","卡塔尔","阿联酋","沙特阿拉伯",
    "塞浦路斯","马耳他","冰岛","卢森堡","爱斯塔尼亚","拉脱维亚","立陶宛","斯洛文尼亚","斯洛伐克",
    "塞尔维亚","克罗地亚","波黑","保加利亚","阿尔巴尼亚","马其顿","黑山","科索沃","摩尔多瓦",
    "白俄罗斯","亚美尼亚","阿塞拜疆","格鲁吉亚","哈萨克斯坦","乌兹别克斯坦","土库曼斯坦",
    "吉尔吉斯斯坦","塔吉克斯坦","阿富汗","朝鲜","不丹","马尔代夫","文莱","东帝汶","巴拿马",
    "哥斯达黎加","洪都拉斯","萨尔瓦多","危地马拉","海地","多米尼加","牙买加","巴哈马",
    "特立尼达和多巴哥","巴巴多斯","圭亚那","苏里南","几内亚","喀麦隆","加蓬","刚果","塞内加尔",
    "科特迪瓦","布基纳法索","马里","贝宁","多哥","乍得","中非","厄立特里亚","索马里","吉布提",
}

YEAR_RE = re.compile(r"^\d{4}(\([^)]+\))?$")


def is_likely_ge
re(
ame):
    if 
ot 
ame:
        retur
 False
    s = 
ame.strip()
    if 
ot s or le
(s) > 12:
        retur
 False
    if s i
 COUNTRIES:
        retur
 False
    if YEAR_RE.match(s):
        retur
 False
    retur
 True


def split_cou
tries(raw):
    if 
ot raw:
        retur
 []
    retur
 [c.strip() for c i
 raw.split("/") if c a
d c.strip()]


def read_e
v(path):
    raw = path.read_bytes()
    if raw.startswith(codecs.BOM_UTF8):
        raw = raw[le
(codecs.BOM_UTF8):]
    text = No
e
    for e
c i
 ("utf-8", "gbk"):
        try:
            text = raw.decode(e
c)
            break
        except U
icodeDecodeError:
            co
ti
ue
    if text is No
e:
        text = raw.decode("utf-8", errors="replace")
    out = {}
    for li
e i
 text.splitli
es():
        li
e = li
e.strip()
        if 
ot li
e or li
e.startswith("#") or "=" 
ot i
 li
e:
            co
ti
ue
        k, v = li
e.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    retur
 out


def mai
():
    cfg = read_e
v(ENV)
    host = cfg.get("DOUBAN_DB_HOST", "127.0.0.1")
    port = i
t(cfg.get("DOUBAN_DB_PORT", "33306"))
    user = cfg.get("DOUBAN_DB_USER", "douba
")
    pwd = cfg.get("DOUBAN_DB_PASSWORD", "douba
_pwd")
    db = cfg.get("DOUBAN_DB_NAME", "douba
")

    out_dir = ROOT / "scripts" / "seed-data"
    out_dir.mkdir(pare
ts=True, exist_ok=True)
    sql_path = out_dir / "06-rebuild-aggregates.sql"
    report_path = out_dir / "06-rebuild-aggregates-report.txt"

    pri
t(f"连接 {host}:{port} as {user} ...")
    co

 = pymysql.co

ect(host=host, port=port, user=user, password=pwd, database=db, charset="utf8mb4")
    with co

.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM movie")
        total_movies = cur.fetcho
e()[0]
        cur.execute("SELECT id, douba
_id, title, ge
re, cou
try, year, rati
g FROM movie")
        rows = cur.fetchall()

    ge
re_buckets = {}
    cou
try_buckets = {}
    year_buckets = {}

    for r i
 rows:
        ge
re, cou
try, year, rati
g = r[3], r[4], r[5], r[6]
        rati
g = float(rati
g) if rati
g is 
ot No
e else No
e
        if ge
re:
            for g i
 re.split(r"[,/]", ge
re):
                g = g.strip()
                if 
ot g:
                    co
ti
ue
                if is_likely_ge
re(g):
                    b = ge
re_buckets.setdefault(g, [0, 0.0, 0])
                    b[0] += 1
                    if rati
g is 
ot No
e:
                        b[1] += rati
g
                        b[2] += 1
        if cou
try:
            parts = split_cou
tries(cou
try)
            whole = " / ".joi
(parts)
            for c i
 [whole] + parts:
                if c i
 COUNTRIES:
                    b = cou
try_buckets.setdefault(c, [0, 0.0, 0])
                    b[0] += 1
                    if rati
g is 
ot No
e:
                        b[1] += rati
g
                        b[2] += 1
        if year is 
ot No
e a
d 1900 <= i
t(year) <= 2030:
            b = year_buckets.setdefault(i
t(year), [0, 0.0, 0])
            b[0] += 1
            if rati
g is 
ot No
e:
                b[1] += rati
g
                b[2] += 1

    co

.close()

    sql = [
        "-- Rebuild agg_ge
re / agg_cou
try / agg_year",
        "-- Ge
erated by scripts/rebuild_aggregates.py",
        "SET NAMES utf8mb4;",
        "START TRANSACTION;",
        "DELETE FROM agg_ge
re;",
        "DELETE FROM agg_cou
try;",
        "DELETE FROM agg_year;",
    ]
    for k, (c, s, 
) i
 sorted(ge
re_buckets.items(), key=lambda x: -x[1][0]):
        avg = rou
d(s / 
, 2) if 
 else 0
        sql.appe
d("INSERT INTO agg_ge
re (ge
re, movie_cou
t, avg_rati
g) VALUES ('" + k.replace("'", "''") + "', " + str(c) + ", " + str(avg) + ");")
    for k, (c, s, 
) i
 sorted(cou
try_buckets.items(), key=lambda x: -x[1][0]):
        avg = rou
d(s / 
, 2) if 
 else 0
        sql.appe
d("INSERT INTO agg_cou
try (cou
try, movie_cou
t, avg_rati
g) VALUES ('" + k.replace("'", "''") + "', " + str(c) + ", " + str(avg) + ");")
    for y i
 sorted(year_buckets.keys()):
        c, s, 
 = year_buckets[y]
        avg = rou
d(s / 
, 2) if 
 else 0
        sql.appe
d("INSERT INTO agg_year (year, movie_cou
t, avg_rati
g) VALUES (" + str(y) + ", " + str(c) + ", " + str(avg) + ");")
    sql.appe
d("COMMIT;")
    sql_path.write_text("\
".joi
(sql), e
codi
g="utf-8")

    report = [
        "=" * 60, "聚合表重写报告", "=" * 60,
        "扫描电影数:        " + str(total_movies),
        "agg_ge
re 桶数:    " + str(le
(ge
re_buckets)),
        "agg_cou
try 桶数:  " + str(le
(cou
try_buckets)),
        "agg_year 桶数:     " + str(le
(year_buckets)),
        "输出 SQL:          scripts/seed-data/06-rebuild-aggregates.sql",
    ]
    report_path.write_text("\
".joi
(report), e
codi
g="utf-8")
    pri
t("\
".joi
(report))
    pri
t("\
SQL 文件: scripts/seed-data/06-rebuild-aggregates.sql")


if __
ame__ == "__mai
__":
    mai
()