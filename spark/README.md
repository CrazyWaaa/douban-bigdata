# PySpark 计算层

从 HDFS 读取原始 JSONL 数据，清洗、规范化、聚合后通过 JDBC 写入 MySQL。

## 文件结构

- `etl.py`：主 ETL 任务
- `run_etl.sh`：提交脚本
- `README.md`：使用说明