#!/bin/bash
# 全自动数据导入脚本

cd /Users/zcy/IdeaProjects/fish-price-platform

# 激活虚拟环境
source venv/bin/activate

# 设置数据库连接
export MYSQL_DSN="mysql://root:YOUR_PASSWORD@127.0.0.1:3306/fish_prices"

# 运行导入脚本
python backend/run_auto_import.py
