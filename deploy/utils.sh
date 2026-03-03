#!/bin/bash

# 工具模块 - 通用工具函数
# 包含环境检查、交互式菜单、配置管理等功能

# 加载配置
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/config.sh"

# ============================================
# 帮助和版本信息
# ============================================

# 显示帮助信息
show_help() {
    echo -e "${BLUE}📖 用法: ./deploy.sh [选项]${NC}"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo -e "  ${GREEN}-a, --all${NC}          完整部署 (后端 + 前端)"
    echo -e "  ${GREEN}-b, --backend${NC}      仅部署后端"
    echo -e "  ${GREEN}-f, --frontend${NC}     仅部署前端"
    echo -e "  ${GREEN}-c, --config${NC}       仅配置环境"
    echo -e "  ${GREEN}-h, --help${NC}         显示此帮助信息"
    echo -e "  ${GREEN}-v, --version${NC}      显示版本信息"
    echo ""
    echo -e "${YELLOW}💡 使用示例:${NC}"
    echo -e "  ${CYAN}./deploy.sh${NC}              # 交互式选择部署模式"
    echo -e "  ${CYAN}./deploy.sh --all${NC}        # 一键完整部署"
    echo -e "  ${CYAN}./deploy.sh --backend${NC}    # 仅部署后端"
    echo -e "  ${CYAN}./deploy.sh --frontend${NC}   # 仅部署前端"
}

# 显示版本信息
show_version() {
    echo -e "${BLUE}📦 Zayum Admin 本地部署脚本 v3.0.0${NC}"
    echo "适用于 FastAPI + Vue3 全栈项目"
    echo "项目根目录: $PROJECT_ROOT"
}

# ============================================
# 环境检查
# ============================================

# 检查系统环境
check_environment() {
    step "1" "环境检查"
    
    local all_ok=true
    local missing_deps=()
    
    info "检查系统依赖..."
    separator
    
    # 检查 Python
    if check_command python3; then
        local py_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        success "Python 版本: $py_version"
    else
        error "Python 3 未安装"
        missing_deps+=("Python 3.8+")
        all_ok=false
    fi
    
    # 检查 pip
    if check_command pip3; then
        success "pip3 已安装"
    else
        warning "pip3 未安装 (Python 包管理器)"
        missing_deps+=("pip3")
        all_ok=false
    fi
    
    # 检查 Node.js
    if check_command node; then
        local node_version=$(node --version)
        success "Node.js 版本: $node_version"
    else
        error "Node.js 未安装"
        missing_deps+=("Node.js 16+")
        all_ok=false
    fi
    
    # 检查 npm
    if check_command npm; then
        local npm_version=$(npm --version)
        success "npm 版本: $npm_version"
    else
        warning "npm 未安装 (Node 包管理器)"
        missing_deps+=("npm")
        all_ok=false
    fi
    
    # 检查 Git
    if check_command git; then
        local git_version=$(git --version | cut -d' ' -f3)
        success "Git 版本: $git_version"
    else
        warning "Git 未安装 (版本控制工具)"
        missing_deps+=("Git")
    fi
    
    separator
    
    if [ "$all_ok" = true ]; then
        success "所有依赖检查通过"
        return 0
    else
        error "以下依赖项缺失:"
        for dep in "${missing_deps[@]}"; do
            echo -e "    ${RED}•${NC} $dep"
        done
        echo ""
        info "请安装缺失的依赖后重试"
        return 1
    fi
}

# 检查项目结构
check_project_structure() {
    step "2" "项目结构检查"
    
    local all_ok=true
    
    info "检查项目目录结构..."
    separator
    
    # 检查后端目录
    if [ -d "$BACKEND_DIR" ]; then
        success "后端目录: $BACKEND_DIR"
    else
        error "后端目录不存在: $BACKEND_DIR"
        all_ok=false
    fi
    
    # 检查前端目录
    if [ -d "$FRONTEND_DIR" ]; then
        success "前端目录: $FRONTEND_DIR"
    else
        error "前端目录不存在: $FRONTEND_DIR"
        all_ok=false
    fi
    
    # 检查后端的 install.sh
    if [ -f "$BACKEND_DIR/install.sh" ]; then
        success "后端安装脚本: install.sh"
    else
        error "后端安装脚本不存在: $BACKEND_DIR/install.sh"
        all_ok=false
    fi
    
    # 检查前端的 start.sh
    if [ -f "$FRONTEND_DIR/start.sh" ]; then
        success "前端启动脚本: start.sh"
    else
        error "前端启动脚本不存在: $FRONTEND_DIR/start.sh"
        all_ok=false
    fi
    
    separator
    
    if [ "$all_ok" = true ]; then
        success "项目结构检查通过"
        return 0
    else
        error "项目结构检查失败"
        return 1
    fi
}

# ============================================
# 交互式菜单
# ============================================

# 显示主菜单并获取选择
select_deploy_mode() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}              ${YELLOW}请选择部署模式${NC}                               ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local options=(
        "完整部署 - 后端 + 前端 (推荐首次使用)"
        "仅部署后端 - 只部署 FastAPI 后端服务"
        "仅部署前端 - 只部署 Vue3 前端应用"
        "仅配置环境 - 初始化数据库和域名配置"
        "显示帮助信息"
        "退出"
    )
    
    local choice=$(select_option "部署选项:" "${options[@]}")
    
    case $choice in
        1)
            echo "$DEPLOY_MODE_ALL"
            ;;
        2)
            echo "$DEPLOY_MODE_BACKEND"
            ;;
        3)
            echo "$DEPLOY_MODE_FRONTEND"
            ;;
        4)
            echo "$DEPLOY_MODE_CONFIG"
            ;;
        5)
            echo "__SHOW_HELP__"
            ;;
        6)
            echo "__EXIT__"
            ;;
    esac
}

