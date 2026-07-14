# 接口文档（API）

后端 Flask 暴露的全部 REST 接口，前端 Vue 通过 `/api/*` 调用（开发时 Vite 反代，生产时 Nginx 反代）。
鉴权为可选项：`DOUBAN_API_KEY` 留空则关闭鉴权；填写则所有 `require_api_key` 装饰的接口强制要求 `X-API-Key` 请求头。

## 通用约定

**成功响应**：

```json
{ "data": <业务载荷> }
```

**错误响应**：

```json
{ "error": "not_found", "message": "movie not found" }
```

| 错误码 | 错误键 | 触发场景 |
|---|---|---|
| 400 | — | `/img-proxy` 缺 `url` 或非 http(s) / 域名不在白名单 |
| 401 | `unauthorized` | 鉴权开启但 `X-API-Key` 缺失或错误 |
| 404 | `not_found` | 资源不存在（如电影 ID） |
| 413 | — | `/img-proxy` 上游图片 > 10 MB |
| 429 | `rate_limited` | 触发 `flask-limiter` 限流（默认 60/min/IP） |
| 500 | `server_error` | 未捕获异常 |
| 502 | — | `/img-proxy` 上游不可达 |

**鉴权**：除 `GET /api/health` 外，所有业务接口均挂 `@require_api_key`。
- `DOUBAN_API_KEY` 为空 → 关闭鉴权，放行
- `DOUBAN_API_KEY` 非空 → 必须请求头 `X-API-Key: <key>`，否则 401

**限流**：`flask-limiter`，默认 `60/minute` 按 IP。可通过环境变量 `DOUBAN_RATE_LIMIT` 覆盖（如 `120/minute`）。

**CORS**：`/api/*` 默认 `origins=*`（开发友好）；生产建议收紧为前端域名。
---

## 1. `GET /api/health`

健康检查，含 DB 连通性。**不挂鉴权**。

**响应**

| 字段 | 类型 | 说明 |
|---|---|---|
| status | string | `"ok"` 或 `"degraded"` |
| db | boolean | true 表示数据库连接正常 |

---

## 2. `GET /api/dashboard/summary`

大屏核心指标（5 项 KPI）。直接来自 `movie` 主表实时聚合。

**响应**

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | 影片总数 |
| avg_rating | number \| null | 平均评分 |
| distinct_genre | integer | 类型维度去重数 |
| distinct_country | integer | 地区维度去重数 |
| distinct_year | integer | 年代维度去重数 |

---

## 3. `GET /api/dashboard/summary_extended`

大屏扩展指标，给大屏 KPI 卡 / 头部概览用。

**响应**

| 字段 | 类型 | 说明 |
|---|---|---|
| total | integer | 影片总数 |
| avg_rating | number \| null | 平均评分 |
| max_rating | number \| null | 最高评分 |
| avg_rating_count | integer \| null | 平均评价人数 |
| top_rating_count_title | string \| null | 评价人数最多的影片标题 |
| top_rating_count | integer \| null | 上述影片的评价人数 |
| distinct_year | integer | 年代去重数 |
| distinct_genre | integer | 类型去重数 |
| distinct_country | integer | 地区去重数 |

> 注意：本接口响应**没有 `data` 包装**（service 直接返回 dict，路由 `jsonify(service.summary_extended())`），与第 2 节一致。

---

## 4. `GET /api/movies/count_by_genre`

按类型分布（来自 `agg_genre` 聚合表，Spark ETL 写入）。

**响应**

```json
{
  "data": [
    { "name": "剧情", "count": 1024, "avg_rating": 8.21 },
    { "name": "喜剧", "count": 612,  "avg_rating": 7.65 }
  ]
}
```

数组按 `count` 降序。

---

## 5. `GET /api/movies/count_by_country`

按地区分布（来自 `agg_country`）。

```json
{
  "data": [
    { "name": "美国", "count": 820, "avg_rating": 8.04 },
    { "name": "日本", "count": 312, "avg_rating": 8.27 }
  ]
}
```

按 `count` 降序。

---

## 6. `GET /api/movies/count_by_year`

按年份分布（来自 `agg_year`）。

