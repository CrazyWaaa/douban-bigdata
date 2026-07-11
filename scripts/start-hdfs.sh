#!/usr/bin/env bash
set -euo pipefail
export HADOOP_HOME=/usr/local/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

hdfs namenode -format -force -nonInteractive || true
start-dfs.sh
sleep 2
echo "== HDFS 状态 =="
hdfs dfsadmin -report | head -20
echo "== 进程 =="
jps