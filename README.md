# 豆瓣电影大数据分析平台

基于豆瓣电影公开页面构建的端到端数据工程 Demo：
**爬虫 → 数据存储 → ETL 聚合 → MySQL → Flask REST API → Vue 3 大屏 → Nginx 反代**。

---

## 技术栈

| 层 | 技术 |
|---|---|
| 数据采集 | Python 3 + Requests + BeautifulSoup4 |
| 分布式存储 | Hadoop HDFS（伪分布式，单机可绕开） |
| 分布式计算 | Apache Spark + PySpark Standalone / 本地 pymysql |
| 关系数据库 | MySQL 8.0（docker-compose 容器或本地安装） |
| 后端服务 | Flask 2 + SQLAlchemy + Gunicorn（容器内） |
| 前端展示 | Vue 3 + Vue Router + Pinia + ECharts 5（Vite 构建） |
| 部署运维 | Docker Compose 一键起 MySQL + backend + nginx |
| 反向代理 | Nginx Alpine 镜像，反代 /api 到 Flask 容器 |

---

## 项目结构

```
douban-bigdata/
├── crawler/                 # 数据采集层（Python 爬虫）
├── hdfs/                    # HDFS 上传脚本（可选）
├── spark/                   # PySpark 清洗与聚合 / 或 pymysql 本地脚本
├── backend/                 # Flask REST API（routes/services 分层）
│   ├── routes/              #    URL 路由（dashboard / movies）
│   └── services/            #    业务逻辑与 SQL 聚合
├── frontend/                # Vue 3 单页前端
│   ├── src/views/           #    Dashboard / Top / Movie / Search / Country / Genre / Year
│   ├── src/stores/          #    Pinia stores（dashboard / movies / search）
│   └── src/api/             #    axios 封装 + interceptor 自动解包
├── deploy/                  # Nginx 生产配置（douban.conf）
├── scripts/                 # 脚本：seed-data / generate_seed_data / verify_local / init-mysql
├── docs/                    # schema.sql、api.md、migrations/02_indexes.sql
├── docker-compose.yml       # 主入口：mysql + backend + nginx
└── README.md
```

---

## 快速开始（推荐：Docker Compose）

### 1. 环境要求

- Docker Engine 20.10+（Windows 上用 Docker Desktop）
- Node.js 18+（用于 `npm run build` 构建前端）
- Python 3.10+（仅在本机需要跑爬虫 / 生成 seed 数据时用到）

### 2. 构建前端

Nginx 直接挂载 `frontend/dist/`，所以**构建前端产物是必做的**：

```bash
cd frontend
npm install
npm run build
# 产物: frontend/dist/{index.html, assets/*}
```

### 3. 启动全部服务

```bash
cd ..           # 回到项目根目录
docker compose up -d --build
```

会依次启动：

| 容器 | 作用 | 端口 |
|---|---|---|
| `douban-mysql` | MySQL 8.0，首次启动自动注入 schema.sql + seed 数据 | `3306`（本机映射 `3306`，可改 `docker-compose.yml`） |
| `douban-backend` | Flask + Gunicorn，反代 /api 请求的上游 | 容器内 `5000` |
| `douban-nginx` | 静态文件（`/usr/share/nginx/html` ← 挂载 `./frontend/dist`）+ /api 反代 | `8080`（本机映射） |

### 4. 打开页面

浏览器访问：**http://localhost:8080**

- **首页 / Dashboard**：指标卡 + 11 个图表区块（类型/地区/年代/评分/片长分布 + 导演榜/语言榜/高分榜/年代汇总）
- **/top**：榜单页（筛选类型/地区 + 分页 + 排序）
- **/movie/:id**：详情页（海报、评分、相关推荐、上下部导航）
- **/search?q=关键字**：片名/导演/演员模糊搜索
- **/country / /genre / /year**：维度视图（同大屏对应区块的独立页）

### 5. 停止 / 清理

```bash
docker compose stop           # 暂停（保留容器与数据卷）
docker compose down           # 删除容器（数据卷仍在）
docker compose down -v        # 连 MySQL 数据一起删掉（⚠️ 危险）
```

---

## 快速开始（本地裸跑，不开 Docker）

适用于想直接改代码即时看到效果的场景：

