#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：显示帮助信息
show_help() {
    echo -e "${BLUE}用法: $0 [选项]${NC}"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo "  -d, --dev      启动开发者模式 (默认)"
    echo "  -p, --prod     启动生产模式"
    echo "  -h, --help     显示此帮助信息"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo "  $0              # 启动开发者模式"
    echo "  $0 --dev        # 启动开发者模式"
    echo "  $0 --prod       # 启动生产模式"
    echo ""
}

# 函数：处理域名协议
# 如果域名已经包含 http:// 或 https://，则保持原样
# 否则添加指定的协议前缀
# 参数: $1 - 域名, $2 - 默认协议 (默认为 https)
normalize_domain() {
    local domain="$1"
    local default_protocol="${2:-https}"
    
    # 如果域名为空，直接返回
    if [ -z "$domain" ]; then
        echo ""
        return
    fi
    
    # 检查是否已经包含协议
    if [[ "$domain" =~ ^https?:// ]]; then
        # 已经包含协议，保持原样
        echo "$domain"
    else
        # 不包含协议，添加指定的协议前缀
        echo "${default_protocol}://$domain"
    fi
}

# 函数：交互式配置域名（生产环境）
configure_domain() {
    local access_domain=""
    local api_domain=""
    
    echo -e "${BLUE}请配置生产环境域名:${NC}"
    echo ""
    
    # 配置访问域名（前端域名）
    echo -e "${YELLOW}1. 访问域名 (VITE_GLOB_URL) - 用户访问前端的地址${NC}"
    echo -e "${YELLOW}默认值: https://demo.zayum.com${NC}"
    echo -e "${YELLOW}提示: 可以输入完整 URL (如 https://example.com) 或裸域名 (如 example.com)${NC}"
    
    # 检查是否有标准输入可用
    if [ -t 0 ]; then
        # 交互式模式：提示用户输入
        read -p "请输入访问域名 (直接回车使用默认值): " access_domain
    else
        # 非交互式模式：尝试从标准输入读取一行
        if read -t 1 access_domain; then
            echo -e "${GREEN}从标准输入读取访问域名: $access_domain${NC}"
        else
            access_domain=""
        fi
    fi
    
    if [ -z "$access_domain" ]; then
        access_domain="demo.zayum.com"
        echo -e "${GREEN}使用默认访问域名: $access_domain${NC}"
    else
        echo -e "${GREEN}使用自定义访问域名: $access_domain${NC}"
    fi
    
    # 规范化访问域名（处理协议）
    ACCESS_DOMAIN="$(normalize_domain "$access_domain")"
    echo -e "${GREEN}规范化后的访问域名: $ACCESS_DOMAIN${NC}"
    
    echo ""
    
    # 配置 API 域名（后端域名）
    echo -e "${YELLOW}2. API 域名 (VITE_GLOB_API_URL) - 前端访问后端的地址${NC}"
    echo -e "${YELLOW}默认值: https://api.demo.zayum.com${NC}"
    echo -e "${YELLOW}提示: 可以输入完整 URL (如 https://api.example.com) 或裸域名 (如 api.example.com)${NC}"
    
    # 检查是否有标准输入可用
    if [ -t 0 ]; then
        # 交互式模式：提示用户输入
        read -p "请输入 API 域名 (直接回车使用默认值): " api_domain
    else
        # 非交互式模式：尝试从标准输入读取一行
        if read -t 1 api_domain; then
            echo -e "${GREEN}从标准输入读取 API 域名: $api_domain${NC}"
        else
            api_domain=""
        fi
    fi
    
    if [ -z "$api_domain" ]; then
        api_domain="api.demo.zayum.com"
        echo -e "${GREEN}使用默认 API 域名: $api_domain${NC}"
    else
        echo -e "${GREEN}使用自定义 API 域名: $api_domain${NC}"
    fi
    
    # 规范化 API 域名（处理协议）
    API_DOMAIN="$(normalize_domain "$api_domain")"
    echo -e "${GREEN}规范化后的 API 域名: $API_DOMAIN${NC}"
}

# 函数：设置生产环境配置
setup_production_env() {
    echo -e "${BLUE}正在设置生产环境配置...${NC}"
    
    # 交互式配置域名
    configure_domain
    
    # 复制 .env.example 到 .env.production
    if [ -f ".env.example" ]; then
        cp .env.example .env.production
        echo -e "${GREEN}✓ 已复制 .env.example 到 .env.production${NC}"
    else
        echo -e "${RED}✗ 错误: .env.example 文件不存在${NC}"
        exit 1
    fi
    
    # 检查 .env.production 文件是否存在
    if [ ! -f ".env.production" ]; then
        echo -e "${RED}✗ 错误: .env.production 文件不存在，无法配置环境变量${NC}"
        exit 1
    fi
    
    # 配置指定的环境变量
    echo -e "${BLUE}正在配置生产环境变量...${NC}"
    
    # 配置 VITE_GLOB_URL
    if grep -q "^VITE_GLOB_URL=" .env.production; then
        sed -i '' "s|^VITE_GLOB_URL=.*|VITE_GLOB_URL=${ACCESS_DOMAIN}|" .env.production && \
        echo -e "${GREEN}✓ 已配置 VITE_GLOB_URL=${ACCESS_DOMAIN}${NC}"
    else
        echo "VITE_GLOB_URL=${ACCESS_DOMAIN}" >> .env.production && \
        echo -e "${GREEN}✓ 已配置 VITE_GLOB_URL=${ACCESS_DOMAIN}${NC}"
    fi
    
    # 配置 VITE_GLOB_API_URL
    if grep -q "^VITE_GLOB_API_URL=" .env.production; then
        sed -i '' "s|^VITE_GLOB_API_URL=.*|VITE_GLOB_API_URL=${API_DOMAIN}|" .env.production && \
        echo -e "${GREEN}✓ 已配置 VITE_GLOB_API_URL=${API_DOMAIN}${NC}"
    else
        echo "VITE_GLOB_API_URL=${API_DOMAIN}" >> .env.production && \
        echo -e "${GREEN}✓ 已配置 VITE_GLOB_API_URL=${API_DOMAIN}${NC}"
    fi
    
    echo -e "${GREEN}✓ 生产环境配置完成${NC}"
}

# 函数：配置开发环境域名
configure_dev_domain() {
    local access_domain=""
    local api_domain=""
    local normalized_access_domain=""
    local normalized_api_domain=""
    
    echo -e "${BLUE}请配置开发环境域名:${NC}"
    echo ""
    
    # 配置访问域名（前端域名）
    echo -e "${YELLOW}1. 访问域名 (VITE_GLOB_URL) - 用户访问前端的地址${NC}"
    echo -e "${YELLOW}默认值: localhost:5666${NC}"
    echo -e "${YELLOW}提示: 可以输入完整 URL (如 http://localhost:5666) 或裸域名 (如 localhost:5666)${NC}"
    
    # 检查是否有标准输入可用
    if [ -t 0 ]; then
        # 交互式模式：提示用户输入
        read -p "请输入访问域名 (直接回车使用默认值): " access_domain
    else
        # 非交互式模式：尝试从标准输入读取一行
        if read -t 1 access_domain; then
            echo -e "${GREEN}从标准输入读取访问域名: $access_domain${NC}"
        else
            access_domain=""
        fi
    fi
    
    if [ -z "$access_domain" ]; then
        access_domain="localhost:5666"
        echo -e "${GREEN}使用默认访问域名: $access_domain${NC}"
    else
        echo -e "${GREEN}使用自定义访问域名: $access_domain${NC}"
    fi
    
    # 规范化访问域名（开发环境默认使用 http 协议）
    normalized_access_domain="$(normalize_domain "$access_domain" "http")"
    echo -e "${GREEN}规范化后的访问域名: $normalized_access_domain${NC}"
    
    echo ""
    
    # 配置 API 域名（后端域名）
    echo -e "${YELLOW}2. API 域名 (VITE_GLOB_API_URL) - 前端访问后端的地址${NC}"
    echo -e "${YELLOW}默认值: localhost:8000${NC}"
    echo -e "${YELLOW}提示: 可以输入完整 URL (如 http://localhost:8000) 或裸域名 (如 localhost:8000)${NC}"
    
    # 检查是否有标准输入可用
    if [ -t 0 ]; then
        # 交互式模式：提示用户输入
        read -p "请输入 API 域名 (直接回车使用默认值): " api_domain
    else
        # 非交互式模式：尝试从标准输入读取一行
        if read -t 1 api_domain; then
            echo -e "${GREEN}从标准输入读取 API 域名: $api_domain${NC}"
        else
            api_domain=""
        fi
    fi
    
    if [ -z "$api_domain" ]; then
        api_domain="localhost:8000"
        echo -e "${GREEN}使用默认 API 域名: $api_domain${NC}"
    else
        echo -e "${GREEN}使用自定义 API 域名: $api_domain${NC}"
    fi
    
    # 规范化 API 域名（开发环境默认使用 http 协议）
    normalized_api_domain="$(normalize_domain "$api_domain" "http")"
    echo -e "${GREEN}规范化后的 API 域名: $normalized_api_domain${NC}"
    
    # 确保 .env.development 文件存在
    if [ ! -f ".env.development" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env.development
            echo -e "${GREEN}✓ 已创建 .env.development 文件${NC}"
        else
            echo -e "${RED}✗ 错误: .env.example 文件不存在${NC}"
            return 1
        fi
    fi
    
    # 检查 .env.development 文件是否存在
    if [ ! -f ".env.development" ]; then
        echo -e "${RED}✗ 错误: .env.development 文件不存在，无法配置环境变量${NC}"
        return 1
    fi
    
    # 配置开发环境变量
    echo -e "${BLUE}正在配置开发环境变量...${NC}"
    
    # 配置 VITE_GLOB_URL
    if grep -q "^VITE_GLOB_URL=" .env.development; then
        sed -i '' "s|^VITE_GLOB_URL=.*|VITE_GLOB_URL=${normalized_access_domain}|" .env.development && \
        echo -e "${GREEN}✓ 已配置 VITE_GLOB_URL=${normalized_access_domain}${NC}"
    else
        echo "VITE_GLOB_URL=${normalized_access_domain}" >> .env.development && \
        echo -e "${GREEN}✓ 已配置 VITE_GLOB_URL=${normalized_access_domain}${NC}"
    fi
    
    # 配置 VITE_GLOB_API_URL
    if grep -q "^VITE_GLOB_API_URL=" .env.development; then
        sed -i '' "s|^VITE_GLOB_API_URL=.*|VITE_GLOB_API_URL=${normalized_api_domain}|" .env.development && \
        echo -e "${GREEN}✓ 已配置 VITE_GLOB_API_URL=${normalized_api_domain}${NC}"
    else
        echo "VITE_GLOB_API_URL=${normalized_api_domain}" >> .env.development && \
        echo -e "${GREEN}✓ 已配置 VITE_GLOB_API_URL=${normalized_api_domain}${NC}"
    fi
    
    echo -e "${GREEN}✓ 开发环境配置完成${NC}"
}

# 函数：检查依赖是否已安装
check_dependencies() {
    echo -e "${BLUE}检查依赖...${NC}"
    
    # 检查 node_modules 目录是否存在
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠  node_modules 目录不存在，正在安装依赖...${NC}"
        if npm install; then
            echo -e "${GREEN}✓ 依赖安装成功${NC}"
        else
            echo -e "${RED}✗ 依赖安装失败${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}✓ 依赖已安装${NC}"
    fi
    
    # 检查 vite 是否可用
    if ! command -v vite &> /dev/null && ! npx vite --version &> /dev/null; then
        echo -e "${YELLOW}⚠  vite 命令不可用，尝试安装...${NC}"
        if npm install vite --save-dev; then
            echo -e "${GREEN}✓  vite 安装成功${NC}"
        else
            echo -e "${RED}✗  vite 安装失败${NC}"
            return 1
        fi
    fi
    
    return 0
}

# 函数：启动开发者模式
start_dev_mode() {
    echo -e "${BLUE}启动开发者模式...${NC}"
    
    # 配置开发环境域名
    configure_dev_domain
    
    # 检查依赖
    if ! check_dependencies; then
        echo -e "${RED}✗ 依赖检查失败，无法启动开发服务器${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}使用开发环境配置 (.env.development)${NC}"
    echo -e "${BLUE}启动开发服务器...${NC}"
    npm run dev
}

# 函数：启动生产模式
start_prod_mode() {
    echo -e "${BLUE}启动生产模式...${NC}"
    
    # 设置生产环境配置
    setup_production_env
    
    # 检查依赖
    if ! check_dependencies; then
        echo -e "${RED}✗ 依赖检查失败，无法启动生产服务器${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}使用生产环境配置 (.env.production)${NC}"
    echo -e "${BLUE}启动生产服务器...${NC}"
    npm run dev
}

# 函数：启动构建模式
start_build_mode() {
    echo -e "${BLUE}启动构建模式...${NC}"
    
    # 设置生产环境配置
    setup_production_env
    
    # 检查依赖
    if ! check_dependencies; then
        echo -e "${RED}✗ 依赖检查失败，无法构建应用${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}使用生产环境配置构建应用...${NC}"
    if npm run build; then
        echo -e "${GREEN}✓ 构建完成${NC}"
    else
        echo -e "${RED}✗ 构建失败${NC}"
        exit 1
    fi
}

# 函数：交互式选择模式
select_mode() {
    echo -e "${BLUE}请选择启动模式:${NC}"
    echo -e "  ${GREEN}1${NC}) 开发者模式 (Development)"
    echo -e "  ${GREEN}2${NC}) 生产模式 (Production)"
    echo -e "  ${GREEN}3${NC}) 构建模式 (Build)"
    echo -e "  ${GREEN}4${NC}) 显示帮助信息"
    echo ""
    read -p "请输入选项 [1-4] (默认: 1): " choice
    
    case $choice in
        1|"")
            MODE="dev"
            ;;
        2)
            MODE="prod"
            ;;
        3)
            MODE="build"
            ;;
        4)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}错误: 无效选项 '$choice'${NC}"
            select_mode
            ;;
    esac
}

# 解析命令行参数
if [[ $# -gt 0 ]]; then
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dev)
                MODE="dev"
                shift
                ;;
            -p|--prod)
                MODE="prod"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}错误: 未知选项 '$1'${NC}"
                show_help
                exit 1
                ;;
        esac
    done
else
    # 如果没有命令行参数，则交互式选择
    select_mode
fi

# 切换到脚本所在目录
cd "$(dirname "$0")" || exit

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    Zayum Admin Frontend 启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"

# 根据模式启动
case $MODE in
    "dev")
        start_dev_mode
        ;;
    "prod")
        start_prod_mode
        ;;
    "build")
        start_build_mode
        ;;
    *)
        echo -e "${RED}错误: 未知模式 '$MODE'${NC}"
        exit 1
        ;;
esac
