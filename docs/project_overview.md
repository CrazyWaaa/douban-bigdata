# 豆瓣电影大数据分析平台 - 项目说明文档

## 1. 项目概述

本项目是一个基于豆瓣电影数据的大数据分析可视化平台，采用前后端分离架构，集成多种数据可视化图表，提供电影数据的多维度分析和交互式探索功能。

## 2. 技术栈

### 2.1 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4.x | 前端框架 |
| Vite | 5.2.x | 构建工具 |
| ECharts | 5.5.x | 数据可视化图表库 |
| vue-echarts | 7.0.x | Vue 3 ECharts 封装 |
| Pinia | 2.1.x | 状态管理 |
| Vue Router | 4.3.x | 路由管理 |
| Axios | 1.6.x | HTTP 请求 |

### 2.2 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Flask | 3.0.x | Web 框架 |
| SQLAlchemy | 2.0.x | ORM 框架 |
| PyMySQL | 1.1.x | MySQL 驱动 |
| Gunicorn | 21.2.x | WSGI 服务器 |
| Flask-Cors | 4.0.x | CORS 跨域 |
| Flask-Limiter | 3.5.x | 请求限流 |

### 2.3 数据库

| 数据库 | 版本 | 用途 |
|--------|------|------|
| MySQL | 8.0.x | 主数据库 |

### 2.4 部署架构

| 组件 | 用途 |
|------|------|
| Docker | 容器化部署 |
| Docker Compose | 多容器编排 |
| Nginx | 反向代理、静态资源服务 |

## 3. 项目结构

```
douban-bigdata/
├── backend/                    # 后端服务
│   ├── routes/                 # 路由模块
│   │   ├── dashboard.py        # 大屏总览接口
│   │   ├── health.py           # 健康检查接口
│   │   ├── img_proxy.py        # 图片代理接口
│   │   ├── movies.py           # 电影数据接口
│   │   └── viz.py              # 高级可视化接口
│   ├── services/               # 业务逻辑层
│   │   ├── movies.py           # 电影服务
│   │   └── _safe.py            # 安全工具
│   ├── app.py                  # Flask 应用入口
│   ├── models.py               # SQLAlchemy 模型
│   ├── db.py                   # 数据库连接
│   ├── auth.py                 # API 认证
│   └── config.py               # 配置管理
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── views/              # 页面视图
│   │   │   ├── Dashboard.vue   # 大屏总览
│   │   │   ├── Top.vue         # 高分榜
│   │   │   ├── Search.vue      # 搜索页面
│   │   │   ├── Genre.vue       # 类型分析
│   │   │   ├── Country.vue     # 国家分析
│   │   │   ├── Year.vue        # 年代分析
│   │   │   ├── Movie.vue       # 电影详情
│   │   │   ├── Sankey.vue      # 桑基图
│   │   │   ├── Treemap.vue     # 矩阵树
│   │   │   ├── WordCloud.vue   # 词云
│   │   │   ├── Gauge.vue       # 仪表盘
│   │   │   ├── Funnel.vue      # 漏斗图
│   │   │   ├── Calendar.vue    # 日历热力图
│   │   │   ├── Network.vue     # 关系网络图
│   │   │   ├── MapView.vue     # 世界地图
│   │   │   └── Radar.vue       # 雷达图
│   │   ├── components/         # 公共组件
│   │   │   ├── EChart.vue      # ECharts 封装
│   │   │   ├── PageScaffold.vue # 页面脚手架
│   │   │   ├── UiCard.vue      # 卡片组件
│   │   │   ├── UiMetricCard.vue # 指标卡片
│   │   │   ├── KpiBar.vue      # KPI 滚动条
│   │   │   └── ...
│   │   ├── echarts/            # ECharts 配置
│   │   │   ├── options.js      # 图表配置
│   │   │   └── echarts-setup.js # ECharts 初始化
│   │   ├── api/                # API 请求
│   │   │   ├── httpClient.js   # Axios 封装
│   │   │   └── index.js        # API 接口定义
│   │   ├── stores/             # Pinia 状态管理
│   │   │   ├── dashboard.js    # 大屏状态
│   │   │   ├── movies.js       # 电影状态
│   │   │   └── search.js       # 搜索状态
│   │   ├── router/             # 路由配置
│   │   ├── composables/        # 组合式函数
│   │   └── utils/              # 工具函数
├── crawler/                    # 爬虫模块
├── spark/                      # Spark ETL（备用）
├── data/                       # 数据库初始化脚本
├── deploy/                     # 部署配置
│   └── nginx/                  # Nginx 配置
├── scripts/                    # 维护脚本
└── docker-compose.yml          # Docker Compose 配置
```