```bash
# 1. MySQL：本机已装 8.0，先注入 schema
mysql -uroot -p < docs/schema.sql
#    再灌种子数据（25 条）
python scripts/generate_seed_data.py   # 生成 INSERT
#    或直接跑 seed-data 下的 .sql（如果有）
mysql -uroot -p douban < scripts/seed-data/10-movie.sql

# 2. 应用索引迁移（首次或新增索引时）
mysql -uroot -p douban < docs/migrations/02_indexes.sql

# 3. 启动后端
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows Git Bash: . .venv/Scripts/activate
pip install -r requirements.txt
python app.py                # 监听 0.0.0.0:5000

# 4. 启动前端 dev server（另开一个终端）
cd frontend
npm install
npm run dev                  # Vite 默认 http://localhost:5173

# 5. 或者构建后用 nginx 当生产态（见上一节）
```

---

## 后端 API 一览

所有接口前缀 `/api`，GET 无需鉴权（除非配置了 `DOUBAN_API_KEY` 环境变量）。

### 健康检查

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 返回 `{"status":"ok"}`，用来探测容器是否就绪 |

### 大屏聚合

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/dashboard/summary` | 核心指标卡：总条数、平均评分、各维度去重计数 |
| GET | `/api/dashboard/summary_extended` | 扩展版：最高分、总评价数、TOP200 计数等 |

### 电影列表 / 分页 / 搜索

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/movies/top_rated?limit=50` | 按评分+评价数排序的 TOP 列表 |
| GET | `/api/movies/paged?page=1&size=20&sort=rating&order=desc&genre=剧情&country=美国&year_from=2000&year_to=2020` | 带筛选/排序的分页查询 |
| GET | `/api/movies/search?q=肖申克&limit=30` | 标题/导演/演员模糊搜索 |

### 电影详情 / 相关

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/movies/{douban_id}` | 单条详情（title/year/genre/country/director/actors/rating/rating_count/poster_url 等） |
| GET | `/api/movies/{douban_id}/related?limit=12` | 同类型推荐（排除自身） |
| GET | `/api/movies/{douban_id}/neighbors` | 按榜单排序的上一部 / 下一部 |

### 维度聚合（图表用）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/movies/count_by_genre` | 按类型条数统计 |
| GET | `/api/movies/count_by_country` | 按地区条数统计 |
| GET | `/api/movies/count_by_year` | 按年份条数统计 |
| GET | `/api/movies/count_by_avg?dim=genre&limit=10` | 双轴：条数 + 平均评分（dim ∈ genre/country/year） |
| GET | `/api/movies/count_by_director?limit=10` | 按导演聚合（含平均评分） |
| GET | `/api/movies/count_by_language?limit=10` | 按语言聚合（用 `/` 分隔字段拆条） |
| GET | `/api/movies/count_by_decade?limit=20` | 按年代（10 年一组）聚合 |
| GET | `/api/movies/rating_distribution` | 评分直方图（4 分桶：<7 / 7–8 / 8–9 / 9+） |
| GET | `/api/movies/runtime_distribution` | 片长直方图（<90 / 90–120 / 120–150 / 150+ 分钟） |

响应示例：

```json
// GET /api/dashboard/summary
{
  "data": {
    "total": 25,
    "avg_rating": 9.3,
    "distinct_genre": 14,
    "distinct_country": 8,
    "distinct_year": 12
  }
}

// GET /api/movies/count_by_avg?dim=genre&limit=5
{
  "data": [
    { "name": "剧情", "count": 21, "avg_rating": 9.3 },
    { "name": "爱情", "count":  8, "avg_rating": 9.1 },
    ...
  ]
}
```

更多接口文档请见 [docs/api.md](docs/api.md)。

---

## 数据库表与索引

### Schema

见 [docs/schema.sql](docs/schema.sql)，核心三张表：

| 表 | 用途 | 主键 |
|---|---|---|
| `movie` | 电影主表（title / year / genre / country / director / actors / rating / rating_count / poster_url / languages / runtime / runtime_minutes / summary / quote / also_know_as / imdb_id / official_sites / comment_short_count / comment_review_count / discussion_count / rating_stars / related_pics） | `id` AUTO_INCREMENT, `douban_id` UNIQUE |
| `agg_genre` | 类型聚合预计算（movie_count / avg_rating） | `id` |
| `agg_country` | 地区聚合预计算 | `id` |
| `agg_year` | 年份聚合预计算 | `id` |

