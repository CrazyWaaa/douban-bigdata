#!/usr/bin/env bash
# 一键触发 Spark ETL, 把 data/raw/*.jsonl 写回 Docker 里的 MySQL
#
# 设计:
#   - 调用 docker compose --profile etl run --rm etl
#   - 默认 dry-run: 输出 SQL 但不执行(--skip-writes)
#   - 加 --write 参数才真写库
#   - 加 --backup 参数自动备份 movie 表到 docs/backup_before_<date>.sql
#
# 用法:
#   bash scripts/update_db.sh           # dry-run
#   bash scripts/update_db.sh --write   # 真写库
#   bash scripts/update_db.sh --backup  # 写库前先备份
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

WRITE=false
BACKUP=false

for arg in "$@"; do
  case "$arg" in
    --write)  WRITE=true ;;
    --backup) BACKUP=true ;;
    -h|--help)
      sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "unknown arg: $arg"; exit 2 ;;
  esac
done

# 1. 检查 docker compose
if ! command -v docker >/dev/null 2>&1; then
  echo "[err] docker not found"; exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "[err] docker compose v2 not found"; exit 1
fi

# 2. 检查 MySQL 容器在跑
if ! docker ps --format '{{.Names}}' | grep -q '^douban-mysql$'; then
  echo "[err] douban-mysql 容器没在跑, 请先: docker compose up -d mysql"
  exit 1
fi

# 3. 检查输入文件
shopt -s nullglob
jsonls=( data/raw/*.jsonl )
shopt -u nullglob
if [ ${#jsonls[@]} -eq 0 ]; then
  echo "[err] data/raw/ 下没有 .jsonl 文件, 先跑 enrich_all_details.py"
  exit 1
fi
echo "[info] ETL 输入文件:"
for f in "${jsonls[@]}"; do echo "  - $f"; done

# 4. 备份(可选)
if [ "$BACKUP" = true ]; then
  ts=$(date +%Y%m%d_%H%M%S)
  bak="docs/backup_before_${ts}.sql"
  echo "[info] 备份 movie 表到 $bak"
  docker exec douban-mysql \
    mysqldump -u root -p"${MYSQL_ROOT_PASSWORD:-root_pwd}" douban movie > "$bak"
  echo "[ok] backup done: $bak"
fi

# 5. 触发 ETL
EXTRA=""
if [ "$WRITE" != true ]; then
  echo "[info] dry-run 模式, 加 --write 才真写库"
  EXTRA="--skip-writes"
else
  echo "[info] 写库模式, 会 UPSERT 到 MySQL"
  read -rp "确认写库? (yes/no): " ans
  if [ "$ans" != "yes" ]; then
    echo "aborted"; exit 1
  fi
fi

docker compose --profile etl run --rm etl $EXTRA
echo "[ok] ETL done"