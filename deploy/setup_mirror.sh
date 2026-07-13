#!/usr/bin/env bash
# deploy/setup_mirror.sh
# -----------------------
# Fix the two image sources that block `docker compose up -d --build` on a domestic ECS:
#   1) Docker Hub (mysql, nginx, python base image) -> configure registry-mirrors
#   2) PyPI in our own Dockerfile -> already switched to mirrors.aliyun.com, see backend/Dockerfile & spark/Dockerfile
#
# Run once on the ECS as root:
#     sudo bash deploy/setup_mirror.sh
#
# Tested on: Ubuntu 22.04 / Debian 11 (other distros work the same way; systemd-managed docker).

set -euo pipefail

# ---------- 1) Choose a Docker Hub mirror ----------
# 阿里云、腾讯云、网易、中科大,任选其一;这里默认给三个,按可用性排序
# 如果 ECS 是阿里云,用阿里云镜像 mirror.aliyuncs.com 速度最快
MIRRORS=(
  "https://mirror.ccs.tencentyun.com"      # tencent cloud mirror (generic, works for any ECS)
  "https://docker.mirrors.ustc.edu.cn"     # ustc
  "https://hub-mirror.c.163.com"           # netease
)

if [[ -f /etc/docker/daemon.json ]]; then
  echo ">>> /etc/docker/daemon.json already exists:"
  cat /etc/docker/daemon.json
  echo ""
  echo -n "    overwrite with our registry-mirrors? [y/N] "
  read -r ans
  if [[ "${ans:-N}" != "y" && "${ans:-N}" != "Y" ]]; then
    echo "    skip mirror setup"
  else
    WRITE_MIRROR=1
  fi
else
  WRITE_MIRROR=1
fi

if [[ "${WRITE_MIRROR:-0}" == "1" ]]; then
  echo ">>> writing /etc/docker/daemon.json"
  sudo mkdir -p /etc/docker
  # registry-mirrors 必须是数组;阿里云 ECS 也可填 https://<你的ID>.mirror.aliyuncs.com
  cat | sudo tee /etc/docker/daemon.json >/dev/null <<'JSON'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "max-concurrent-downloads": 10,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
JSON
  sudo systemctl restart docker
  echo ">>> docker restarted"
fi

# ---------- 2) Pull a quick test to confirm Docker Hub is reachable ----------
echo ">>> smoke test: docker pull mysql:8.0 (max 5 minutes)"
sudo docker pull mysql:8.0 2>&1 | tail -n 3 || {
  echo "!! pull mysql:8.0 failed even with mirrors."
  echo "   options:"
  echo "     a) confirm ECS can reach the mirror (curl -I https://mirror.ccs.tencentyun.com/v2/)"
  echo "     b) try a different mirror from the list above"
  echo "     c) fall back to ACR / dockerhub proxy images"
}

# ---------- 3) Pip mirror check (informational) ----------
echo ">>> pip mirror check (informational)"
echo "    backend/Dockerfile & spark/Dockerfile already use mirrors.aliyun.com/pypi/simple"
echo "    if a build still fails on pip install, check the file content above and rebuild without cache:"
echo "      docker compose build --no-cache backend"

echo ""
echo ">>> done. now run your usual:"
echo "      bash scripts/deploy.sh"