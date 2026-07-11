#!/usr/bin/env bash
# 本地验证用：不需要 Spark 集群，pyspark 在 driver 模式跑。
set -euo pipefail
cd "$(dirname "$0")/.."
python3 spark/etl.py --input crawler/data/raw --skip-writes "$@"