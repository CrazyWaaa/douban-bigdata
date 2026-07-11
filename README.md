# 豆瓣电影大数据分析平台

基于经典大数据分层架构的端到端实训项目：爬虫 → HDFS → Spark → MySQL → Flask → Vue 3 → Nginx。

## 技术栈

| 层 | 技术 |
|---|---|
| 数据采集 | Python 3 + Requests + BeautifulSoup4 |
| 分布式存储 | Hadoop HDFS（伪分布式） |
| 分布式计算 | Apache Spark + PySpark（Standalone） |
| 关系数据库 | MySQL 8 |
| 后端服务 | Flask + Gunicorn + Nginx |
| 前端展示 | Vue 3 + Vue Router + Pinia + ECharts 5 |
| 部署运维 | Ubuntu 22.04 + Nginx + Systemd + UFW |

## 项目结构

```
douban-bigdata/
├── crawler/     # 数据采集层（Python 爬虫）
├── hdfs/        # HDFS 数据落地与目录规划
├── spark/       # PySpark 清洗与聚合任务
├── backend/     # Flask REST API
├── frontend/    # Vue 3 多页前端
├── deploy/      # 云服务器部署配置（Nginx / Systemd）
├── scripts/     # 一次性安装脚本（bootstrap.sh 等）
└── docs/        # 设计文档、库表设计、接口文档
```

## 快速开始

1. 本地 Ubuntu 虚拟机一次性初始化：`bash scripts/bootstrap.sh`
2. 启动 HDFS：`bash scripts/start-hdfs.sh`
3. 跑爬虫：`cd crawler && python3 main.py`
4. PySpark 清洗：`bash spark/run_etl.sh`
5. 启 Flask：`bash backend/run.sh`
6. 启 Vue：`cd frontend && npm run dev`

## 部署上线

参见 `deploy/README.md`。
