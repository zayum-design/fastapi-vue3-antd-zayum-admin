#!/bin/bash

# 一键部署脚本 - FastAPI + Vue3 管理系统
# 使用方法: ./deploy.sh [选项]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}用法: $0 [选项]${NC}"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo "  -a, --all          完整部署 (后端 + 前端)"
    echo "  -b, --backend      仅部署后端"
    echo "  -f, --frontend     仅部署前端"
    echo "  -h, --help         显示此帮助信息"
    echo "  -v, --version      显示版本信息"
    echo ""
    echo -e "${YELLOW}功能说明:${NC}"
    echo "  本脚本用于自动化部署 Zayum Admin 管理系统，支持："
    echo "  - 完整部署：后端安装 + 前端启动"
    echo "  - 单独部署：仅后端或仅前端"
    echo "  - 环境检查：自动检测系统环境"
    echo "  - 配置管理：数据库、管理员等配置"
    echo ""
    echo -e "${YELLOW}示例:${NC}"
    echo "  $0                    # 交互式选择部署模式"
    echo "  $0 --all              # 完整部署系统"
    echo "  $0 --backend          # 仅部署后端"
    echo "  $0 --frontend         # 仅部署前端"
    echo "  $0 --help             # 显示帮助信息"
    echo ""
    echo -e "${YELLOW}注意事项:${NC}"
    echo "  • 确保系统已安装必要的开发工具"
    echo "  • 生产环境建议使用 HTTPS 和防火墙"
    echo "  • 定期备份数据库和配置文件"
}

# 显示版本信息
show_version() {
    echo -e "${BLUE}Zayum Admin 部署脚本 v1.0.0${NC}"
    echo "适用于 FastAPI + Vue3 管理系统"
    echo "项目根目录: $(pwd)"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 未安装，请先安装 $1${NC}"
        return 1
    fi
    return 0
}

# 检查系统环境
check_environment() {
    echo -e "${BLUE}🔍 检查系统环境...${NC}"
    
    # 检查基本命令
    check_command python3 || return 1
    check_command pip3 || return 1
    check_command node || return 1
    check_command npm || return 1
    
    echo -e "${GREEN}✅ 系统环境检查通过${NC}"
    return 0
}

# 部署后端
deploy_backend() {
    echo -e "${BLUE}🚀 开始部署后端系统...${NC}"
    echo -e "${BLUE}==========================================${NC}"
    
    if [ ! -d "backend-fastapi-app" ]; then
        echo -e "${RED}❌ 后端目录 backend-fastapi-app 不存在${NC}"
        return 1
    fi
    
    if [ ! -f "backend-fastapi-app/install.sh" ]; then
        echo -e "${RED}❌ 后端安装脚本 backend-fastapi-app/install.sh 不存在${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}执行后端安装脚本...${NC}"
    cd backend-fastapi-app
    chmod +x install.sh
    ./install.sh
    local backend_result=$?
    cd ..
    
    if [ $backend_result -eq 0 ]; then
        echo -e "${GREEN}✅ 后端部署成功${NC}"
        return 0
    else
        echo -e "${RED}❌ 后端部署失败${NC}"
        return 1
    fi
}

# 选择前端启动模式
select_frontend_mode() {
    echo -e "${BLUE}请选择前端启动模式:${NC}"
    echo -e "  ${GREEN}1${NC}) 开发者模式 (Development) - 用于开发调试"
    echo -e "  ${GREEN}2${NC}) 生产模式 (Production) - 生产环境"
    echo -e "  ${GREEN}3${NC}) 构建模式 (Build) - 构建生产版本"
    echo -e "  ${GREEN}4${NC}) 返回上级菜单"
    echo ""
    read -p "请输入选项 [1-4] (直接按回车选择默认值 1): " choice
    
    case $choice in
        1|"")
            FRONTEND_MODE="dev"
            ;;
        2)
            FRONTEND_MODE="prod"
            ;;
        3)
            FRONTEND_MODE="build"
            ;;
        4)
            return 1
            ;;
        *)
            echo -e "${RED}错误: 无效选项 '$choice'${NC}"
            select_frontend_mode
            ;;
    esac
    
    return 0
}

