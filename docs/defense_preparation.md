# 豆瓣电影大数据分析平台 - 答辩准备文档

## 项目信息

- **项目名称**：豆瓣电影大数据分析平台
- **团队成员**：[组长姓名]（组长）、[组员A姓名]、[组员B姓名]
- **答辩时间**：约 15-20 分钟
- **分工策略**：组长负责核心架构和数据流，组员A负责前端技术和可视化，组员B负责后端技术和数据库

---

## 一、答辩流程与时间分配

| 环节 | 主讲人 | 时长 | 内容 |
|------|--------|------|------|
| 项目概述 | 魏少锋 | 2分钟 | 项目背景、目标、整体架构 |
| 前端技术 | 陈壹伟 | 4分钟 | Vue 3、ECharts、响应式布局 |
| 后端技术 | 李子瑗 | 4分钟 | Flask、SQLAlchemy、API设计 |
| 核心功能演示 | 魏少锋 | 3分钟 | 大屏、高级可视化展示 |
| 数据流与ETL | 魏少锋 | 3分钟 | 数据采集、处理、展示流程 |
| 问答环节 | 全员 | 3-4分钟 | 回答评委问题 |

---

## 二、各部分详细说辞

### 2.1 项目概述（组长）

**开场白：**
> 各位老师好，我们团队的项目是豆瓣电影大数据分析平台。这是一个基于豆瓣电影数据的可视化分析系统，主要目标是通过多维度的数据展示，帮助用户了解电影市场的整体情况。

**技术栈概述：**
> 我们采用前后端分离的架构，前端使用 Vue 3 + ECharts 实现数据可视化，后端使用 Flask + SQLAlchemy 提供 API 服务，数据库采用 MySQL，通过 Docker 容器化部署。

**项目亮点：**
> 本项目的核心亮点在于丰富的可视化图表类型，包括桑基图、矩阵树、词云、日历热力图等 9 种高级可视化，以及完整的大屏展示功能。

---

### 2.2 前端技术（陈壹伟）

**负责内容：** Vue 3、Vite、ECharts、响应式布局、组件设计

#### 2.2.1 Vue 3 框架

**说辞：**
> 前端框架我们选择了 Vue 3，主要是因为它的组合式 API 非常适合构建复杂的单页应用。我们使用了 `<script setup>` 语法，让代码更加简洁，同时利用 Pinia 进行状态管理，实现了数据在组件间的高效共享。

