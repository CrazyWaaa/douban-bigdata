#!/usr/bin/env bash
set -euo pipefail
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin
export PYSPARK_PYTHON=python3

cd "$(dirname "$0")/.."

spark-submit \
  --master spark://$(hostname):7077 \
  --driver-memory 1g \
  --executor-memory 1g \
  --packages mysql:mysql-connector-java:8.0.33 \
  spark/etl.py "$@"