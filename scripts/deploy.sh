#!/usr/bin/env bash
# \u4e00\u952e\u90e8\u7f72\u811a\u672c(Windows \u672c\u5730 / Linux \u4e91\u901a\u7528)
#
# Windows PowerShell \u7528\u6237\u8bf7\u7528 deploy.ps1 \u5165\u53e3\u3002

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Load .env so this script and Docker Compose use the same paths and ports.
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
else
  echo "ERROR: .env not found; copy .env.production.example to .env first" >&2
  exit 1
fi

# Windows \u4e0b\u7528 bash \u8dd1\u8fd9\u6761,\u9ed8\u8ba4 DATA_ROOT \u662f D \u76d8
if [[ -z "${DATA_ROOT:-}" ]]; then
  if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$(uname -s 2>/dev/null)" == MINGW* ]]; then
    export DATA_ROOT="D:/douban-bigdata"
  else
    export DATA_ROOT="/opt/douban-bigdata"
  fi
fi

export FRONTEND_DIST="${FRONTEND_DIST:-$DATA_ROOT/dist}"

echo ">>> DATA_ROOT = $DATA_ROOT"
echo ">>> FRONTEND_DIST = $FRONTEND_DIST"
mkdir -p "$DATA_ROOT"/{mysql-data,data/raw,logs/backend} "$FRONTEND_DIST"

# 1) \u51c6\u5907\u79cd\u5b50\u6570\u636e(JSONL -> SQL)
if [[ ! -f scripts/seed-data/01-schema.sql ]]; then
  echo ">>> generate seed data"
  python3 scripts/generate_seed_data.py
fi

# 2) \u524d\u7aef\u6784\u5efa(\u82e5 dist \u7a7a)
if [[ -z "$(ls -A "$FRONTEND_DIST" 2>/dev/null)" ]]; then
  echo ">>> build frontend"
  cd frontend
  if [[ ! -d node_modules ]]; then
    npm install
  fi
  npm run build
  cp -r dist/. "$FRONTEND_DIST/"
  cd ..
fi

# 3) \u542f\u52a8 mysql + backend + nginx
echo ">>> docker compose up -d --build"
docker compose --env-file .env up -d --build

# 4) \u5065\u5eb7\u68c0\u67e5
echo ">>> health check"
sleep 10
NGINX_HOST_PORT="${NGINX_HOST_PORT:-8080}"
healthy=0
for i in 1 2 3 4 5; do
  if curl -s -f "http://127.0.0.1:${NGINX_HOST_PORT}/api/health" >/dev/null 2>&1; then
    echo "    [OK] backend health passed"
    healthy=1
    break
  fi
  echo "    retry $i/5"
  sleep 3
done

if [[ "$healthy" != "1" ]]; then
  echo "ERROR: health check failed" >&2
  docker compose ps
  exit 1
fi

echo ">>> done"
echo "    site:    http://127.0.0.1:${NGINX_HOST_PORT}"
echo "    mysql:   127.0.0.1:3306 (user=douban, db=douban)"
echo "    data:    $DATA_ROOT"
