# 阿里云 ECS 单机部署

本项目生产链路为：`Nginx -> Flask/Gunicorn -> MySQL 8.0`，全部由 Docker Compose 管理。Spark/ETL 是按需任务，不作为常驻服务启动。

## 1. 推荐配置

- 操作系统：Ubuntu 22.04 或 24.04 64 位
- 最低配置：2 vCPU / 4 GiB；需要在服务器跑 ETL 时建议 4 vCPU / 8 GiB
- 系统盘：至少 40 GiB；电影数据较多时单独挂载数据盘并把 `DATA_ROOT` 指向挂载点
- 安全组入方向：仅开放 `22/tcp`（建议限制为你的办公公网 IP）、`80/tcp`；配置域名和证书后再开放 `443/tcp`
- 不开放：`3306/tcp`、`5000/tcp`

## 2. 安装运行环境

```bash
sudo apt update
sudo apt install -y git curl ca-certificates docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
newgrp docker

docker --version
docker compose version
```

若镜像拉取缓慢，可执行：

```bash
sudo bash deploy/setup_mirror.sh
```

不要额外安装宿主机 MySQL 或 Nginx，避免与 Compose 容器抢占端口。

## 3. 拉取项目并配置

```bash
sudo mkdir -p /opt/douban-bigdata
sudo chown -R "$USER:$USER" /opt/douban-bigdata
git clone <YOUR_REPOSITORY_URL> /opt/douban-bigdata
cd /opt/douban-bigdata
cp .env.production.example .env
```

编辑 `.env`，必须替换两个 `CHANGE_ME` 密码。可生成随机密码：

```bash
openssl rand -base64 32
```

默认生产模板使用：

- `DATA_ROOT=/opt/douban-data`
- `FRONTEND_DIST=/opt/douban-data/dist`
- `NGINX_HOST_PORT=80`
- MySQL 只绑定 `127.0.0.1:3306`，不能从公网直接访问
- `DOUBAN_API_KEY` 留空；当前浏览器前端不会发送 `X-API-Key`，填写后页面接口会返回 401

## 4. 构建与启动

服务器需要 Node.js 18+ 构建前端。Ubuntu 可先安装发行版 Node.js，版本不足时再改用 NodeSource：

```bash
sudo apt install -y nodejs npm
node --version
npm --version
bash scripts/deploy.sh
```

部署脚本会创建持久化目录、生成种子 SQL、构建前端、启动容器，并通过 Nginx 检查 `/api/health`。验证：

```bash
docker compose ps
docker compose logs --tail=100
curl -fsS http://127.0.0.1/api/health
```

浏览器访问 `http://<ECS_PUBLIC_IP>/`。

## 5. 阿里云安全组

在 ECS 控制台的安全组入方向配置：

| 端口 | 来源 | 用途 |
|---|---|---|
| 22/TCP | 你的固定公网 IP `/32` | SSH 管理 |
| 80/TCP | `0.0.0.0/0`、`::/0` | HTTP 网站 |
| 443/TCP | 配置 HTTPS 后开放 | HTTPS 网站 |

不要添加 3306 或 5000 的公网规则。若启用了 UFW：

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 6. 更新与回滚

更新代码：

```bash
cd /opt/douban-bigdata
git pull
rm -rf /opt/douban-data/dist/*
bash scripts/deploy.sh
```

查看状态和日志：

```bash
docker compose ps
docker compose logs -f nginx backend mysql
```

停止服务不会删除数据库：

```bash
docker compose down
```

不要随意删除 `/opt/douban-data/mysql-data`。MySQL 初始化 SQL 只会在该目录为空时执行。

## 7. 域名与 HTTPS

只有公网 IP 时可先用 HTTP 上线。准备好已解析到 ECS 的域名后，再配置 HTTPS；中国大陆地域 ECS 对外提供网站服务通常还需要完成 ICP 备案。证书接入前不建议把 Compose 直接改成 443，可在宿主机反向代理或为 Compose 增加专用 TLS 配置。
