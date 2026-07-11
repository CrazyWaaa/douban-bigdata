# Vue 3 前端

## 技术栈

- Vue 3 + Vite
- Vue Router 4
- Pinia
- ECharts 5
- Axios

## 多页规划

| 路由 | 页面 |
|---|---|
| `/` | 数据大屏 Dashboard |
| `/genre` | 按类型分布 |
| `/country` | 按地区分布 |
| `/year` | 按年份分布 |
| `/top` | 高分榜 |
| `/movie/:id` | 影片详情 |

## 本地开发

```
npm install
npm run dev
```

## 生产构建

```
npm run build
```

构建产物在 `dist/`，由 Nginx 静态托管，反向代理转发 `/api` 到 Flask。