#!/usr/bin/env bash
set -euo pipefail
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin

start-master.sh
sleep 2
start-worker.sh spark://$(hostname):7077 || start-slave.sh spark://$(hostname):7077
sleep 2
echo "== Spark Master UI: http://$(hostname):8080 =="
jps