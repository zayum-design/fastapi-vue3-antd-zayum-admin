#!/bin/bash

# 检查安装锁文件是否存在
LOCK_FILE="install.lock"

if [ -f "$LOCK_FILE" ]; then
    echo "系统已安装，如需重新安装请删除 $LOCK_FILE 文件"
    exit 1
fi

echo "Starting backend with Supervisor..."
cd "$(dirname "$0")" || exit
supervisord -c supervisord.conf

echo "Backend is now running on http://localhost:8000"
