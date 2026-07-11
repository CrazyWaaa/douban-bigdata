# Douban Bigdata - 部署指南

端到端 Docker 化部署:一条命令起 MySQL + 后端 + Nginx,数据全部走 D 盘(本机)或 `/opt/douban-bigdata`(云)。

## 0. 准备

### 本机(Windows 11)
- 安装 Docker Desktop:`https://www.docker.com/products/docker-desktop/`
- 第一次启动要打开 WSL2 后端(默认)
- 准备 D 盘空间(预计镜像+数据 3-5 GB)

### 云服务器(Linux)
- Ubuntu 22.04 LTS 2C4G 起
- 装 Docker + Compose Plugin:
  ```bash
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker $USER
  newgrp docker   # 或重连 SSH
  ```
- 安全组开 TCP 22 / 8080(如果用 80 改 compose 端口)

## 1. 一键起

### Windows PowerShell
```powershell
cd D:\Ayueqian\project\code\douban-bigdata
cp .env.example .env
.\scripts\deploy.ps1
```

### Windows Git Bash / Linux
```bash
cd /path/to/douban-bigdata
cp .env.example .env
bash scripts/deploy.sh
```

脚本会:
1. 在 `DATA_ROOT` 下自动创建 4 个子目录(mysql-data / data/raw / logs/backend / dist)
2. 把 `data/raw/*.jsonl` 转成 SQL,放进 `scripts/seed-data/`
3. 构建前端(`npm run build`),把 `dist/` 拷到 `DATA_ROOT/dist/`
4. `docker compose up -d --build` 启动 MySQL + Backend + Nginx
5. 健康检查 `http://127.0.0.1:5000/api/health`

> 注:ETL 是 `profiles: [etl]` 隔离,**默认不跑**。需要时手动触发:
> ```bash
> docker compose --profile etl run --rm etl
> ```

## 2. 验证

```bash
# 容器状态
docker compose ps
# 应看到 mysql(healthy)/ backend / nginx 三个 Up

# API
curl http://127.0.0.1:8080/api/health
curl http://127.0.0.1:8080/api/dashboard/overview

# 数据库
docker compose exec mysql mysql -udouban -pdouban_pwd douban -e "SELECT COUNT(*) FROM movie;"
```

前端入口:`http://127.0.0.1:8080`

## 3. 文件路径(C 盘零写入)

| 容器 | 写入路径 | 宿主机路径 |
|---|---|---|
| MySQL | `/var/lib/mysql` | `${DATA_ROOT}/mysql-data`(默认 `D:\douban-bigdata\mysql-data`) |
| ETL 输入 | `/data/raw` | `${DATA_ROOT}/data/raw`(默认 `D:\douban-bigdata\data\raw`) |
| Backend 日志 | `/var/log/gunicorn` | `${DATA_ROOT}/logs/backend` |
| Nginx 静态 | `/usr/share/nginx/html` | `${DATA_ROOT}/dist` |

**DOCKER 镜像本身仍占 C 盘**(默认 2-4 GB,不可绕开)
把 Docker Desktop 的 WSL 虚拟盘搬到 D 盘:
```powershell
wsl --export docker-desktop-data "D:\Docker\docker-desktop-data.tar"
wsl --unregister docker-desktop-data
wsl --import docker-desktop-data "D:\Docker\wsl\data" "D:\Docker\docker-desktop-data.tar" --version 2
```

## 4. 日常命令

```bash
docker compose ps                # 看状态
docker compose logs -f backend   # 看后端日志
docker compose restart backend   # 重启后端
docker compose down              # 停掉(数据保留)
docker compose down -v           # 停掉并清空 MySQL 数据(谨慎)
```

定时跑 ETL(每 6 小时一次,在宿主 crontab / 任务计划程序):
```bash
docker compose --profile etl run --rm etl
```

## 5. 上云迁移

把本机 `.env` 改成:
```bash
# Linux 云
export DATA_ROOT=/opt/douban-bigdata
```

然后在云服务器上:
```bash
ssh user@server
sudo mkdir -p /opt/douban-bigdata/{mysql-data,data/raw,logs/backend,dist}
# rsync 本机 DIST 和 SEED 到云(也可以直接在云上 build)
cd /opt/douban-bigdata && docker compose up -d --build
```

## 6. 常见问题

| 症状 | 原因 | 解决 |
|---|---|---|
| `bind: address already in use` 端口冲突 | 本机已有 MySQL | 改 `.env` 的 `MYSQL_HOST_PORT=3307` 等 |
| mysql 容器频繁 restart | `mysql-data` 损坏 | `docker compose down -v` 重置 |
| 后端日志 `Can't connect to MySQL` | healthcheck 未通过 | `docker compose logs mysql` 看密码是否对 |
| ETL 找不到 JSONL | `data/raw` 没数据 | `python crawler/main.py` 抓一次 |
| 前端页面空白 | `dist/` 空 | `cd frontend && npm run build` 后重跑 `deploy.ps1` |
| C 盘突然变满 | named volume 没挂载对 | 全部用 bind mount,改 DATA_ROOT |