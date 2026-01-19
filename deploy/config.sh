#!/bin/bash

# 配置模块 - 本地部署配置

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径配置
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend-fastapi-app"
FRONTEND_DIR="$PROJECT_ROOT/frontend-vue-app"

# 部署模式常量
DEPLOY_MODE_ALL="all"
DEPLOY_MODE_BACKEND="backend"
DEPLOY_MODE_FRONTEND="frontend"

# 前端模式常量
FRONTEND_MODE_DEV="dev"
FRONTEND_MODE_PROD="prod"
FRONTEND_MODE_BUILD="build"

# 默认域名配置
DEFAULT_DEV_ACCESS_DOMAIN="localhost:5666"
DEFAULT_DEV_API_DOMAIN="localhost:8000"
DEFAULT_PROD_ACCESS_DOMAIN="demo.zayum.com"
DEFAULT_PROD_API_DOMAIN="api.demo.zayum.com"

# 获取时间戳
get_timestamp() {
    date +%Y%m%d_%H%M%S
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 未安装，请先安装 $1${NC}"
        return 1
    fi
    return 0
}
