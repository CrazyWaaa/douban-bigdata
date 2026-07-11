#!/usr/bin/env bash
# 一键部署脚本(Windows 本地 / Linux 云通用)
#
# Windows PowerShell 用户请用 deploy.ps1 入口,这里 deploy.sh 在 Git Bash/WSL 里直接跑。

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Windows 下用 bash 跑这条,默认 DATA_ROOT 是 D 盘
if [[ -z "${DATA_ROOT:-}" ]]; then
  if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$(uname -s 2>/dev/null)" == MINGW* ]]; then
    export DATA_ROOT="D:/douban-bigdata"
  else
    export DATA_ROOT="/opt/douban-bigdata"
  fi
fi

echo ">>> DATA_ROOT = $DATA_ROOT"
mkdir -p "$DATA_ROOT"/{mysql-data,data/raw,logs/backend,dist}

# 1) 准备种子数据(JSONL -> SQL)
if [[ ! -f scripts/seed-data/01-schema.sql ]]; then
  echo ">>> generate seed data"
  python3 scripts/generate_seed_data.py
fi

# 2) 前端构建(若 dist 空)
if [[ -z "$(ls -A "$DATA_ROOT/dist" 2>/dev/null)" ]]; then
  echo ">>> build frontend"
  cd frontend
  if [[ ! -d node_modules ]]; then
    npm install
  fi
  npm run build
  cp -r dist/* "$DATA_ROOT/dist/" || true
  cd ..
fi

# 3) 启动 mysql + backend + nginx
echo ">>> docker compose up -d --build"
docker compose --env-file .env up -d --build

# 4) 健康检查
echo ">>> health check"
sleep 10
for i in 1 2 3 4 5; do
  if curl -s -f http://127.0.0.1:5000/api/health >/dev/null 2>&1; then
    echo "    [OK] backend health passed"
    break
  fi
  echo "    retry $i/5"
  sleep 3
done

echo ">>> done"
echo "    backend: http://127.0.0.1:8080"
echo "    mysql:   127.0.0.1:3306 (user=douban, db=douban)"
echo "    data:    $DATA_ROOT"