# -*- coding: utf-8 -*-
"""高级视图所需的后端接口。
- /api/sankey/flow         三列能量流（类型→国家→年代）
- /api/treemap/genre_country 类型 × 国家 矩阵
- /api/calendar/monthly    月度发行热力
- /api/network/collaborations 演员/导演合作网络
- /api/map/countries       国家中英文与片数,供前端对世界地图
"""
from __future__ import annotations
import json
import re
from collections import defaultdict, Counter

from flask import Blueprint, jsonify, request
from sqlalchemy import func, select

from db import get_session
from models import Movie

bp = Blueprint("viz", __name__, url_prefix="/api")


# ===== 公共:字段拆分 =====
def _split_multi(raw, sep_pattern=r"[,/]"):
    if not raw:
        return []
    out = []
    for tok in re.split(sep_pattern, str(raw)):
        s = tok.strip()
        if s:
            out.append(s)
    return out


# ===== 国家中英映射(扩展覆盖 TOP250 实际国家) =====
COUNTRY_EN = {
    "美国": "United States", "英国": "United Kingdom", "日本": "Japan",
    "中国大陆": "China", "中国香港": "Hong Kong", "中国台湾": "Taiwan",
    "韩国": "South Korea", "法国": "France", "德国": "Germany",
    "意大利": "Italy", "西班牙": "Spain", "加拿大": "Canada",
    "澳大利亚": "Australia", "印度": "India", "泰国": "Thailand",
    "俄罗斯": "Russia", "新西兰": "New Zealand", "巴西": "Brazil",
    "瑞典": "Sweden", "丹麦": "Denmark", "瑞士": "Switzerland",
    "波兰": "Poland", "奥地利": "Austria", "阿根廷": "Argentina",
    "墨西哥": "Mexico", "南非": "South Africa", "荷兰": "Netherlands",
    "希腊": "Greece", "捷克": "Czech Rep.", "匈牙利": "Hungary",
    "爱尔兰": "Ireland", "比利时": "Belgium", "黎巴嫩": "Lebanon",
    "伊朗": "Iran", "土耳其": "Turkey", "以色列": "Israel",
    "新加坡": "Singapore", "马来西亚": "Malaysia", "越南": "Vietnam",
    "印度尼西亚": "Indonesia", "菲律宾": "Philippines", "乌克兰": "Ukraine",
    "罗马尼亚": "Romania", "芬兰": "Finland", "挪威": "Norway",
    "葡萄牙": "Portugal", "智利": "Chile", "古巴": "Cuba",
    "摩洛哥": "Morocco", "突尼斯": "Tunisia", "约旦": "Jordan",
    "卡塔尔": "Qatar", "阿联酋": "United Arab Emirates",
    "沙特阿拉伯": "Saudi Arabia", "塞浦路斯": "Cyprus", "马耳他": "Malta",
    "冰岛": "Iceland", "卢森堡": "Luxembourg",
    "爱沙尼亚": "Estonia", "拉脱维亚": "Latvia", "立陶宛": "Lithuania",
    "斯洛文尼亚": "Slovenia", "斯洛伐克": "Slovakia",
    "塞尔维亚": "Serbia", "克罗地亚": "Croatia", "保加利亚": "Bulgaria",
    "阿尔巴尼亚": "Albania", "波黑": "Bosnia and Herzegovina",
    "白俄罗斯": "Belarus", "亚美尼亚": "Armenia",
    "阿塞拜疆": "Azerbaijan", "格鲁吉亚": "Georgia",
    "哈萨克斯坦": "Kazakhstan", "阿富汗": "Afghanistan",
    "朝鲜": "North Korea", "不丹": "Bhutan", "马尔代夫": "Maldives",
    "孟加拉国": "Bangladesh", "尼泊尔": "Nepal", "斯里兰卡": "Sri Lanka",
    "缅甸": "Myanmar", "柬埔寨": "Cambodia", "老挝": "Laos",
    "蒙古": "Mongolia", "巴基斯坦": "Pakistan",
    "巴拿马": "Panama", "哥斯达黎加": "Costa Rica",
    "洪都拉斯": "Honduras", "萨尔瓦多": "El Salvador",
    "危地马拉": "Guatemala", "海地": "Haiti",
    "多米尼加": "Dominican Rep.", "牙买加": "Jamaica",
    "特立尼达和多巴哥": "Trinidad and Tobago",
}


