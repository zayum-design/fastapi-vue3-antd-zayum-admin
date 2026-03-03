#!/bin/bash

# 配置模块 - 本地部署配置
# 包含所有可配置项和常量定义

# ============================================
# 颜色定义
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# ============================================
# 项目路径配置
# ============================================
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend-fastapi-app"
FRONTEND_DIR="$PROJECT_ROOT/frontend-vue-app"
DEPLOY_DIR="$PROJECT_ROOT/deploy"

# ============================================
# 部署模式常量
# ============================================
DEPLOY_MODE_ALL="all"
DEPLOY_MODE_BACKEND="backend"
DEPLOY_MODE_FRONTEND="frontend"
DEPLOY_MODE_CONFIG="config"

# ============================================
# 前端模式常量
# ============================================
FRONTEND_MODE_DEV="dev"
FRONTEND_MODE_PROD="prod"
FRONTEND_MODE_BUILD="build"

# ============================================
# 数据库类型常量
# ============================================
DB_TYPE_MYSQL="mysql"
DB_TYPE_POSTGRESQL="postgresql"
DB_TYPE_SQLITE="sqlite"

# ============================================
# 默认域名配置
# ============================================
# 开发环境默认配置
DEFAULT_DEV_ACCESS_DOMAIN="localhost:5666"
DEFAULT_DEV_API_DOMAIN="localhost:8000"
DEFAULT_DEV_ATTACHMENT_DOMAIN="localhost:8000/api/common"

# 生产环境默认配置
DEFAULT_PROD_ACCESS_DOMAIN="localhost"
DEFAULT_PROD_API_DOMAIN="localhost:8000"
DEFAULT_PROD_ATTACHMENT_DOMAIN="http://localhost:8000/api/common"

# ============================================
# 默认数据库配置
# ============================================
# MySQL 默认配置
DEFAULT_MYSQL_HOST="localhost"
DEFAULT_MYSQL_PORT="3306"
DEFAULT_MYSQL_USER="root"
DEFAULT_MYSQL_DB="zayum_admin"

# PostgreSQL 默认配置
DEFAULT_POSTGRES_HOST="localhost"
DEFAULT_POSTGRES_PORT="5432"
DEFAULT_POSTGRES_USER="postgres"
DEFAULT_POSTGRES_DB="zayum_admin"

# SQLite 默认配置
DEFAULT_SQLITE_DB="db.sqlite3"

# ============================================
# 后端默认配置
# ============================================
DEFAULT_BACKEND_PORT="8000"
DEFAULT_BACKEND_HOST="0.0.0.0"
DEFAULT_LOG_LEVEL="info"

# ============================================
# 日志配置
# ============================================
LOG_DIR="$PROJECT_ROOT/logs"
DEPLOY_LOG_FILE="$LOG_DIR/deploy.log"

# ============================================
# 工具函数
# ============================================

# 获取时间戳
get_timestamp() {
    date +"%Y%m%d_%H%M%S"
}

# 获取格式化时间
get_formatted_time() {
    date +"%Y-%m-%d %H:%M:%S"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        return 1
    fi
    return 0
}

# 记录日志
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(get_formatted_time)
    
    # 确保日志目录存在
    mkdir -p "$LOG_DIR"
    
    # 写入日志文件
    echo "[$timestamp] [$level] $message" >> "$DEPLOY_LOG_FILE"
}

# 打印带颜色的消息并记录日志
print_message() {
    local color="$1"
    local prefix="$2"
    local message="$3"
    local level="${4:-INFO}"
    
    echo -e "${color}${prefix}${NC} ${message}"
    log_message "$level" "$prefix $message"
}

# 打印信息消息
info() {
    print_message "$BLUE" "ℹ️" "$1" "INFO"
}

# 打印成功消息
success() {
    print_message "$GREEN" "✅" "$1" "SUCCESS"
}

# 打印警告消息
warning() {
    print_message "$YELLOW" "⚠️" "$1" "WARNING"
}

# 打印错误消息
error() {
    print_message "$RED" "❌" "$1" "ERROR"
}

# 打印步骤标题
step() {
    local step_num="$1"
    local step_title="$2"
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  步骤 ${step_num}:${NC} ${YELLOW}${step_title}${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    log_message "STEP" "步骤 $step_num: $step_title"
}

# 分隔线
separator() {
    echo -e "${BLUE}──────────────────────────────────────────────────────────────${NC}"
}

# 确认提示（是/否）
confirm() {
    local message="$1"
    local default="${2:-y}"
    
    local prompt
    if [ "$default" = "y" ]; then
        prompt="[Y/n]"
    else
        prompt="[y/N]"
    fi
    
    while true; do
        echo -ne "${YELLOW}${message} ${prompt}? ${NC}"
        read -r response
        
        # 如果直接回车，使用默认值
        if [ -z "$response" ]; then
            response="$default"
        fi
        
        case "$response" in
            [Yy]*)
                return 0
                ;;
            [Nn]*)
                return 1
                ;;
            *)
                echo -e "${RED}请输入 y 或 n${NC}"
                ;;
        esac
    done
}

# 输入提示（带默认值）
prompt_input() {
    local message="$1"
    local default="$2"
    local required="${3:-false}"
    local secret="${4:-false}"
    
    while true; do
        if [ -n "$default" ]; then
            if [ "$secret" = true ]; then
                echo -ne "${YELLOW}${message} [默认: ********]: ${NC}"
            else
                echo -ne "${YELLOW}${message} [默认: ${default}]: ${NC}"
            fi
        else
            echo -ne "${YELLOW}${message}: ${NC}"
        fi
        
        if [ "$secret" = true ]; then
            read -rs input
            echo ""  # 换行
        else
            read -r input
        fi
        
        # 如果输入为空且有默认值，使用默认值
        if [ -z "$input" ] && [ -n "$default" ]; then
            input="$default"
        fi
        
        # 检查必填项
        if [ "$required" = true ] && [ -z "$input" ]; then
            echo -e "${RED}此项为必填项，请输入值${NC}"
            continue
        fi
        
        echo "$input"
        return 0
    done
}

# 选择菜单
select_option() {
    local title="$1"
    shift
    local options=("$@")
    local count=${#options[@]}
    
    echo ""
    echo -e "${CYAN}${title}${NC}"
    separator
    
    for i in "${!options[@]}"; do
        local num=$((i + 1))
        echo -e "  ${GREEN}${num}${NC}) ${options[$i]}"
    done
    
    echo ""
    
    while true; do
        echo -ne "${YELLOW}请选择 [1-${count}]: ${NC}"
        read -r choice
        
        # 验证输入
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "$count" ]; then
            echo "$choice"
            return 0
        else
            echo -e "${RED}无效选择，请输入 1-${count} 之间的数字${NC}"
        fi
    done
}