```json
{
  "data": [
    { "year": 1994, "count": 36, "avg_rating": 8.21 },
    { "year": 1995, "count": 41, "avg_rating": 7.92 }
  ]
}
```

按 `year` 升序。
---

## 7. `GET /api/movies/count_by_avg`

双轴图数据：每个维度下 top N + avg_rating，用于双柱复合图。

**Query 参数**

| 参数 | 默认 | 范围 | 说明 |
|---|---|---|---|
| dim | `genre` | `genre` \| `country` \| `year` | 维度 |
| limit | `10` | 1-50 | 返回条数上限 |

**响应**（以 `dim=genre` 为例）

```json
{
  "data": [
    { "name": "剧情", "count": 1024, "avg_rating": 8.21 }
  ]
}
```

> 当 `dim=year` 时，`name` 为 integer 年份；当 `dim=genre/country` 时为字符串。按该维度的 `movie_count` 降序。

---

## 8. `GET /api/movies/count_by_director`

按导演聚合（SQL 内拆分 `director` 列的 `/` 分隔项）。

**Query 参数**

| 参数 | 默认 | 范围 | 说明 |
|---|---|---|---|
| limit | `10` | 1-50 | 返回条数上限 |

**响应**

```json
{
  "data": [
    { "name": "克里斯托弗·诺兰", "count": 8, "avg_rating": 8.92 }
  ]
}
```

按 `count` 降序。

---

## 9. `GET /api/movies/count_by_language`

按语言聚合（拆分 `languages` 列的 `/` 分隔项）。

**Query 参数**

| 参数 | 默认 | 范围 |
|---|---|---|
| limit | `10` | 1-50 |

**响应**：同 `count_by_director`，`name` 为语言名。

---

## 10. `GET /api/movies/count_by_decade`

按年代桶聚合（`year // 10 * 10`）。

**Query 参数**

| 参数 | 默认 | 范围 |
|---|---|---|
| limit | `20` | 1-50 |

**响应**

```json
{
  "data": [
    { "name": 1990, "count": 87, "avg_rating": 8.41 },
    { "name": 2000, "count": 64, "avg_rating": 8.15 }
  ]
}
```

按 `name`（年代）升序。
---

## 11. `GET /api/movies/rating_distribution`

评分分桶（4 段），直方图 / 柱状图用。

**响应**

```json
{
  "data": [
    { "bucket": "6以下", "count": 12 },
    { "bucket": "7-8",   "count": 87 },
    { "bucket": "8-9",   "count": 121 },
    { "bucket": "9以上", "count": 30 }
  ]
}
```

分段规则：`[lo, hi)`，首段无下限、末段无上限。

---

## 12. `GET /api/movies/runtime_distribution`

片长分桶（4 段），单位分钟；`runtime_minutes` 为空的影片不计入。

**响应**

```json
{
  "data": [
    { "bucket": "<90",    "count": 18 },
    { "bucket": "90-120", "count": 96 },
    { "bucket": "120-150","count": 102 },
    { "bucket": "150+",   "count": 34 }
  ]
}
```
---

## 13. `GET /api/movies/top_rated?limit=N`

高分组榜 TOP N，按 `rating desc, rating_count desc` 排序（NULL 排到最后）。

**Query 参数**

| 参数 | 默认 | 范围 | 说明 |
|---|---|---|---|
| limit | `50` | 1-200 | 返回条数上限 |

**响应**

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

**每条字段**

| 字段 | 类型 | 说明 |
|---|---|---|
| rank | integer | 1-based 排名 |
| douban_id | string | 豆瓣 ID |
| title | string | 片名 |
| year | integer \| null | 年份 |
| rating | number \| null | 评分（0-10） |
| rating_count | integer \| null | 评价人数 |
| director | string | 导演 |
| actors | string | 主演 |
| country | string | 地区 |
| genre | string | 类型 |
| summary | string | 简介（可能为空） |
| poster_url | string | 海报 URL |
| **+扩展字段** | 仅在有值时出现 | 见下文 |

扩展字段（在详情页 / 列表接口中仅当数据库非空才返回，避免列表接口传输大量空字段）：

