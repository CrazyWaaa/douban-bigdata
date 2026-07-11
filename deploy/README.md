# 部署运维

云服务器（按量付费，Ubuntu 22.04）一键部署。

## 文件结构

- `nginx/douban.conf`：Nginx 反向代理 + 静态站点
- `systemd/douban-flask.service`：Flask + Gunicorn Systemd 单元
- `systemd/hadoop.service`：HDFS 伪分布式 Systemd 单元
- `systemd/spark.service`：Spark Standalone Master/Worker Systemd 单元
- `systemd/mysql.service`：MySQL Systemd 单元（系统自带）
- `cloud_init.sh`：云服务器初始化脚本
- `README.md`：部署总览