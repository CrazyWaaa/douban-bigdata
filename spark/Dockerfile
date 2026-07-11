# Douban Spark ETL - 一次性任务镜像
# 用 bitnami/spark 3.5(java + pyspark + spark-submit 都齐了,免安装)
FROM bitnami/spark:3.5.1

USER root

# 国内 PyPI 镜像,加速 pyspark 与 jdbc driver 解析
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

WORKDIR /opt/spark-app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY etl.py ./
COPY etl/ ./etl/

# 默认以 local[*] 模式跑(单容器单机,不依赖外部 spark master)
# compose 会通过环境变量覆盖 ETL_HDFS_INPUT / ETL_DB_HOST 等
CMD ["bash","-lc","spark-submit --master local[*] --driver-memory 1g --packages mysql:mysql-connector-java:8.0.33 etl.py --input /data/raw"]