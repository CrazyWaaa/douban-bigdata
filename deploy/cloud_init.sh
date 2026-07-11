#!/usr/bin/env bash
# 云服务器一次性初始化（Ubuntu 22.04）
set -euo pipefail
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget vim nginx ufw mysql-server python3-pip
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
yes | sudo ufw enable
sudo mkdir -p /opt/douban-bigdata
sudo chown -R $USER:$USER /opt/douban-bigdata
echo "云服务器初始化完成。请 git clone 仓库到 /opt/douban-bigdata 后执行 bash scripts/bootstrap.sh"