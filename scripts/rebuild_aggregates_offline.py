# -*- coding: utf-8 -*-
"""
基于实时 API 数据生成重建聚合表的 SQL
不连 DB,直接从运行中的后端拉接口聚合→写 SQL
"""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts" / "seed-data"
OUT.mkdir(parents=True, exist_ok=True)
API = "http://127.0.0.1:8080/api"

# 国家白名单(常见豆瓣 TOP250 出品国)
COUNTRIES = {
    "美国", "英国", "日本", "中国大陆", "中国香港", "中国台湾",
    "韩国", "法国", "德国", "意大利", "西班牙", "加拿大",
    "澳大利亚", "印度", "泰国", "俄罗斯", "新西兰", "巴西",
    "瑞典", "丹麦", "瑞士", "波兰", "奥地利", "阿根廷", "墨西哥",
    "南非", "荷兰", "希腊", "捷克", "匈牙利", "爱尔兰",
    "比利时", "黎巴嫩", "伊朗", "土耳其", "以色列", "新加坡",
    "马来西亚", "越南", "印尼", "菲律宾", "乌克兰", "罗马尼亚",
    "芬兰", "挪威", "葡萄牙", "智利", "古巴", "摩洛哥", "突尼斯",
    "肯尼亚", "巴基斯坦", "孟加拉国", "斯里兰卡",
    "缅甸", "柬埔寨", "老挝", "蒙古",
    "约旦", "伊拉克", "科威特", "卡塔尔", "阿联酋", "沙特阿拉伯",
    "塞浦路斯", "马耳他", "冰岛", "卢森堡",
    "爱沙尼亚", "拉脱维亚", "立陶宛", "斯洛文尼亚", "斯洛伐克",
    "塞尔维亚", "克罗地亚", "波黑", "保加利亚", "阿尔巴尼亚",
    "马其顿", "黑山", "科索沃", "摩尔多瓦", "白俄罗斯", "亚美尼亚",
    "阿塞拜疆", "格鲁吉亚", "哈萨克斯坦", "乌兹别克斯坦",
    "土库曼斯坦", "吉尔吉斯斯坦", "塔吉克斯坦",
    "阿富汗", "朝鲜", "不丹", "马尔代夫", "文莱", "东帝汶",
    "巴拿马", "哥斯达黎加", "洪都拉斯", "萨尔瓦多", "危地马拉",
    "海地", "多米尼加", "牙买加", "巴哈马", "特立尼达和多巴哥",
    "巴巴多斯", "圭亚那", "苏里南",
    "几内亚", "喀麦隆", "加蓬", "刚果", "塞内加尔", "科特迪瓦",
    "布基纳法索", "马里", "贝宁", "多哥", "乍得", "中非",
    "厄立特里亚", "索马里", "吉布提",
}

GENRE_BLACKLIST = COUNTRIES

def get(path):
    with urllib.request.urlopen(API + path, timeout=8) as r:
        data = json.loads(r.read())
        return data.get("data") or []

def split_countries(s):
    if not s: return []
    return [c.strip() for c in s.split("/") if c.strip()]

def is_genre(s):
    if not s: return False
    s = s.strip()
    if not s or len(s) > 12: return False
    if s in GENRE_BLACKLIST: return False
    if s[:4].isdigit() and (len(s) == 4 or (len(s) >= 5 and not s[4].isalpha())): return False
    return True

# 由于实时接口只给了聚合表,我们要从 movie 拉明细
# 这里走 /api/movies/paged 取全量
movies = []
total = None
page = 1
size = 100
while True:
    data = get(f"/movies/paged?page={page}&size={size}")
    if total is None:
        pass
    movies.extend(data)
    if len(data) < size: break
    page += 1

print(f"总抓取: {len(movies)}")

genre_buckets = {}
country_buckets = {}
year_buckets = {}

for m in movies:
    rating = float(m.get("rating") or 0) or None
    g = m.get("genre") or ""
    for tk in [x.strip() for x in g.replace("/", ",").split(",") if x.strip()]:
        if is_genre(tk):
            b = genre_buckets.setdefault(tk, [0, 0.0, 0])
            b[0] += 1
            if rating is not None:
                b[1] += rating; b[2] += 1
    c = m.get("country") or ""
    parts = split_countries(c)
    whole = " / ".join(parts)
    for label in [whole] + parts:
        if label in COUNTRIES:
            b = country_buckets.setdefault(label, [0, 0.0, 0])
            b[0] += 1
            if rating is not None:
                b[1] += rating; b[2] += 1
    y = m.get("year")
    if isinstance(y, int) and 1900 <= y <= 2030:
        b = year_buckets.setdefault(y, [0, 0.0, 0])
        b[0] += 1
        if rating is not None:
            b[1] += rating; b[2] += 1

sql_lines = [
    "-- 由 scripts/rebuild_aggregates_offline.py 自动生成",
    "-- 从 /api/movies/paged 拉全量清洗后,truncate-then-insert 三个聚合表",
    "SET NAMES utf8mb4;",
    "START TRANSACTION;",
    "DELETE FROM agg_genre;",
    "DELETE FROM agg_country;",
    "DELETE FROM agg_year;",
]

def esc(s):
    return str(s).replace("'", "''")

for k, (c, s, n) in sorted(genre_buckets.items(), key=lambda x: -x[1][0]):
    avg = round(s/n, 2) if n else 0
    sql_lines.append(f"INSERT INTO agg_genre (genre, movie_count, avg_rating) VALUES ('{esc(k)}', {c}, {avg});")

for k, (c, s, n) in sorted(country_buckets.items(), key=lambda x: -x[1][0]):
    avg = round(s/n, 2) if n else 0
    sql_lines.append(f"INSERT INTO agg_country (country, movie_count, avg_rating) VALUES ('{esc(k)}', {c}, {avg});")

for y in sorted(year_buckets.keys()):
    c, s, n = year_buckets[y]
    avg = round(s/n, 2) if n else 0
    sql_lines.append(f"INSERT INTO agg_year (year, movie_count, avg_rating) VALUES ({y}, {c}, {avg});")

sql_lines.append("COMMIT;")
out_sql = OUT / "06-rebuild-aggregates.sql"
out_sql.write_text("\n".join(sql_lines), encoding="utf-8")

report = [
    "=" * 64,
    "聚合表重写报告(离线版)",
    "=" * 64,
    f"扫描电影数:        {len(movies)}",
    f"agg_genre 桶数:    {len(genre_buckets)}",
    f"agg_country 桶数:  {len(country_buckets)}",
    f"agg_year 桶数:     {len(year_buckets)}",
    f"输出 SQL:          scripts/seed-data/06-rebuild-aggregates.sql",
]
out_report = OUT / "06-rebuild-aggregates-report.txt"
out_report.write_text("\n".join(report), encoding="utf-8")
print("\n".join(report))