# PySpark 计算层

读 HDFS 上的 JSONL 数据，规范化字段、按多维度聚合，结果通过 JDBC 直写 MySQL。

## 文件结构

```
spark/
├── etl.py                  # 主任务入口（argparse）
├── run_etl.sh              # 集群模式提交（spark-submit -> spark://...）
├── run_local_check.sh      # 本地验证：不写 MySQL、stdout 预览聚合
└── etl/
    ├── settings.py         # 环境配置（HDFS 路径 / JDBC URL）
    ├── reader.py           # 从 HDFS 读 JSONL
    ├── transformer.py      # 清洗、类型转换、去重
    ├── aggregator.py       # agg_genre / agg_country / agg_year
    └── writer.py           # JDBC 写 MySQL
```

## 运行

集群模式（HDFS + Spark Standalone + MySQL）：
```bash
bash run_etl.sh
```

本地 dry-run（不开集群，直接读 `crawler/data/raw/*.jsonl`，stdout 打印聚合预览）：
```bash
bash run_local_check.sh
```

自定义参数：
```bash
python3 spark/etl.py --help
```

## 数据流

```
HDFS /raw/douban/movies/*.jsonl
        │
        ▼
reader (read.json)
        │
        ▼
transformer (类型转换 / 去空 / 去重 / year 合法性)
        │
        ├──► movie 主表
        ├──► agg_genre
        ├──► agg_country
        └──► agg_year
        │
        ▼
writer (JDBC，写 MySQL 库 douban)
```

## 环境变量

- `ETL_HDFS_INPUT`：HDFS 输入根目录，默认 `hdfs://localhost:9000/raw/douban/movies`
- `ETL_SPARK_MASTER`：Spark master URL，默认 `spark://localhost:7077`
- `ETL_SHUFFLE_PARTITIONS`：shuffle 并行度，默认 8
- `ETL_DB_HOST/PORT/NAME/USER/PASSWORD`：JDBC 连接信息