### 索引

初始建表时已建：`idx_year / idx_rating / idx_country / idx_runtime` + `PRIMARY / douban_id`。

大屏扩展后新增的索引在 [docs/migrations/02_indexes.sql](docs/migrations/02_indexes.sql)：

- `idx_rating_count` — 榜单按评价数排序
- `idx_genre(genre(32))` — 类型前缀索引，模糊匹配 / 列表筛选
- `idx_country_prefix(country(32))` — 地区前缀索引
- `idx_rating_pair(rating, rating_count)` — 联合索引，榜单主力排序
- `idx_title(title(32))` — 标题前缀索引，搜索页高频使用

**手动应用索引**（如果 MySQL 已经跑起来过一次了）：

```bash
# 方式一：通过 docker exec 推送到容器
docker exec -i douban-mysql mysql -uroot -p"MYSQL_ROOT_PASSWORD" douban < docs/migrations/02_indexes.sql

# 方式二：本机 MySQL 客户端直连
mysql -h127.0.0.1 -P3306 -uroot -p douban < docs/migrations/02_indexes.sql
```

校验索引是否生效：

```sql
SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS
 WHERE TABLE_SCHEMA = 'douban' AND TABLE_NAME = 'movie'
 GROUP BY INDEX_NAME;
```

期望看到 11 个索引名：`PRIMARY / douban_id / idx_year / idx_rating / idx_country / idx_runtime / idx_rating_count / idx_genre / idx_country_prefix / idx_rating_pair / idx_title`。

---

## 数据流

```
  豆瓣公开页面
      │
      ▼
 crawler (Python, Requests + BS4)
      │ 输出 movies.jsonl
      ▼
┌────────────────────┐ 可选走 HDFS
│  hdfs/ 或本地 JSON │  ──► scripts/generate_seed_data.py 生成 INSERT SQL
└────────────────────┘          │
                                 ▼
                               MySQL (douban 库)
                                 │  movie / agg_genre / agg_country / agg_year
                                 ▼
                           Flask backend (SQLAlchemy)
                                 │  GET /api/*（13+ 接口）
                                 ▼
                         Nginx (静态 + /api 反代)
                                 │
                                 ▼
                           Vue 3 SPA（浏览器）
```

---

## 数据量说明

- **验证态**：`scripts/seed-data/10-movie.sql` 含 25 条 TOP 电影数据，够跑通整个链路
- **生产目标**：爬虫扩展抓取（按 genres / countries 标签铺开），目标 1 万+ 条
- **注意**：豆瓣对频繁请求有反爬（403 / 418），生产建议走云服务器 + 代理池 + 限速

---

## 反爬与限速

- 单请求随机 sleep 1–3 秒
- User-Agent 随机轮换（fake-useragent + 兜底池）
- 失败指数退避重试 5 次（403 / 418 / 429 / 5xx）
- 可选配置 `DOUBAN_PROXIES=http://ip1:port,http://ip2:port` 叠加代理

---

## 常见坑（避坑清单）

1. **nginx 启动后立即退出，logs 里报 `unknown directive`**  
   检查 `deploy/nginx/douban.conf` 是否有 **UTF-8 BOM**（Windows 编辑器常见），以及是否有 `proxy_valid` 这种并非 nginx 有效指令的行。可用 `file deploy/nginx/douban.conf` 或 VS Code 右下角切换为 "UTF-8"（不带 BOM）。

2. **Docker 首次 up 后 seed 数据没进来**  
   `docker-entrypoint-initdb.d/` 只在**数据目录为空**（即首次初始化）时跑 SQL。若 `mysql-data` 卷已存在，脚本不会再执行。要重灌，需 `docker compose down -v` 后再 up（⚠️ 会清空所有数据），或手动 `docker exec -i douban-mysql mysql ... < scripts/seed-data/xxx.sql`。

3. **大屏接口返回 500**  
   大概率是 `idx_rating_count / idx_rating_pair` 等新索引脚本没跑过。先 `docker compose restart mysql`，再按上面"数据库表与索引"里的方式执行 `02_indexes.sql`，然后 `docker compose up -d --build backend` 重启后端。