| 字段 | 类型 | 来源 / 说明 |
|---|---|---|
| detail_url | string | 详情页 URL（拼接或详情页抓取） |
| languages | string | 语言，多个以 `/` 分隔 |
| release_date | string | 上映时间（多地区以 `/` 分隔） |
| runtime | string | 片长原文本，如 `"142分钟"` |
| runtime_minutes | integer \| null | 数值化片长（分钟） |
| quote | string | 经典台词 / 短评 |
| better_than | string | 例 `"好于 X% 剧情片 / Y% 犯罪片"` |
| also_know_as | string | 又名 |
| imdb_id | string | IMDb ID |
| official_sites | string | 官方网站（多个以 `/` 分隔） |
| comment_short_count | integer \| null | 短评数 |
| comment_review_count | integer \| null | 长评/影评数 |
| discussion_count | integer \| null | 讨论区条数 |
| rating_stars | object \| null | 星级占比，例 `{"5": 85.0, "4": 10.0, ...}`（JSON 字符串已解析） |
| related_pics | array \| null | 详情页相关图片 URL 列表（JSON 字符串已解析） |
---

## 14. `GET /api/movies/<douban_id>`

影片详情，单条。返回字段结构与第 13 节一致（**但会包含所有扩展字段**，即 `_serialize_movie` 完整输出）。

**路径参数**

| 参数 | 说明 |
|---|---|
| douban_id | 豆瓣 ID 字符串 |

