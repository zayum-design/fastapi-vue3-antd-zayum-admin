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

# 函数：交互式配置域名
configure_domain() {
    echo -e "${BLUE}请配置生产环境域名:${NC}"
    echo -e "${YELLOW}默认域名: api.demo.zayum.com${NC}"
    read -p "请输入域名 (直接回车使用默认值): " domain
    
    if [ -z "$domain" ]; then
        domain="api.demo.zayum.com"
        echo -e "${GREEN}使用默认域名: $domain${NC}"
    else
        echo -e "${GREEN}使用自定义域名: $domain${NC}"
    fi
    
    DOMAIN="$domain"
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
    
    # 配置指定的环境变量
    echo -e "${BLUE}正在配置生产环境变量...${NC}"
    
    # 配置 VITE_GLOB_URL
    if grep -q "^VITE_GLOB_URL=" .env.production; then
        sed -i '' "s|^VITE_GLOB_URL=.*|VITE_GLOB_URL=http://${DOMAIN}|" .env.production
    else
        echo "VITE_GLOB_URL=http://${DOMAIN}" >> .env.production
    fi
    echo -e "${GREEN}✓ 已配置 VITE_GLOB_URL=http://${DOMAIN}${NC}"
    
    # 配置 VITE_GLOB_API_URL
    if grep -q "^VITE_GLOB_API_URL=" .env.production; then
        sed -i '' "s|^VITE_GLOB_API_URL=.*|VITE_GLOB_API_URL=http://${DOMAIN}/api|" .env.production
    else
        echo "VITE_GLOB_API_URL=http://${DOMAIN}/api" >> .env.production
    fi
    echo -e "${GREEN}✓ 已配置 VITE_GLOB_API_URL=http://${DOMAIN}/api${NC}"
    
    echo -e "${GREEN}✓ 生产环境配置完成${NC}"
}

# 函数：配置开发环境域名
configure_dev_domain() {
    echo -e "${BLUE}请配置开发环境域名:${NC}"
    echo -e "${YELLOW}提示: 输入域名用于配置开发环境的 API 地址${NC}"
    read -p "请输入域名 (例如: localhost:8000): " domain
    
    if [ -z "$domain" ]; then
        echo -e "${YELLOW}未配置域名，使用默认开发环境配置${NC}"
        return
    fi
    
    echo -e "${GREEN}使用开发环境域名: $domain${NC}"
    
    # 确保 .env.development 文件存在
    if [ ! -f ".env.development" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env.development
            echo -e "${GREEN}✓ 已创建 .env.development 文件${NC}"
        else
            echo -e "${RED}✗ 错误: .env.example 文件不存在${NC}"
            return
        fi
    fi
    
    # 配置开发环境变量
    echo -e "${BLUE}正在配置开发环境变量...${NC}"
    
    # 配置 VITE_GLOB_URL
    if grep -q "^VITE_GLOB_URL=" .env.development; then
        sed -i '' "s|^VITE_GLOB_URL=.*|VITE_GLOB_URL=http://${domain}|" .env.development
    else
        echo "VITE_GLOB_URL=http://${domain}" >> .env.development
    fi
    echo -e "${GREEN}✓ 已配置 VITE_GLOB_URL=http://${domain}${NC}"
    
    # 配置 VITE_GLOB_API_URL
    if grep -q "^VITE_GLOB_API_URL=" .env.development; then
        sed -i '' "s|^VITE_GLOB_API_URL=.*|VITE_GLOB_API_URL=http://${domain}/api|" .env.development
    else
        echo "VITE_GLOB_API_URL=http://${domain}/api" >> .env.development
    fi
    echo -e "${GREEN}✓ 已配置 VITE_GLOB_API_URL=http://${domain}/api${NC}"
    
    echo -e "${GREEN}✓ 开发环境配置完成${NC}"
}

# 函数：启动开发者模式
start_dev_mode() {
    echo -e "${BLUE}启动开发者模式...${NC}"
    
    # 配置开发环境域名
    configure_dev_domain
    
    echo -e "${YELLOW}使用开发环境配置 (.env.development)${NC}"
    npm run dev
}

# 函数：启动生产模式
start_prod_mode() {
    echo -e "${BLUE}启动生产模式...${NC}"
    
    # 设置生产环境配置
    setup_production_env
    
    echo -e "${YELLOW}使用生产环境配置 (.env.production)${NC}"
    npm run dev
}

# 函数：启动构建模式
start_build_mode() {
    echo -e "${BLUE}启动构建模式...${NC}"
    
    # 设置生产环境配置
    setup_production_env
    
    echo -e "${YELLOW}使用生产环境配置构建应用...${NC}"
    npm run build
    echo -e "${GREEN}✓ 构建完成${NC}"
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