# 函数：交互式配置域名
configure_domain_interactive() {
    local mode="$1"  # dev 或 prod
    local default_access_domain=""
    local default_api_domain=""
    local protocol="http"
    
    if [ "$mode" = "prod" ]; then
        default_access_domain="demo.zayum.com"
        default_api_domain="api.demo.zayum.com"
        protocol="https"
    else
        default_access_domain="localhost:5666"
        default_api_domain="localhost:8000"
        protocol="http"
    fi
    
    # 直接输出到标准错误，避免污染函数返回值
    echo -e "${BLUE}请配置 ${mode} 环境域名:${NC}" >&2
    echo "" >&2
    
    # 配置访问域名（前端域名）
    echo -e "${YELLOW}1. 访问域名 (VITE_GLOB_URL) - 用户访问前端的地址${NC}" >&2
    echo -e "${YELLOW}默认值: ${default_access_domain}${NC}" >&2
    echo -e "${YELLOW}提示: 可以输入完整 URL (如 ${protocol}://example.com) 或裸域名 (如 example.com)${NC}" >&2
    echo "" >&2
    
    # 从标准输入读取，输出提示到标准错误
    read -p "请输入访问域名 (直接回车使用默认值): " access_domain >&2
    
    if [ -z "$access_domain" ]; then
        access_domain="$default_access_domain"
        echo -e "${GREEN}使用默认访问域名: $access_domain${NC}" >&2
    else
        # 去除可能的前后空格
        access_domain=$(echo "$access_domain" | xargs)
        echo -e "${GREEN}使用自定义访问域名: $access_domain${NC}" >&2
    fi
    
    # 规范化域名
    if [[ ! "$access_domain" =~ ^https?:// ]]; then
        access_domain="${protocol}://$access_domain"
    fi
    
    echo -e "${GREEN}规范化后的访问域名: $access_domain${NC}" >&2
    echo "" >&2
    
    # 配置 API 域名（后端域名）
    echo -e "${YELLOW}2. API 域名 (VITE_GLOB_API_URL) - 前端访问后端的地址${NC}" >&2
    echo -e "${YELLOW}默认值: ${default_api_domain}${NC}" >&2
    echo -e "${YELLOW}提示: 可以输入完整 URL (如 ${protocol}://api.example.com) 或裸域名 (如 api.example.com)${NC}" >&2
    echo "" >&2
    
    read -p "请输入 API 域名 (直接回车使用默认值): " api_domain >&2
    
    if [ -z "$api_domain" ]; then
        api_domain="$default_api_domain"
        echo -e "${GREEN}使用默认 API 域名: $api_domain${NC}" >&2
    else
        # 去除可能的前后空格
        api_domain=$(echo "$api_domain" | xargs)
        echo -e "${GREEN}使用自定义 API 域名: $api_domain${NC}" >&2
    fi
    
    # 规范化域名
    if [[ ! "$api_domain" =~ ^https?:// ]]; then
        api_domain="${protocol}://$api_domain"
    fi
    
    echo -e "${GREEN}规范化后的 API 域名: $api_domain${NC}" >&2
    echo "" >&2
    
    # 返回结果（只包含域名，不包含颜色代码）
    echo "$access_domain $api_domain"
}

# 函数：更新环境变量文件
update_env_file() {
    local env_file="$1"
    local access_domain="$2"
    local api_domain="$3"
    
    # 创建临时文件
    local temp_file="${env_file}.tmp"
    
    # 如果文件不存在，创建它
    if [ ! -f "$env_file" ]; then
        touch "$env_file"
    fi
    
    # 检查是否已经包含正确的环境变量
    local url_found=false
    local api_found=false
    
    # 读取文件并检查
    while IFS= read -r line; do
        # 跳过注释行和空行
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue
        
        # 检查 VITE_GLOB_URL
        if [[ "$line" =~ ^VITE_GLOB_URL=(.*)$ ]]; then
            local value="${BASH_REMATCH[1]}"
            # 去除可能的引号和空格
            value=$(echo "$value" | sed -e 's/^["'\'']//' -e 's/["'\'']$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
            if [[ "$value" == "$access_domain" ]]; then
                url_found=true
            fi
        fi
        
        # 检查 VITE_GLOB_API_URL
        if [[ "$line" =~ ^VITE_GLOB_API_URL=(.*)$ ]]; then
            local value="${BASH_REMATCH[1]}"
            # 去除可能的引号和空格
            value=$(echo "$value" | sed -e 's/^["'\'']//' -e 's/["'\'']$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
            if [[ "$value" == "$api_domain" ]]; then
                api_found=true
            fi
        fi
    done < "$env_file"
    
    # 如果环境变量已经正确设置，直接返回成功
    if $url_found && $api_found; then
        echo -e "${GREEN}✅ 环境变量已正确配置${NC}"
        return 0
    fi
    
    # 备份原始文件（只在需要修改时创建备份）
    cp "$env_file" "${env_file}.bak"
    
    # 使用更安全的方法更新环境变量
    # 先删除现有的行（如果存在）
    grep -v "^VITE_GLOB_URL=" "$env_file" > "$temp_file"
    
    # 在适当的位置插入 VITE_GLOB_URL
    # 查找 "# Web 地址（前端访问地址）" 注释，并在其下一行插入
    if grep -q "# Web 地址（前端访问地址）" "$temp_file"; then
        # 使用 sed 在注释后插入
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS 系统
            sed -i '' '/# Web 地址（前端访问地址）/a\
VITE_GLOB_URL='"${access_domain}"'
' "$temp_file"
        else
            # Linux 和其他系统
            sed -i '/# Web 地址（前端访问地址）/a\VITE_GLOB_URL='"${access_domain}" "$temp_file"
        fi
    else
        # 如果找不到注释，直接追加
        echo "VITE_GLOB_URL=${access_domain}" >> "$temp_file"
    fi
    
    # 再次处理 API URL
    grep -v "^VITE_GLOB_API_URL=" "$temp_file" > "${temp_file}2"
    
    # 在适当的位置插入 VITE_GLOB_API_URL
    # 查找 "# 接口地址（后端 API 地址）" 注释，并在其下一行插入
    if grep -q "# 接口地址（后端 API 地址）" "${temp_file}2"; then
        # 使用 sed 在注释后插入
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS 系统
            sed -i '' '/# 接口地址（后端 API 地址）/a\
VITE_GLOB_API_URL='"${api_domain}"'
' "${temp_file}2"
        else
            # Linux 和其他系统
            sed -i '/# 接口地址（后端 API 地址）/a\VITE_GLOB_API_URL='"${api_domain}" "${temp_file}2"
        fi
    else
        # 如果找不到注释，直接追加
        echo "VITE_GLOB_API_URL=${api_domain}" >> "${temp_file}2"
    fi
    
    # 替换原文件
    mv "${temp_file}2" "$env_file"
    rm -f "$temp_file"
    
    # 确保环境变量文件有正确的权限
    chmod 644 "$env_file"
    
    # 验证环境变量是否已正确写入
    echo -e "${GREEN}✅ 环境变量已正确写入 $env_file 文件${NC}"
    return 0
}

# 部署前端
deploy_frontend() {
    echo -e "${BLUE}🚀 开始部署前端系统...${NC}"
    echo -e "${BLUE}==========================================${NC}"
    
    if [ ! -d "frontend-vue-app" ]; then
        echo -e "${RED}❌ 前端目录 frontend-vue-app 不存在${NC}"
        return 1
    fi
    
    if [ ! -f "frontend-vue-app/start.sh" ]; then
        echo -e "${RED}❌ 前端启动脚本 frontend-vue-app/start.sh 不存在${NC}"
        return 1
    fi
    
    # 选择前端启动模式
    if ! select_frontend_mode; then
        echo -e "${YELLOW}取消前端部署${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}执行前端启动脚本 (模式: $FRONTEND_MODE)...${NC}"
    cd frontend-vue-app
    chmod +x start.sh
    
    # 根据选择的模式执行
    case $FRONTEND_MODE in
        "dev")
            # 开发模式：交互式配置开发环境变量
            echo -e "${YELLOW}配置开发环境...${NC}"
            
            # 确保 .env.development 文件存在
            if [ ! -f ".env.development" ]; then
                if [ -f ".env.example" ]; then
                    cp .env.example .env.development
                    echo -e "${GREEN}✓ 已创建 .env.development 文件${NC}"
                else
                    echo -e "${RED}✗ 错误: .env.example 文件不存在${NC}"
                    cd ..
                    return 1
                fi
            fi
            
            # 交互式配置域名
            domain_config=$(configure_domain_interactive "dev")
            # 使用更可靠的方法解析结果，避免awk处理特殊字符
            access_domain=$(echo "$domain_config" | cut -d' ' -f1)
            api_domain=$(echo "$domain_config" | cut -d' ' -f2-)
            
            echo -e "${GREEN}使用访问域名: $access_domain${NC}"
            echo -e "${GREEN}使用 API 域名: $api_domain${NC}"
            
            # 更新 .env.development 文件
            if update_env_file ".env.development" "$access_domain" "$api_domain"; then
                echo -e "${GREEN}✓ 开发环境配置完成${NC}"
            else
                echo -e "${RED}✗ 开发环境配置失败${NC}"
                cd ..
                return 1
            fi
            
            # 启动开发服务器
            echo -e "${YELLOW}启动开发服务器...${NC}"
            ./start.sh --dev
            ;;
        "prod")
            # 生产模式：交互式配置生产环境变量
            echo -e "${YELLOW}配置生产环境...${NC}"
            
            # 确保 .env.production 文件存在
            if [ ! -f ".env.production" ]; then
                if [ -f ".env.example" ]; then
                    cp .env.example .env.production
                    echo -e "${GREEN}✓ 已创建 .env.production 文件${NC}"
                else
                    echo -e "${RED}✗ 错误: .env.example 文件不存在${NC}"
                    cd ..
                    return 1
                fi
            fi
            
            # 交互式配置域名
            domain_config=$(configure_domain_interactive "prod")
            # 使用更可靠的方法解析结果，避免awk处理特殊字符
            access_domain=$(echo "$domain_config" | cut -d' ' -f1)
            api_domain=$(echo "$domain_config" | cut -d' ' -f2-)
            
            echo -e "${GREEN}使用访问域名: $access_domain${NC}"
            echo -e "${GREEN}使用 API 域名: $api_domain${NC}"
            
            # 更新 .env.production 文件
            if update_env_file ".env.production" "$access_domain" "$api_domain"; then
                echo -e "${GREEN}✓ 生产环境配置完成${NC}"
            else
                echo -e "${RED}✗ 生产环境配置失败${NC}"
                cd ..
                return 1
            fi
            
            # 启动生产服务器，传递环境变量避免重复配置
            echo -e "${YELLOW}启动生产服务器...${NC}"
            # 设置环境变量，这样 start.sh 可以检测到已经配置
            export VITE_GLOB_URL="$access_domain"
            export VITE_GLOB_API_URL="$api_domain"
            ./start.sh --prod
            ;;
        "build")
            # 构建模式：交互式配置生产环境变量并构建
            echo -e "${YELLOW}配置构建环境...${NC}"
            
            # 确保 .env.production 文件存在
            if [ ! -f ".env.production" ]; then
                if [ -f ".env.example" ]; then
                    cp .env.example .env.production
                    echo -e "${GREEN}✓ 已创建 .env.production 文件${NC}"
                else
                    echo -e "${RED}✗ 错误: .env.example 文件不存在${NC}"
                    cd ..
                    return 1
                fi
            fi
            
            # 交互式配置域名
            domain_config=$(configure_domain_interactive "prod")
            # 使用更可靠的方法解析结果，避免awk处理特殊字符
            access_domain=$(echo "$domain_config" | cut -d' ' -f1)
            api_domain=$(echo "$domain_config" | cut -d' ' -f2-)
            
            echo -e "${GREEN}使用访问域名: $access_domain${NC}"
            echo -e "${GREEN}使用 API 域名: $api_domain${NC}"
            
            # 更新 .env.production 文件
            if update_env_file ".env.production" "$access_domain" "$api_domain"; then
                echo -e "${GREEN}✓ 构建环境配置完成${NC}"
            else
                echo -e "${RED}✗ 构建环境配置失败${NC}"
                cd ..
                return 1
            fi
            
            # 启动构建
            echo -e "${YELLOW}开始构建应用...${NC}"
            ./start.sh --prod --build 2>/dev/null || echo "3" | ./start.sh
            ;;
        *)
            echo -e "${RED}错误: 未知前端模式 '$FRONTEND_MODE'${NC}"
            cd ..
            return 1
            ;;
    esac
    
    local frontend_result=$?
    cd ..
    
    if [ $frontend_result -eq 0 ]; then
        echo -e "${GREEN}✅ 前端部署成功 (模式: $FRONTEND_MODE)${NC}"
        return 0
    else
        echo -e "${RED}❌ 前端部署失败 (模式: $FRONTEND_MODE)${NC}"
        return 1
    fi
}