4. **`/movie/:id` 页面空白但接口返回 200**  
   检查前端 `views/Movie.vue` 是否正确引入了 `useMoviesStore`，且 `onMounted` 中调用了 `moviesStore.fetchRelated / fetchNeighbors`。确保 `npm run build` 后重启过 `douban-nginx` 容器。

5. **Nginx 反代 `/api/` 返回 502**  
   后端容器 `douban-backend` 可能还在等 MySQL 健康检查（最多 30s），或 compose 中 `depends_on: mysql: healthy` 配置被改乱了。等几秒后重试。

6. **Windows 上路径分隔符问题**  
   所有脚本里的路径已按 `./frontend/dist` 等相对路径写法，使用 Git Bash 或 PowerShell 都 OK；但不要把 `\` 写进 docker-compose 的 volume 路径。

---

## 开发 / 调试小贴士

- 跑后端接口冒烟：项目根目录下 `python _test_api.py`（假设后端 5000 或 nginx 8080 通）
- 后端单步调试：在 `backend/` 目录直接 `flask run --host 0.0.0.0 --port 5000 --reload`，前端 dev server 里改 `api/index.js` 的 `baseURL` 指向这个地址
- 前端改完自动热更新：`npm run dev` 下直接看效果，等 OK 再 `npm run build` 让 nginx 拿最新

---

## 后续计划（可扩展方向）

- [ ] 扩展爬虫：按 genres / countries 维度抓 1 万+ 条
- [ ] Spark ETL `dim_*` 维度表实现（星型模型）
- [ ] `/api/dashboard/*` 加一层 nginx proxy_cache（30s），减少 MySQL 压力
- [ ] 后端接口鉴权 + 限流（已有 `DOUBAN_API_KEY` / `DOUBAN_RATE_LIMIT` 变量位，但需要补实现）
- [ ] 大屏里 `vue-echarts` 替换裸手写 ECharts，便于维护
- [ ] CI：lint / build / 接口冒烟，PR 自动跑
- [ ] 架构图与完整数据字典文档

---

## 数据更新（补抓详情页）

当 movie 表中部分电影的详情页字段（`summary` / `runtime_minutes` / `languages` /
`imdb_id` 等）缺失时，可以用以下流程补抓，**无需重建表，后端无感刷新**：

### 一次性补抓流程

```bash
# 1. 补抓详情字段写到 data/raw/movies.jsonl（约 30-50 分钟）
python scripts/enrich_all_details.py

# 2. Dry-run：看 ETL 会写什么，但不真写库
bash scripts/update_db.sh

# 3. 写库前先备份（推荐）
bash scripts/update_db.sh --backup

# 4. 确认后真正写库（UPSERT 模式，幂等）
bash scripts/update_db.sh --write
```

### 工作原理

- `enrich_all_details.py` 从 MySQL `movie` 表读全部 `douban_id`，
  对比已有 `data/raw/movies.jsonl` 中的记录，**只重抓详情字段不全的**。
- 抓取结果合并写回 `data/raw/movies.jsonl`。
- `update_db.sh` 触发 Docker 中的 Spark ETL（`etl` profile），
  走 `INSERT ... ON DUPLICATE KEY UPDATE` 写回 MySQL，**保留 `created_at`、刷新其他字段**。

### 高级用法

```bash
# 强制全量重抓（忽略 JSONL 已有记录）
python scripts/enrich_all_details.py --force

# 用代理（需要 proxies.txt 有可用代理）
python scripts/enrich_all_details.py --proxy-file crawler/proxies.txt

# 自定义 ID 列表（每行一个 douban_id）
python scripts/enrich_all_details.py --ids-file data/raw/my_ids.txt

# 只爬不合并写回 JSONL（调试用）
python scripts/enrich_all_details.py --no-write
```

### 设计原则

- **幂等**：可重复运行，结果一致
- **断点**：JSONL 已存在的 ID 不会被覆盖（除非 `--force`）
- **跳过阈值**：4 个关键字段（`summary`/`runtime_minutes`/`languages`/`imdb_id`）
  任一为空即视为未抓详
- **节流**：单 IP 默认 6-15 秒/条，配合 `curl_cffi` 模拟浏览器 TLS 指纹

### 云端更新

代码推送到 GitHub 后，在云服务器上：

```bash
cd /opt/douban-bigdata
git pull
docker compose up -d --build          # 代码有变更时
bash scripts/update_db.sh --write     # 触发 ETL 写库
```