**响应 200**

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
    "poster_url": "https://...",
    "detail_url": "https://movie.douban.com/subject/1292052/",
    "languages": "英语",
    "release_date": "1994-09-10(多伦多电影节) / 1994-10-14(美国)",
    "runtime": "142分钟",
    "runtime_minutes": 142,
    "quote": "...",
    "rating_stars": { "5": 85.0, "4": 10.0, "3": 3.0, "2": 1.0, "1": 1.0 },
    "related_pics": ["https://..."]
  }
}
```

**404**

```json
{ "error": "not_found", "message": "movie not found" }
```

---

## 15. `GET /api/movies/<douban_id>/related`

相关推荐：取当前影片的第一个 `genre` 作为匹配键，按评分倒序拉 top N，**排除自身**。

**Query 参数**

| 参数 | 默认 | 范围 |
|---|---|---|
| limit | `10` | 1-20 |

**响应**：数组，每项结构同 `top_rated`（**无 `rank`**）。

空响应：当前影片不存在或 `genre` 为空 → `data: []`。

---

## 16. `GET /api/movies/<douban_id>/neighbors`

榜单上下部（详情页"上一部 / 下一部"导航）。榜单口径与 `top_rated` 一致。

**响应**

```json
{
  "data": {
    "prev": { "douban_id": "1291546", "title": "霸王别姬" },
    "next": { "douban_id": "1292720", "title": "阿甘正传" }
  }
}
```

未找到 ID 或已在边界 → 对应字段为 `null`：

```json
{ "data": { "prev": null, "next": { "douban_id": "1292720", "title": "阿甘正传" } } }
```
---

## 17. `GET /api/movies/paged`

通用分页列表，支持筛选 + 排序，给 Top / Search / Genre / Country / Year 页面用。

**Query 参数**

| 参数 | 默认 | 范围 | 说明 |
|---|---|---|---|
| page | `1` | ≥1 | 页码 |
| size | `20` | 1-100（服务层夹紧） | 每页条数 |
| sort | `rating` | `rating` \| `rating_count` \| `year` \| `title` \| `id` | 排序字段；其他值回退 `rating` |
| order | `desc` | `asc` \| `desc` | 排序方向 |
| genre | — | 字符串 | 类型模糊匹配（`LIKE %genre%`） |
| country | — | 字符串 | 地区模糊匹配 |
| year_from | — | integer | 起始年份（闭区间） |
| year_to | — | integer | 截止年份（闭区间） |

**响应**

```json
{
  "data": {
    "total": 250,
    "page": 1,
    "size": 20,
    "items": [
      { "rank": null, "douban_id": "1292052", "title": "肖申克的救赎", "rating": 9.7 }
    ]
  }
}
```

`items[]` 中每项结构同 `top_rated`（**无 `rank`**）。

---

## 18. `GET /api/movies/search`

片名 / 导演 / 演员模糊搜索，`LIKE %q%`，按 `rating desc`（NULL 排最后）。

**Query 参数**

| 参数 | 默认 | 范围 | 说明 |
|---|---|---|---|
| q | `""` | 非空 | 关键词；空字符串直接返回 `data: []` |
| limit | `20` | 1-100（服务层夹紧） | 返回条数上限 |

**响应**

```json
{
  "data": [
    { "rank": null, "douban_id": "1292052", "title": "肖申克的救赎", "rating": 9.7 }
  ]
}
```
---

## 19. `GET /img-proxy?url=<encoded>`

豆瓣图片反代。**注意路径是 `/img-proxy` 而非 `/api/img-proxy`**（Nginx 与 Flask 都挂在根路径）。
用于解决前端跨域 / 豆瓣图床防盗链问题。**不挂鉴权**，不计入 `/api/*` CORS 规则。

**Query 参数**

| 参数 | 必填 | 说明 |
|---|---|---|
| url | 是 | 完整图片 URL，必须 `http://` 或 `https://` 开头 |

**白名单域名**（请求的 host 必须命中其一或其子域）：

`doubanio.com` · `douban.com` · `img1.doubanio.com` · `img2.doubanio.com` · `img3.doubanio.com` · `img9.doubanio.com`

**响应**：原图二进制，`Content-Type` 透传上游，附带 7 天 `Cache-Control: public, max-age=604800`。

**错误**

| 状态 | 触发 |
|---|---|
| 400 | `url` 缺失 / 非 http(s) / 域名不在白名单 |
| 413 | 上游图片 > 10 MB |
| 502 | 上游不可达 |
| 透传 | 透传上游 HTTP 错误码（如 404） |

> Nginx 模式下：`/img-proxy` 直接 `proxy_pass $arg_url`，行为等效但配置不同。

---

## 数据来源与职责分工

| 接口 | 数据来源表 | 写入方 |
|---|---|---|
| `/api/health` | `SELECT 1` | 系统自带 |
| `/api/dashboard/summary` | `movie`（实时聚合） | Spark ETL 写 `movie` 主表 |
| `/api/dashboard/summary_extended` | `movie`（实时聚合） | Spark ETL 写 `movie` 主表 |
| `/api/movies/count_by_genre` | `agg_genre` | Spark ETL 聚合 |
| `/api/movies/count_by_country` | `agg_country` | Spark ETL 聚合 |
| `/api/movies/count_by_year` | `agg_year` | Spark ETL 聚合 |
| `/api/movies/count_by_avg` | `agg_genre/country/year` | Spark ETL 聚合 |
| `/api/movies/count_by_director` | `movie`（SQL 拆分 `director`） | Spark ETL 写 `movie` 主表 |
| `/api/movies/count_by_language` | `movie`（SQL 拆分 `languages`） | Spark ETL 写 `movie` 主表 |
| `/api/movies/count_by_decade` | `movie`（SQL `year//10*10`） | Spark ETL 写 `movie` 主表 |
| `/api/movies/rating_distribution` | `movie`（实时分桶） | Spark ETL 写 `movie` 主表 |
| `/api/movies/runtime_distribution` | `movie`（实时分桶） | Spark ETL 写 `movie` 主表 |
| `/api/movies/top_rated` | `movie` | Spark ETL 写 `movie` 主表 |
| `/api/movies/<id>` | `movie` | Spark ETL 写 `movie` 主表 |
| `/api/movies/<id>/related` | `movie`（同 genre） | Spark ETL 写 `movie` 主表 |
| `/api/movies/<id>/neighbors` | `movie`（按榜单序） | Spark ETL 写 `movie` 主表 |
| `/api/movies/paged` | `movie` | Spark ETL 写 `movie` 主表 |
| `/api/movies/search` | `movie` | Spark ETL 写 `movie` 主表 |

`docs/schema.sql` 是表结构，`spark/etl/writer.py` 是写入实现。

---

## CORS

后端启用 `Flask-Cors`，`/api/*` 默认 `origins=*`，生产建议改为具体前端域名。