# 选择前端启动模式
select_frontend_mode() {
    echo ""
    echo -e "${CYAN}请选择前端启动模式:${NC}"
    separator
    
    local options=(
        "开发模式 - 热更新，适合开发调试 (端口: 5173)"
        "生产模式 - 优化构建，适合生产环境"
        "构建模式 - 仅构建，不启动服务"
        "取消 - 返回上级菜单"
    )
    
    local choice=$(select_option "前端模式:" "${options[@]}")
    
    case $choice in
        1)
            echo "$FRONTEND_MODE_DEV"
            ;;
        2)
            echo "$FRONTEND_MODE_PROD"
            ;;
        3)
            echo "$FRONTEND_MODE_BUILD"
            ;;
        4)
            echo "cancel"
            ;;
    esac
}

# 选择部署模式（安全/强制）
select_deployment_safety_mode() {
    echo ""
    echo -e "${CYAN}请选择部署安全模式:${NC}"
    separator
    
    echo -e "${GREEN}安全模式${NC} - 跳过已存在的数据表和配置文件 (推荐)"
    echo "   适用于: 首次部署或保留现有数据"
    echo ""
    echo -e "${YELLOW}强制模式${NC} - 覆盖已存在的数据表和配置文件"
    echo "   适用于: 全新安装或重置环境"
    echo ""
    
    local options=(
        "安全模式 - 保护现有数据和配置"
        "强制模式 - 全新安装，覆盖所有"
    )
    
    local choice=$(select_option "安全选项:" "${options[@]}")
    
    case $choice in
        1)
            echo "safe"
            ;;
        2)
            echo "force"
            ;;
    esac
}

# ============================================
# 参数解析
# ============================================

# 解析命令行参数
parse_arguments() {
    local mode=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--all)
                mode="$DEPLOY_MODE_ALL"
                shift
                ;;
            -b|--backend)
                mode="$DEPLOY_MODE_BACKEND"
                shift
                ;;
            -f|--frontend)
                mode="$DEPLOY_MODE_FRONTEND"
                shift
                ;;
            -c|--config)
                mode="$DEPLOY_MODE_CONFIG"
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
                error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo "$mode"
}

# ============================================
# 部署状态管理
# ============================================

# 检查是否已部署
check_deployed() {
    local component="$1"  # backend, frontend, all
    
    case $component in
        backend)
            [ -f "$BACKEND_DIR/install.lock" ]
            ;;
        frontend)
            [ -f "$FRONTEND_DIR/install.lock" ]
            ;;
        all)
            [ -f "$BACKEND_DIR/install.lock" ] && [ -f "$FRONTEND_DIR/install.lock" ]
            ;;
        *)
            false
            ;;
    esac
}

# 显示部署状态
show_deploy_status() {
    echo ""
    echo -e "${CYAN}当前部署状态:${NC}"
    separator
    
    # 检查后端状态
    if [ -f "$BACKEND_DIR/install.lock" ]; then
        echo -e "  ${GREEN}✅ 后端${NC} - 已部署"
        echo -e "      安装时间: $(head -1 "$BACKEND_DIR/install.lock" 2>/dev/null | cut -d: -f2-)"
    else
        echo -e "  ${RED}❌ 后端${NC} - 未部署"
    fi
    
    # 检查前端状态
    if [ -f "$FRONTEND_DIR/install.lock" ]; then
        echo -e "  ${GREEN}✅ 前端${NC} - 已部署"
        echo -e "      安装时间: $(head -1 "$FRONTEND_DIR/install.lock" 2>/dev/null | cut -d: -f2-)"
    else
        echo -e "  ${RED}❌ 前端${NC} - 未部署"
    fi
    
    separator
}

# ============================================
# 配置保存和加载
# ============================================

# 保存配置到文件
save_config() {
    local config_file="$PROJECT_ROOT/.deploy-config"
    
    info "保存配置到 $config_file"
    
    cat > "$config_file" << EOF
# Zayum Admin 部署配置
# 生成时间: $(get_formatted_time)
# 请勿手动修改此文件

# 数据库配置
DB_TYPE=${DB_TYPE:-mysql}
MYSQL_HOST=${MYSQL_HOST:-localhost}
MYSQL_PORT=${MYSQL_PORT:-3306}
MYSQL_USER=${MYSQL_USER:-}
MYSQL_DB=${MYSQL_DB:-zayum_admin}
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-}
POSTGRES_DB=${POSTGRES_DB:-zayum_admin}
SQLITE_DB=${SQLITE_DB:-db.sqlite3}

# 域名配置
ACCESS_DOMAIN=${ACCESS_DOMAIN:-}
API_DOMAIN=${API_DOMAIN:-}
ATTACHMENT_DOMAIN=${ATTACHMENT_DOMAIN:-}

# 后端配置
BACKEND_PORT=${BACKEND_PORT:-8000}
BACKEND_HOST=${BACKEND_HOST:-0.0.0.0}
EOF
    
    chmod 600 "$config_file"
    success "配置已保存"
}

# 加载配置文件
load_config() {
    local config_file="$PROJECT_ROOT/.deploy-config"
    
    if [ -f "$config_file" ]; then
        info "加载配置..."
        source "$config_file"
        return 0
    fi
    
    return 1
}