## 4. 功能模块

### 4.1 大屏总览 (Dashboard)

- **KPI 卡片**：展示电影总数、平均评分、评价人数、最高评分等核心指标
- **高分榜 Top10**：按豆瓣评分排序的电影榜单
- **类型分布**：柱状图展示各类型片数与平均分
- **年代趋势**：折线图展示近 20 年电影数量与评分趋势
- **评分分布**：饼图展示整体评分构成
- **国家 Top10**：柱状图展示各国电影数量
- **最受关注**：展示评价人数最多的电影

### 4.2 基础查询

| 页面 | 功能 |
|------|------|
| Top | 高分电影榜单，支持排序和分页 |
| Search | 电影搜索，支持关键词匹配 |
| Genre | 类型维度分析，查看各类型电影详情 |
| Country | 国家维度分析，查看各国电影详情 |
| Year | 年代维度分析，查看各年代电影详情 |
| Movie | 电影详情页，展示完整信息 |

### 4.3 高级可视化

| 页面 | 图表类型 | 数据内容 |
|------|----------|----------|
| Sankey | 桑基图 | 类型 → 国家 → 年代三列能量流 |
| Treemap | 矩阵树 | 类型 × 国家 片数矩阵 |
| WordCloud | 词云 | 电影名称/标签词频 |
| Gauge | 仪表盘 | 评分指标展示 |
| Funnel | 漏斗图 | 评分分布漏斗 |
| Calendar | 日历热力图 | 月度发行片数 |
| Network | 关系网络图 | 演员/导演合作网络 |
| MapView | 世界地图 | 各国电影分布 |
| Radar | 雷达图 | 电影多维度分析 |

## 5. 数据库设计

### 5.1 数据表

| 表名 | 类型 | 描述 |
|------|------|------|
| `movie` | 事实表 | 电影主表，存储电影完整信息 |
| `agg_genre` | 聚合表 | 类型维度聚合（片数、平均分） |
| `agg_country` | 聚合表 | 国家维度聚合（片数、平均分） |
| `agg_year` | 聚合表 | 年代维度聚合（片数、平均分） |
| `dim_genre` | 维度表 | 类型维表 |
| `dim_country` | 维度表 | 国家维表 |
| `dim_year` | 维度表 | 年代维表 |

### 5.2 核心表结构

#### movie 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键，自增 |
| douban_id | VARCHAR(32) | 豆瓣电影 ID（唯一） |
| title | VARCHAR(255) | 电影标题 |
| director | VARCHAR(512) | 导演 |
| actors | TEXT | 演员列表 |
| genre | VARCHAR(128) | 类型（空格分隔） |
| country | VARCHAR(256) | 国家（空格分隔） |
| year | SMALLINT | 上映年份 |
| rating | DECIMAL(3,1) | 豆瓣评分 |
| rating_count | INT | 评价人数 |
| summary | TEXT | 剧情简介 |
| poster_url | VARCHAR(512) | 海报链接 |
| runtime_minutes | INT | 片长（分钟） |
| rating_stars | VARCHAR(512) | 星级占比（JSON） |
| created_at | TIMESTAMP | 创建时间 |

#### 聚合表 (agg_genre/agg_country/agg_year)

| 字段 | 类型 | 说明 |
|------|------|------|
| genre/country/year | VARCHAR/INT | 维度键（主键） |
| movie_count | INT | 电影数量 |
| avg_rating | DECIMAL(3,2) | 平均评分 |

## 6. API 接口

