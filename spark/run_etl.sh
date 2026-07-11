#!/usr/bin/env bash
set -euo pipefail
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin
export PYSPARK_PYTHON=python3

spark-submit \
  --master spark://$(hostname):7077 \
  --driver-memory 1g \
  --executor-memory 1g \
  "$(dirname "$0")/etl.py"