# 完整部署
deploy_all() {
    echo -e "${BLUE}🚀 开始完整部署 Zayum Admin 系统...${NC}"
    echo -e "${BLUE}==========================================${NC}"
    
    # 检查环境
    if ! check_environment; then
        echo -e "${RED}❌ 环境检查失败，请先安装必要的工具${NC}"
        exit 1
    fi
    
    # 部署后端
    if ! deploy_backend; then
        echo -e "${RED}❌ 后端部署失败，停止部署${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${BLUE}==========================================${NC}"
    echo ""
    
    # 部署前端
    if ! deploy_frontend; then
        echo -e "${RED}❌ 前端部署失败${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}🎉 完整部署完成！${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${YELLOW}📊 服务访问信息：${NC}"
    echo "后端 API 地址: http://localhost:8000"
    echo "前端开发服务器: http://localhost:5173"
    echo "Swagger 文档: http://localhost:8000/docs"
    echo ""
    echo -e "${YELLOW}🔧 管理命令：${NC}"
    echo "停止后端服务: cd backend-fastapi-app && kill \$(cat .backend_pid)"
    echo "重新启动前端: cd frontend-vue-app && ./start.sh"
    echo ""
    echo -e "${YELLOW}💡 部署说明：${NC}"
    echo "1. 后端服务已在后台运行"
    echo "2. 前端开发服务器已启动"
    echo "3. 您可以在浏览器中访问前端地址开始使用系统"
    echo "4. 生产环境建议使用 Nginx 等 Web 服务器"
}

