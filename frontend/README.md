# Vue 3 前端

## 技术栈

- Vue 3 + Vite 5
- Vue Router 4
- Pinia 2
- ECharts 5（自封装 EChart 组件）
- Axios

## 页面

| 路由 | 页面 | 说明 |
|---|---|---|
| `/` | Dashboard | 数据大屏总览 |
| `/genre` | Genre | 按类型分布柱状图 |
| `/country` | Country | 按地区分布饼图 |
| `/year` | Year | 按年份分布折线图 |
| `/top` | Top | 高分榜 TOP 50 |
| `/movie/:id` | Movie | 影片详情 |

## 开发

```
cd frontend
npm install
npm run dev
```

Vite dev server 默认 `http://localhost:5173`，已配置 `/api` 反向代理到 `http://127.0.0.1:5000`。

## 构建

```
npm run build
```

产物在 `dist/`，部署时由 Nginx 托管，`/api` 反代到 Flask。