def _decade(year):
    if not isinstance(year, int):
        return None
    if year < 1900 or year > 2030:
        return None
    return (year // 10) * 10


@bp.get("/sankey/flow")
def sankey_flow():
    """类型 → 国家 → 年代 三列链路,流量 = 引用片数(每部片在每个类型/国家桶里加 1)"""
    top = request.args.get("top", default="6,5,5")
    try:
        g_top, c_top, d_top = [int(x) for x in top.split(",")]
    except ValueError:
        g_top, c_top, d_top = 6, 5, 5
    g_top = max(2, min(g_top, 20))
    c_top = max(2, min(c_top, 20))
    d_top = max(2, min(d_top, 12))

    s = get_session()
    try:
        rows = s.execute(select(Movie.genre, Movie.country, Movie.year, Movie.title)).all()
    finally:
        s.close()

    # 过滤类型桶:去除被 ETL 串进来的国家/年份
    country_zh = set(COUNTRY_EN.keys())
    year_re = re.compile(r"^\d{4}(\([^)]+\))?$")

    def is_genre(name):
        if not name:
            return False
        s = name.strip()
        if not s or len(s) > 12:
            return False
        if s in country_zh or s in COUNTRY_EN:
            return False
        if year_re.match(s):
            return False
        return True

    g_count = Counter()
    c_count = Counter()
    d_count = Counter()

    edge_gc = defaultdict(int)
    edge_cd = defaultdict(int)

    # 棣栭樁娈★細鍏ㄩ噺缁熻€煎悇缁村害鍑虹幇娆℃暟锛堜笉鍋氳繃婊わ紝閬垮厡缁存哺鎵撴柀锛?    for genre, country, year, _title in rows:
        gens = [g for g in _split_multi(genre) if is_genre(g)] if genre else []
        cns = _split_multi(country) if country else []
        decade = _decade(int(year)) if year is not None else None  # int or None

        # 鍘婚噸锛屾繚璇変竴閮ㄧ墖鍦ㄥ悓绫诲瀷/鍥藉鍙 1
        for g in dict.fromkeys(gens):
            g_count[g] += 1
        for c in dict.fromkeys(cns):
            c_count[c] += 1
        if decade is not None:
            d_count[decade] += 1

        if not gens or not cns or decade is None:
            continue

        # 鐢绘帺鈥攓_c 杈癸細鏁版嵁澶氬氭墜闆圭殑鐢绘帺 (绫诲瀷 鈥?鍥藉) 锛屾瘡闈犻攢 1
        for g in dict.fromkeys(gens):
            for c in dict.fromkeys(cns):
                edge_gc[(g, c)] += 1
        for c in dict.fromkeys(cns):
            edge_cd[(c, decade)] += 1

    # 绗簩闃舵锛氬嚭 top 闃堝€硷紝涓€缁达紝杈搁兘绮楁暣涓?str
    g_top_names = [name for name, _ in g_count.most_common(g_top)]
    c_top_names = [name for name, _ in c_count.most_common(c_top)]
    d_top_names = [str(d) for d, _ in d_count.most_common(d_top)]
    top_g = set(g_top_names)
    top_c = set(c_top_names)
    top_d = set(d_top_names)

    # 绗笁闃舵锛氭瀯閫犺妭鐐逛笌閾捐矾锛屽叏閮ㄥ悕绉颁綔 str锛岄伩鍏?ECharts Sankey 鈥淭arget node not found鈥?	int vs str)
    nodes = []
    for n in g_top_names:
        nodes.append({"name": str(n), "depth": 0, "itemStyle": {"color": "#38bdf8"}})
    for n in c_top_names:
        nodes.append({"name": str(n), "depth": 1, "itemStyle": {"color": "#f59e0b"}})
    for n in d_top_names:
        nodes.append({"name": n, "depth": 2, "itemStyle": {"color": "#a78bfa"}})

    links = []
    for (g, c), v in sorted(edge_gc.items(), key=lambda x: -x[1]):
        if g in top_g and c in top_c:
            links.append({"source": str(g), "target": str(c), "value": int(v)})
    for (c, d), v in sorted(edge_cd.items(), key=lambda x: -x[1]):
        if c in top_c and str(d) in top_d:
            links.append({"source": str(c), "target": str(d), "value": int(v)})

    return jsonify(data={"nodes": nodes, "links": links})

@bp.get("/treemap/genre-country")
def treemap_genre_country():
    """类型 × 国家 矩阵:每个 (类型, 国家) 桶的片数(数组格式)"""
    s = get_session()
    try:
        rows = s.execute(select(Movie.genre, Movie.country)).all()
    finally:
        s.close()

    counter = Counter()
    country_zh = set(COUNTRY_EN.keys())
    year_re = re.compile(r"^\d{4}(\([^)]+\))?$")

    for genre, country in rows:
        gens = _split_multi(genre) if genre else []
        gens = [g for g in gens if g and g.strip() and g.strip() not in country_zh and not year_re.match(g.strip()) and len(g.strip()) <= 12]
        cns = _split_multi(country) if country else []
        cns = [c for c in cns if c in country_zh]
        if not gens or not cns:
            continue
        for g in dict.fromkeys(gens):
            for c in dict.fromkeys(cns):
                counter[(g, c)] += 1

    items = []
    for (g, c), v in counter.items():
        if v >= 1:
            items.append({"name": f"{g} · {c}", "genre": g, "country": c, "value": v})
    items.sort(key=lambda x: -x["value"])
    return jsonify(data=items[:60])


@bp.get("/calendar/monthly")
def calendar_monthly():
    """取 year 范围里每月的上榜片数,数据格式 [date, value]"""
    year = request.args.get("year", default=None, type=int)
    s = get_session()
    try:
        if year:
            rows = s.execute(select(Movie.release_date, Movie.year)).all()
        else:
            rows = s.execute(select(Movie.release_date, Movie.year)).all()
    finally:
        s.close()

    pat = re.compile(r"(19|20)\d{2}[-/.](\d{1,2})")
    counter = defaultdict(int)

    for rd, yr in rows:
        if not rd:
            continue
        m = pat.search(str(rd))
        if not m:
            continue
        y = int(m.group(0).split("-")[0].split("/")[0].split(".")[0])
        mo = int(m.group(2))
        if year and y != year:
            continue
        key = f"{y:04d}-{mo:02d}-01"
        counter[key] += 1

    items = [{"date": k, "value": v} for k, v in sorted(counter.items())]
    years = sorted({int(k[:4]) for k in counter.keys()})
    return jsonify(data={"points": items, "years": years})


@bp.get("/network/collaborations")
def network_collaborations():
    """演员/导演合作网络:节点=人,边=共同参演的电影数(过滤仅 1 部合作的噪声)"""
    type_ = request.args.get("type", default="director")  # director|actor|both
    limit = request.args.get("limit", default=40, type=int)

    s = get_session()
    try:
        rows = s.execute(select(Movie.director, Movie.actors, Movie.title, Movie.douban_id)).all()
    finally:
        s.close()

    def split_people(s):
        if not s:
            return []
        # 中文片名常见用' / '或'/'
        parts = re.split(r"\s*[/、]\s*", str(s))
        return [p.strip() for p in parts if p and p.strip()]

    nodes = Counter()
    edges = defaultdict(int)
    movie_count_by_node = Counter()

    for director, actors, _title, _did in rows:
        if type_ == "director":
            people = split_people(director)
        elif type_ == "actor":
            people = split_people(actors)
        else:
            people = list(dict.fromkeys(split_people(director) + split_people(actors)))
        people = [p for p in people if p]
        if not people:
            continue
        for p in people:
            nodes[p] += 1
            movie_count_by_node[p] += 1
        for i in range(len(people)):
            for j in range(i + 1, len(people)):
                a, b = people[i], people[j]
                if a > b:
                    a, b = b, a
                edges[(a, b)] += 1

    # 取边权 >= 1 的前 limit 条
    sorted_edges = sorted(edges.items(), key=lambda x: -x[1])[:limit]
    node_set = set()
    for (a, b), _ in sorted_edges:
        node_set.add(a)
        node_set.add(b)

    out_nodes = []
    for name in node_set:
        out_nodes.append({
            "name": name,
            "symbolSize": 14 + min(40, movie_count_by_node[name] * 2),
            "value": movie_count_by_node[name],
        })
    out_links = [
        {"source": a, "target": b, "value": v}
        for (a, b), v in sorted_edges if v >= 1
    ]

    return jsonify(data={"nodes": out_nodes, "links": out_links, "type": type_})


@bp.get("/map/countries")
def map_countries():
    """国家分布(英文名 + 中文名 + 片数 + 平均分)"""
    s = get_session()
    try:
        rows = s.execute(select(Movie.country, Movie.rating)).all()
    finally:
        s.close()

    counter = Counter()
    rating_sum = defaultdict(float)
    rating_n = defaultdict(int)
    country_zh = set(COUNTRY_EN.keys())

    for country, rating in rows:
        parts = _split_multi(country) if country else []
        for c in parts:
            if c in country_zh:
                counter[c] += 1
                if rating is not None:
                    rating_sum[c] += float(rating)
                    rating_n[c] += 1

    items = []
    for name, count in sorted(counter.items(), key=lambda x: -x[1]):
        en = COUNTRY_EN.get(name, name)
        avg = round(rating_sum[name] / rating_n[name], 2) if rating_n[name] else 0
        items.append({
            "name_zh": name,
            "name_en": en,
            "count": count,
            "avg_rating": avg,
        })
    return jsonify(data=items)