**核心代码位置：**
- [main.js](file:///d:/Ayueqian/project/code/douban-bigdata/frontend/src/main.js) - Vue 应用入口
- [stores/dashboard.js](file:///d:/Ayueqian/project/code/douban-bigdata/frontend/src/stores/dashboard.js) - Pinia 状态管理

**可能提问及回答：**
- Q：为什么选择 Vue 3 而不是 React？
  - A：Vue 3 的组合式 API 学习曲线相对平缓，且我们团队对 Vue 更为熟悉，能够更快上手开发。

#### 2.2.2 Vite 构建工具

**说辞：**
> 构建工具我们使用了 Vite，它的冷启动速度非常快，能够大大提升开发效率。Vite 采用了 ES Module 原生加载，避免了打包过程，热更新也非常迅速。

**核心配置：**
- [vite.config.js](file:///d:/Ayueqian/project/code/douban-bigdata/frontend/vite.config.js) - Vite 配置，包含代理设置

#### 2.2.3 ECharts 可视化

**说辞：**
> 数据可视化是本项目的核心，我们使用 ECharts 作为图表库。ECharts 支持多种图表类型，配置灵活，且性能优秀。我们封装了统一的 EChart 组件，方便在各个页面中复用。

**图表类型及用途：**

| 图表 | 页面 | 用途 |
|------|------|------|
| 柱状图 | Dashboard、Genre、Country | 展示分类数据对比 |
| 折线图 | Dashboard、Year | 展示时间趋势 |
| 饼图 | Dashboard | 展示占比分布 |
| 桑基图 | Sankey | 展示多维度流量关系 |
| 矩阵树 | Treemap | 展示层级数据聚合 |
| 词云 | WordCloud | 展示文本词频 |
| 漏斗图 | Funnel | 展示转化率 |
| 日历热力图 | Calendar | 展示日期分布 |
| 关系网络图 | Network | 展示实体关系 |

**核心代码位置：**
- [components/EChart.vue](file:///d:/Ayueqian/project/code/douban-bigdata/frontend/src/components/EChart.vue) - ECharts 封装组件
- [echarts/options.js](file:///d:/Ayueqian/project/code/douban-bigdata/frontend/src/echarts/options.js) - 图表配置

**可能提问及回答：**
- Q：桑基图的数据是如何处理的？
  - A：桑基图需要节点和连线数据，我们从后端 API 获取 nodes 和 links，前端负责数据的类型转换和节点匹配验证，确保 source/target 与 nodes.name 精确匹配。

#### 2.2.4 响应式布局

**说辞：**
> 我们实现了响应式布局，大屏页面采用三栏网格布局，在不同分辨率下会自动调整。使用 CSS Grid 和 Flexbox 组合，确保页面在大屏、桌面、移动端都有良好的显示效果。

**核心代码位置：**
- [views/Dashboard.vue](file:///d:/Ayueqian/project/code/douban-bigdata/frontend/src/views/Dashboard.vue#L307-L358) - Dashboard 布局样式

#### 2.2.5 组件设计

**说辞：**
> 我们采用了组件化开发的思想，将页面拆分为多个可复用的组件。比如 KpiBar 组件用于展示核心指标，UiCard 组件用于统一卡片样式，UiChartCard 组件用于图表卡片的封装。

**核心组件：**
- [KpiBar.vue](file:///d:/Ayueqian/project/code/douban-bigdata/frontend/src/components/dashboard/KpiBar.vue) - KPI 指标卡片
- [UiCard.vue](file:///d:/Ayueqian/project/code/douban-bigdata/frontend/src/components/ui/UiCard.vue) - 基础卡片组件
- [PageScaffold.vue](file:///d:/Ayueqian/project/code/douban-bigdata/frontend/src/components/layout/PageScaffold.vue) - 页面脚手架

---

### 2.3 后端技术（李子瑗）

**负责内容：** Flask、SQLAlchemy、API 设计、数据聚合、部署配置

#### 2.3.1 Flask 框架

**说辞：**
> 后端我们选择了 Flask 框架，它是一个轻量级的 Python Web 框架，非常适合快速开发 RESTful API。Flask 的路由系统简洁明了，扩展性也很好。

**核心代码位置：**
- [app.py](file:///d:/Ayueqian/project/code/douban-bigdata/backend/app.py) - Flask 应用入口

**可能提问及回答：**
- Q：为什么选择 Flask 而不是 Django？
  - A：Flask 更加轻量灵活，适合构建 API 服务，而 Django 更适合完整的 Web 应用。我们的项目主要是提供数据接口，Flask 足够满足需求。

#### 2.3.2 SQLAlchemy ORM

**说辞：**
> 数据库层面我们使用了 SQLAlchemy ORM，它提供了强大的对象关系映射能力，让我们可以用 Python 对象来操作数据库，避免了直接编写 SQL 的繁琐。同时，SQLAlchemy 的查询构建器非常灵活，支持复杂的查询操作。

**核心代码位置：**
- [models.py](file:///d:/Ayueqian/project/code/douban-bigdata/backend/models.py) - 数据库模型定义

**模型结构：**
> 我们定义了 Movie 模型作为核心数据模型，包含电影的基本信息如标题、导演、演员、类型、国家、年份、评分等字段。同时还有三个聚合模型：AggGenre、AggCountry、AggYear，用于存储预计算的统计数据，提升查询性能。

**可能提问及回答：**
- Q：聚合表的作用是什么？
  - A：聚合表存储了预计算的统计数据，比如每个类型的电影数量和平均评分。这样前端查询时不需要实时计算，可以直接从聚合表获取数据，大大提升了响应速度。

#### 2.3.3 API 设计

**说辞：**
> 我们设计了 RESTful 风格的 API，分为几个模块：dashboard 模块提供大屏数据，movies 模块提供电影查询和搜索，viz 模块提供高级可视化数据。API 统一使用 JSON 格式返回数据，便于前端处理。

**API 模块划分：**

| 模块 | 路由前缀 | 文件 | 说明 |
|------|----------|------|------|
| Dashboard | /api/dashboard | [routes/dashboard.py](file:///d:/Ayueqian/project/code/douban-bigdata/backend/routes/dashboard.py) | 大屏数据接口 |
| Movies | /api/movies | [routes/movies.py](file:///d:/Ayueqian/project/code/douban-bigdata/backend/routes/movies.py) | 电影数据接口 |
| Visualization | /api | [routes/viz.py](file:///d:/Ayueqian/project/code/douban-bigdata/backend/routes/viz.py) | 可视化数据接口 |
| Health | /api/health | [routes/health.py](file:///d:/Ayueqian/project/code/douban-bigdata/backend/routes/health.py) | 健康检查 |

**关键接口示例：**
- GET /api/movies/top - 获取高分电影榜单
- GET /api/movies/search?q=keyword - 搜索电影
- GET /api/sankey/flow - 获取桑基图数据
- GET /api/dashboard/summary - 获取大屏核心指标

**可能提问及回答：**
- Q：桑基图的数据是如何生成的？
  - A：桑基图数据通过 SQL 查询生成，从 movie 表中统计类型→国家→年代的流量数据，返回 nodes 和 links 两个数组，前端直接用于渲染桑基图。

#### 2.3.4 请求限流与认证

**说辞：**
> 为了防止 API 被滥用，我们使用 Flask-Limiter 实现了请求限流，默认每分钟限制 60 次请求。同时，API 接口支持 API Key 认证，通过请求头传递认证信息。

**核心代码位置：**
- [auth.py](file:///d:/Ayueqian/project/code/douban-bigdata/backend/auth.py) - 认证逻辑
- [config.py](file:///d:/Ayueqian/project/code/douban-bigdata/backend/config.py) - 配置管理

#### 2.3.5 数据库设计

**说辞：**
> 数据库设计采用了维度建模的思想，包含一个事实表 movie 和三个维度聚合表。这种设计既能存储完整的电影数据，又能通过聚合表快速获取统计信息。

**数据库表结构：**

```
┌─────────────────────────────────────────────────────────────┐
│                      movie 事实表                           │
├──────────┬────────────────┬─────────────────────────────────┤
│ 字段     │ 类型           │ 说明                            │
├──────────┼────────────────┼─────────────────────────────────┤
│ id       │ BIGINT         │ 主键                            │
│ douban_id│ VARCHAR(32)    │ 豆瓣电影ID                      │
│ title    │ VARCHAR(255)   │ 电影标题                        │
│ director │ VARCHAR(512)   │ 导演                            │
│ actors   │ TEXT           │ 演员列表                        │
│ genre    │ VARCHAR(128)   │ 类型（空格分隔）                │
│ country  │ VARCHAR(256)   │ 国家（空格分隔）                │
│ year     │ SMALLINT       │ 上映年份                        │
│ rating   │ DECIMAL(3,1)   │ 豆瓣评分                        │
│ rating_count│ INT         │ 评价人数                        │
│ summary  │ TEXT           │ 剧情简介                        │
│ poster_url│ VARCHAR(512)  │ 海报链接                        │
└──────────┴────────────────┴─────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  聚合表 (agg_genre/country/year)            │
├─────────────┬────────────────┬──────────────────────────────┤
│ 字段        │ 类型           │ 说明                         │
├─────────────┼────────────────┼──────────────────────────────┤
│ genre       │ VARCHAR(32)    │ 类型名称（主键）              │
│ movie_count │ INT            │ 电影数量                     │
│ avg_rating  │ DECIMAL(3,2)   │ 平均评分                     │
└─────────────┴────────────────┴──────────────────────────────┘
```

**可能提问及回答：**
- Q：为什么使用空格分隔存储多值字段（genre、country）？
  - A：因为一部电影可能属于多个类型或来自多个国家，使用空格分隔是一种简单有效的存储方式，便于后续的字符串分割和统计。

---

### 2.4 核心功能演示（组长）

**负责内容：** 大屏展示、高级可视化、整体功能介绍

**演示流程：**
1. 打开大屏页面，展示核心指标
2. 展示高分榜 Top10
3. 切换到高级可视化页面，演示桑基图
4. 演示矩阵树、词云等其他图表
5. 演示搜索功能

**说辞要点：**
> 大屏页面展示了电影数据的核心指标，包括电影总数、平均评分、评价人数等。高分榜展示了评分最高的电影。高级可视化页面提供了多种图表，帮助用户从不同维度分析电影数据。

---

### 2.5 数据流与ETL（组长）

**负责内容：** 数据采集、ETL 处理、数据流向

**数据流程图说：**

> 我们的数据流程分为三个阶段：

**第一阶段：数据采集**
> 通过爬虫模块从豆瓣网站获取电影数据，存储到 MySQL 的 movie 表中。爬虫使用 Python 编写，模拟浏览器请求，获取电影的完整信息。

**第二阶段：ETL 处理**
> 数据采集完成后，通过 ETL 脚本对数据进行清洗和聚合。计算每个类型、国家、年份的电影数量和平均评分，存储到对应的聚合表中。这样可以提升前端查询的性能。

**第三阶段：数据展示**
> 前端通过 API 从后端获取数据，使用 ECharts 渲染成各种图表。整个数据流是单向流动的：采集→处理→展示。

**数据流图：**
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
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │   ECharts 可视化      │
                                    │  桑基图/矩阵树/词云等  │
                                    └──────────────────────┘
```

**可能提问及回答：**
- Q：为什么需要聚合表？直接查询不行吗？
  - A：直接查询需要对大量数据进行实时统计，响应速度较慢。使用聚合表可以预先计算好统计结果，前端查询时直接获取，大大提升了响应速度，尤其适合大屏实时展示的场景。

---

## 三、常见问题及回答

### 3.1 技术选型类

**Q：为什么选择前后端分离架构？**
> A：前后端分离可以让前端和后端团队独立开发，提高开发效率。同时，前端可以使用更适合的技术栈（Vue + ECharts）来实现复杂的数据可视化，后端专注于提供高质量的 API 服务。

**Q：为什么使用 Docker 部署？**
> A：Docker 可以将应用及其依赖打包成容器，确保在不同环境中运行一致。使用 Docker Compose 可以方便地管理多个容器（后端、数据库、Nginx），简化部署流程。

**Q：ECharts 和其他图表库相比有什么优势？**
> A：ECharts 是百度开源的图表库，功能强大，支持多种图表类型，文档丰富，社区活跃。特别是在大数据可视化方面，ECharts 的性能表现优秀，适合我们项目的需求。

### 3.2 功能实现类

**Q：桑基图的节点是如何匹配的？**
> A：桑基图需要 nodes 和 links 数据，links 中的 source 和 target 必须与 nodes 中的 name 完全匹配。我们在后端生成数据时确保三者一致，前端也做了类型转换（统一转为字符串）和存在性验证。

**Q：词云的数据是如何生成的？**
> A：词云的数据来自电影名称中的关键词，通过分词和词频统计生成。我们可以根据需求调整分词策略，展示不同维度的关键词。

**Q：日历热力图展示的是什么数据？**
> A：日历热力图展示的是每个月份的电影发行数量，颜色深浅代表片数多少，可以直观地看出电影发行的时间分布规律。

### 3.3 性能优化类

**Q：如何保证大屏展示的实时性？**
> A：我们通过预计算聚合表、使用缓存策略、优化 SQL 查询等方式来提升性能。大屏数据接口返回的都是聚合后的统计数据，数据量较小，可以快速响应。

**Q：电影数据量很大，如何处理？**
> A：我们使用了分页查询，前端每次只获取部分数据。同时，聚合表的使用减少了实时计算的开销。对于高级可视化，我们也做了数据采样和聚合处理。

### 3.4 项目扩展类

**Q：项目未来可以如何扩展？**
> A：可以增加更多的可视化图表类型，比如 3D 图表；可以接入更多数据源，比如用户评论数据；可以增加用户登录和个性化推荐功能；可以优化移动端体验等。

**Q：如何处理数据更新？**
> A：可以定期运行爬虫更新数据，或者使用增量更新策略。ETL 脚本也可以定时执行，更新聚合表的数据。

---

## 四、组员分工明细

### 组长
- [x] 项目整体架构设计
- [x] 数据流设计与 ETL 方案
- [x] 大屏功能开发
- [x] 核心功能演示
- [x] 答辩主导

### 组员A（陈壹伟）
- [x] Vue 3 项目搭建
- [x] 响应式布局实现
- [x] ECharts 图表配置
- [x] 组件设计与封装
- [x] 前端页面开发

### 组员B（李子瑗）
- [x] Flask API 开发
- [x] SQLAlchemy 模型设计
- [x] 数据库设计与优化
- [x] API 认证与限流
- [x] Docker 部署配置

---


