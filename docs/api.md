# 接口文档（API）

后端 Flask 暴露的 7 个 GET 接口，前端 Vue 通过 `/api/*` 调用（开发时 Vite 反代，生产时 Nginx 反代）。

公共返回结构：

```json
{ "data": <业务载荷> }
```

错误响应：

```json
{ "error": "not_found", "message": "movie not found" }
```

---

## 1. `GET /api/health`

健康检查，含 DB 探活。

**响应**：

| 字段 | 类型 | 说明 |
|---|---|---|
| status | string | `"ok"` 或 `"degraded"` |
| db | boolean | true 表示数据库连得通 |

---

## 2. `GET /api/dashboard/summary`

大屏总览统计。

**响应**：

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | 影片总数 |
| avg_rating | number 或 null | 平均评分 |
| distinct_genre | integer | 类型维度去重数 |
| distinct_country | integer | 地区维度去重数 |
| distinct_year | integer | 年份维度去重数 |

---

## 3. `GET /api/movies/count_by_genre`

按类型分布（来自 `agg_genre` 表，由 Spark ETL 写入）。

**响应**：

```json
{
  "data": [
    { "name": "剧情", "count": 1024, "avg_rating": 8.21 },
    { "name": "喜剧", "count": 612,  "avg_rating": 7.65 }
  ]
}
```

数组按 `count` 倒序。

---

## 4. `GET /api/movies/count_by_country`

按地区分布（来自 `agg_country`）。

**响应**：

```json
{
  "data": [
    { "name": "美国", "count": 820, "avg_rating": 8.04 },
    { "name": "日本", "count": 312, "avg_rating": 8.27 }
  ]
}
```

数组按 `count` 倒序。

---

## 5. `GET /api/movies/count_by_year`

按年份分布（来自 `agg_year`）。

**响应**：

```json
{
  "data": [
    { "year": 1994, "count": 36, "avg_rating": 8.21 },
    { "year": 1995, "count": 41, "avg_rating": 7.92 }
  ]
}
```

数组按 `year` 升序。

---

## 6. `GET /api/movies/top_rated?limit=N`

高分榜 TOP N。

**Query 参数**：

| 参数 | 默认 | 范围 | 说明 |
|---|---|---|---|
| limit | 50 | 1-200 | 返回条数上限 |

**响应**：

```json
{
  "data": [
    {
      "rank": 1,
      "douban_id": "1292052",
      "title": "肖申克的救赎",
      "year": 1994,
      "rating": 9.7,
      "director": "弗兰克·德拉邦特 Frank Darabont",
      "country": "美国",
      "genre": "犯罪 剧情"
    }
  ]
}
```

每条字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| rank | integer | 1-based 排名 |
| douban_id | string | 豆瓣 ID |
| title | string | 片名 |
| year | integer 或 null | 年份 |
| rating | number 或 null | 评分（0-10） |
| rating_count | integer 或 null | 评分人数 |
| director | string | 导演 |
| actors | string | 主演 |
| country | string | 地区 |
| genre | string | 类型 |
| summary | string | 简介（来自详情页，列表可能为空） |
| poster_url | string | 海报 URL |

排序：`rating desc nulls last, rating_count desc nulls last`。

---

## 7. `GET /api/movies/<douban_id>`

影片详情，单条。

**路径参数**：`douban_id`（豆瓣 ID 字符串）。

**响应 200**：

```json
{
  "data": {
    "rank": null,
    "douban_id": "1292052",
    "title": "肖申克的救赎",
    "director": "弗兰克·德拉邦特 Frank Darabont",
    "actors": "蒂姆·罗宾斯 Tim Robbins / ...",
    "genre": "犯罪 剧情",
    "country": "美国",
    "year": 1994,
    "rating": 9.7,
    "rating_count": 3302299,
    "summary": "...",
    "poster_url": "https://..."
  }
}
```

**404**：

```json
{ "error": "not_found", "message": "movie not found" }
```

---

## 数据来源与责任分工

| 接口 | 数据来源表 | 写入方 |
|---|---|---|
| `/api/health` | `SELECT 1` | 系统自带 |
| `/api/dashboard/summary` | `movie` | Spark ETL 写 `movie` 主表 |
| `/api/movies/count_by_genre` | `agg_genre` | Spark ETL 聚合 |
| `/api/movies/count_by_country` | `agg_country` | Spark ETL 聚合 |
| `/api/movies/count_by_year` | `agg_year` | Spark ETL 聚合 |
| `/api/movies/top_rated` | `movie` | Spark ETL 写 `movie` 主表 |
| `/api/movies/<id>` | `movie` | Spark ETL 写 `movie` 主表 |

`docs/schema.sql` 是表结构；`spark/etl/writer.py` 是写入实现。

---

## CORS

后端启用 `Flask-Cors`，`/api/*` 默认 `origins=*`，生产建议改为具体前端域名。