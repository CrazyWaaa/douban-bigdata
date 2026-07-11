# 数据采集层（crawler）

抓取豆瓣电影 Top250 及按类型/地区/年份扩展的影片，输出 JSON 行式文件落到 HDFS。

## 文件结构

- `main.py`：入口，调度各类型/地区的抓取任务
- `douban.py`：豆瓣页面请求与解析（Requests + BeautifulSoup4）
- `proxy.py`：可选代理池管理
- `ua.py`：UA 轮换
- `config.py`：抓取配置（URL 模板、限速、重试次数）
- `requirements.txt`：依赖列表