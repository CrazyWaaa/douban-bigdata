# Flask 后端服务

提供 RESTful API（全部为 GET 查询接口），前端 Vue 通过 `/api/*` 调用。

## 文件结构

```
backend/
├── app.py                  # 入口
├── config.py               # 环境配置
├── db.py                   # SQLAlchemy 引擎 + Session
├── models.py               # ORM 模型（与 docs/schema.sql 对应）
├── routes/
│   ├── __init__.py
│   ├── health.py           # /api/health
│   ├── dashboard.py        # /api/dashboard/summary
│   └── movies.py           # /api/movies/*
├── services/
│   ├── __init__.py
│   └── movies.py           # 业务查询
├── run.sh                  # 生产（Gunicorn）
├── run_dev.sh              # 开发（Flask 自带 server）
├── requirements.txt
└── .env.example
```

## 接口

| 方法 | 路径 | 参数 | 说明 |
|---|---|---|---|
| GET | `/api/health` | - | 健康检查（含 DB） |
| GET | `/api/dashboard/summary` | - | 大屏总览：总数、平均分、维度去重数 |
| GET | `/api/movies/count_by_genre` | - | 按类型分布（来自 agg_genre） |
| GET | `/api/movies/count_by_country` | - | 按地区分布（来自 agg_country） |
| GET | `/api/movies/count_by_year` | - | 按年份分布（来自 agg_year） |
| GET | `/api/movies/top_rated` | `limit=50` | 高分榜 TOP N（1-200） |
| GET | `/api/movies/<douban_id>` | - | 影片详情 |

## 配置

复制 `.env.example` 为 `.env`，按本机 MySQL 调整：

```bash
cp .env.example .env
```

或者直接用环境变量启动。

## 启动

安装依赖（一次性）：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

开发模式（自动 reload）：
```bash
bash run_dev.sh
```

生产模式（Gunicorn + Nginx 反代）：
```bash
bash run.sh
```