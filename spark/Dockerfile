# Douban ETL - 轻量纯 Python 镜像（pymysql 写 MySQL）
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY etl.py ./

CMD ["python", "etl.py", "--input", "/data/raw"]
