# Flask 后端服务

提供 RESTful API，供 Vue 前端调用。所有接口均为 GET 查询接口。

## 接口规划

| 路由 | 说明 |
|---|---|
| `/api/dashboard/summary` | 大屏总览统计 |
| `/api/movies/count_by_genre` | 按类型分布 |
| `/api/movies/count_by_country` | 按地区分布 |
| `/api/movies/count_by_year` | 按年份分布 |
| `/api/movies/top_rated` | 高分榜 TOP N |
| `/api/movies/<id>` | 影片详情 |
| `/api/health` | 健康检查 |

## 启动

开发模式：`python3 app.py`
生产模式：`bash run.sh`