# 交互式选择部署模式
select_deploy_mode() {
    echo -e "${BLUE}请选择部署模式:${NC}"
    echo -e "  ${GREEN}1${NC}) 完整部署 (后端 + 前端)"
    echo -e "  ${GREEN}2${NC}) 仅部署后端"
    echo -e "  ${GREEN}3${NC}) 仅部署前端"
    echo -e "  ${GREEN}4${NC}) 显示帮助信息"
    echo -e "  ${GREEN}5${NC}) 退出"
    echo ""
    read -p "请输入选项 [1-5] (直接按回车选择默认值 1): " choice
    
    case $choice in
        1|"")
            MODE="all"
            ;;
        2)
            MODE="backend"
            ;;
        3)
            MODE="frontend"
            ;;
        4)
            show_help
            exit 0
            ;;
        5)
            echo -e "${YELLOW}退出部署${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}错误: 无效选项 '$choice'${NC}"
            select_deploy_mode
            ;;
    esac
}

# 主函数
main() {
    # 解析命令行参数
    if [[ $# -gt 0 ]]; then
        while [[ $# -gt 0 ]]; do
            case $1 in
                -a|--all)
                    MODE="all"
                    shift
                    ;;
                -b|--backend)
                    MODE="backend"
                    shift
                    ;;
                -f|--frontend)
                    MODE="frontend"
                    shift
                    ;;
                -h|--help)
                    show_help
                    exit 0
                    ;;
                -v|--version)
                    show_version
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
        select_deploy_mode
    fi
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    Zayum Admin 部署脚本${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}部署模式: ${MODE}${NC}"
    echo ""
    
    # 根据模式执行部署
    case $MODE in
        "all")
            deploy_all
            ;;
        "backend")
            if ! check_environment; then
                echo -e "${RED}❌ 环境检查失败，请先安装必要的工具${NC}"
                exit 1
            fi
            deploy_backend
            ;;
        "frontend")
            if ! check_environment; then
                echo -e "${RED}❌ 环境检查失败，请先安装必要的工具${NC}"
                exit 1
            fi
            deploy_frontend
            ;;
        *)
            echo -e "${RED}错误: 未知模式 '$MODE'${NC}"
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🎯 部署完成！${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 执行主函数
main "$@"
