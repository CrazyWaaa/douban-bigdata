#!/usr/bin/env bash
# MySQL 初始化：创建数据库 douban 与基础账号
set -euo pipefail

DB=root
echo "MySQL root 密码默认通过 sudo mysql -u root 直连。请设置 root 密码后再继续。"
sudo mysql -u root <<'SQL'
CREATE DATABASE IF NOT EXISTS douban CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'douban'@'localhost' IDENTIFIED BY 'douban_pwd';
GRANT ALL PRIVILEGES ON douban.* TO 'douban'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "数据库 douban 已创建，应用账号 douban / douban_pwd"