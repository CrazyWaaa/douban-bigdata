# 数据采集层（crawler）

抓取豆瓣电影 Top250 及扩展维度，输出 JSONL 文件落到本地 `data/raw/`，供上传 HDFS。

## 文件结构

- `main.py`：入口，调度 `DoubanCrawler`
- `douban.py`：请求会话、限速、UA 轮换、代理池、退避重试
- `parser.py`：页面解析（列表 + 详情）
- `ua.py`：User-Agent 池
- `proxy.py`：代理池
- `config.py`：URL、限速、重试、代理、目标条数
- `requirements.txt`：依赖

## 运行

```
cd douban-bigdata
python3 -m venv .venv
source .venv/bin/activate
pip install -r crawler/requirements.txt
python3 crawler/main.py
```

输出：`crawler/data/raw/movies.jsonl`

## 调优

环境变量（可选）：
- `DOUBAN_PROXIES=http://ip:port,http://ip2:port2` 多代理轮换
- `DOUBAN_OUTPUT_DIR=/path/to/out` 自定义输出目录
- 调整 `config.CrawlerConfig` 里的 `target_count`、`request_interval_*`、`max_retries`

## 反爬要点

- 每个请求间随机 sleep 1-3 秒
- UA 每次随机（fake-useragent 库）
- 失败指数退避（403/418/429/5xx 重试 5 次）
- 可叠加免费代理：留空即直连