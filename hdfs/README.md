# HDFS 存储层

约定 HDFS 目录结构：

```
/raw/douban/movies/        # 原始爬虫数据（JSONL）
/raw/douban/movies/_DONE   # 标记文件，防止重复消费
/warehouse/douban/         # Spark 清洗结果
```

## 文件结构

- `upload_to_hdfs.sh`：本地 JSONL 上传到 HDFS
- `README.md`：目录约定