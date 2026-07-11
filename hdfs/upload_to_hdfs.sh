#!/usr/bin/env bash
set -euo pipefail
LOCAL_DIR="${1:-../crawler/data/raw}"
HDFS_DIR="/raw/douban/movies"

hdfs dfs -mkdir -p "$HDFS_DIR"
hdfs dfs -put -f "$LOCAL_DIR"/* "$HDFS_DIR/" || true
hdfs dfs -touchz "$HDFS_DIR/_DONE"
echo "已上传至 $HDFS_DIR"
hdfs dfs -ls "$HDFS_DIR"