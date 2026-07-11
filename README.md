# 豆瓣电影大数据处理平台

基于豆瓣电影公开页面构建的端到端数据工程 Demo：爬虫 → HDFS → Spark ETL → MySQL → Flask → Vue 3 → Nginx。

## 技术栈

| 层 | 技术 |
|---|---|
| 数据采集 | Python 3 + Requests + BeautifulSoup4 |
| 分布式存储 | Hadoop HDFS（伪分布式） |
| 分布式计算 | Apache Spark + PySpark Standalone |
| 关系数据库 | MySQL 8 |
| 后端服务 | Flask + Gunicorn + Nginx |
| 前端展示 | Vue 3 + Vue Router + Pinia + ECharts 5 |
| 部署运维 | Ubuntu 22.04 + Nginx + Systemd + UFW |

## 项目结构

```
douban-bigdata/
├── crawler/        # 数据采集层（Python 爬虫）
├── hdfs/           # HDFS 上传脚本与目录约定
├── spark/          # PySpark 清洗与聚合
├── backend/        # Flask REST API
├── frontend/       # Vue 3 单页前端
├── deploy/         # Nginx / Systemd 生产配置
├── scripts/        # 一键安装与启停脚本（init-mysql / start-hdfs / start-spark）
└── docs/           # schema.sql、api.md
```

## 快速开始

### 1. 云服务器初始化

首次在 Ubuntu 22.04 云服务器执行：

```bash
bash deploy/cloud_init.sh
git clone https://github.com/CrazyWaa/douban-bigdata.git /opt/douban-bigdata
```

### 2. 启动 MySQL / HDFS / Spark

```bash
bash scripts/init-mysql.sh
bash scripts/start-hdfs.sh
bash scripts/start-spark.sh
```

### 3. 爬取数据

```bash
cd /opt/douban-bigdata
python3 -m venv .venv && source .venv/bin/activate
pip install -r crawler/requirements.txt
python3 crawler/main.py
```

输出：`crawler/data/raw/movies.jsonl`

### 4. 上传到 HDFS

```bash
bash hdfs/upload_to_hdfs.sh
```

### 5. PySpark ETL

```bash
bash spark/run_etl.sh
```

或本地 dry-run（不开集群，仅打印聚合预览）：

```bash
bash spark/run_local_check.sh
```

### 6. 启动 Flask 后端

```bash
bash backend/run.sh
```

### 7. 构建并启动前端

```bash
cd frontend && npm install && npm run build
```

前端静态产物 `dist/` 由 Nginx 托管（见 `deploy/nginx/douban.conf`）。

## 数据流

```
豆瓣页面
   │
   ▼
crawler (Python) → JSONL (crawler/data/raw)
   │
   ▼
hdfs/upload_to_hdfs.sh → /raw/douban/movies/*.jsonl (HDFS)
   │
   ▼
spark/etl.py (PySpark)
   ├──► movie 主表          ┐
   ├──► agg_genre           │
   ├──► agg_country         ├──► MySQL (douban 库)
   └──► agg_year            ┘
   │
   ▼
backend (Flask) → /api/* (7 个 GET 接口)
   │
   ▼
frontend (Vue 3) → 6 个数据页面
```

## 数据量说明

- 开发/验证：本地 `crawler/data/raw/top250.jsonl` 含 25 条清洗样本
- 生产目标：Top250 + 按类型 / 地区标签扩展抓取，目标 1 万+ 条
- 注意：豆瓣对频繁请求有反爬（403/418），生产建议走云服务器 + 代理池 + 限速

## 反爬与限速

- 单请求随机 sleep 1-3 秒
- User-Agent 随机轮换（fake-useragent + 兜底池）
- 失败指数退避重试 5 次（403/418/429/5xx）
- 可选配置 `DOUBAN_PROXIES=http://ip1:port,http://ip2:port` 叠加代理

## 开发进度

| 模块 | 进度 | 关键文件 |
|---|---|---|
| 爬虫 | ~70% | `crawler/main.py`, `crawler/douban.py` |
| HDFS | ~60% | `hdfs/upload_to_hdfs.sh` |
| Spark ETL | ~80% | `spark/etl.py`, `spark/etl/*` |
| Flask 后端 | ~85% | `backend/app.py`, `backend/routes/*` |
| Vue 前端 | ~75% | `frontend/src/views/*` |
| 部署运维 | ~70% | `deploy/nginx/douban.conf`, `deploy/systemd/*` |
| 文档 | ~80% | `docs/api.md`, `docs/schema.sql` |

## 后续计划

- [ ] 扩展爬虫，按 genres/countries 维度抓取 1 万+ 条
- [ ] Spark ETL dim_* 维度表实现
- [ ] 前端 Dashboard 美化与海报渲染
- [ ] 后端接口鉴权 + 限流
- [ ] 部署自动化（一键脚本）
- [ ] 架构图与数据字典文档