### 6.1 大屏接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/dashboard/summary` | GET | 大屏核心指标 |
| `/api/dashboard/summary_extended` | GET | 大屏扩展指标 |

### 6.2 电影接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/movies` | GET | 电影列表 |
| `/api/movies/{id}` | GET | 电影详情 |
| `/api/movies/top` | GET | 高分榜 |
| `/api/movies/search` | GET | 搜索电影 |

### 6.3 高级可视化接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/sankey/flow` | GET | 桑基图数据（类型→国家→年代） |
| `/api/treemap/genre-country` | GET | 矩阵树数据 |
| `/api/calendar/monthly` | GET | 日历热力数据 |
| `/api/network/collaborations` | GET | 关系网络数据 |
| `/api/map/countries` | GET | 世界地图数据 |

### 6.4 健康检查

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |

## 7. 数据流

### 7.1 数据采集阶段

```
豆瓣网站 → 爬虫(crawler/) → MySQL (movie表)
```

### 7.2 数据处理阶段

```
movie表 → ETL脚本(spark/或scripts/) → 聚合表(agg_*)
```

### 7.3 数据展示阶段

```
MySQL → Flask API → Vue前端 → ECharts图表
```

### 7.4 详细数据流图

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   爬虫模块    │ ──→ │   MySQL      │ ──→ │   Flask API  │
│  crawler/    │     │  movie表     │     │   routes/    │
└──────────────┘     └──────┬───────┘     └──────┬───────┘
                            │                    │
                            ▼                    │
                    ┌──────────────┐             │
                    │   ETL处理    │             │
                    │  scripts/    │             │
                    └──────┬───────┘             │
                            │                    │
                            ▼                    │
                    ┌──────────────┐             │
                    │  聚合表      │             │
                    │ agg_genre    │             │
                    │ agg_country  │             │
                    │ agg_year     │             │
                    └──────────────┘             │
                                                 ▼
                                    ┌──────────────────────┐
                                    │    Vue 前端          │
                                    │   views/             │
                                    │   components/        │
                                    │   echarts/           │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │   ECharts 可视化      │
                                    │  桑基图/矩阵树/词云等  │
                                    └──────────────────────┘
```

## 8. 部署架构

### 8.1 Docker 容器

| 容器 | 镜像 | 端口 | 用途 |
|------|------|------|------|
| douban-backend | douban-bigdata-backend | 5000 | Flask 后端 |
| douban-mysql | mysql:8.0 | 33306 | MySQL 数据库 |
| douban-nginx | nginx:1.27-alpine | 8080 | Nginx 反向代理 |

### 8.2 网络架构

```
用户浏览器 → Nginx(8080) → Flask后端(5000) → MySQL(3306)
                    │
                    └──→ 静态资源(frontend/dist)
```

### 8.3 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| MYSQL_HOST_PORT | 33306 | MySQL 端口 |
| DATA_ROOT | ./data | 数据目录 |
| DOUBAN_API_KEY | - | API 认证密钥 |
| DOUBAN_RATE_LIMIT | 60/minute | 请求限流 |

## 9. 运行方式

### 9.1 开发模式

```bash
# 前端开发
cd frontend
npm install
npm run dev

# 后端开发
cd backend
pip install -r requirements.txt
python app.py
```

### 9.2 Docker 部署

```bash
# 启动所有服务
docker compose up -d

# 启动 ETL 任务（一次性）
docker compose --profile etl up -d
```

### 9.3 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:8080 |
| 前端开发 | http://localhost:5173 |
| 后端 API | http://localhost:8080/api |
| MySQL | localhost:33306 |

## 10. 关键特性

- **响应式设计**：支持大屏、桌面、移动端自适应布局
- **深色主题**：全局深色配色，适合数据可视化场景
- **数据聚合**：预计算聚合表，提升查询性能
- **请求限流**：防止 API 滥用
- **图片代理**：解决豆瓣图片跨域问题
- **ETL 支持**：提供 Spark 和 Python 两种 ETL 方案

## 11. 版本信息

- 项目版本：0.1.0
- 创建日期：2026年7月
- 最后更新：2026年7月14日