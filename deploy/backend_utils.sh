#!/bin/bash

# 后端工具模块 - 后端部署相关函数
# 包含后端安装、配置和管理功能

# 加载配置
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/database_utils.sh"

# ============================================
# 后端部署
# ============================================

# 部署后端（主函数）
deploy_backend() {
    local safety_mode="${1:-safe}"
    
    step "BACKEND" "后端部署"
    
    # 检查后端目录
    if [ ! -d "$BACKEND_DIR" ]; then
        error "后端目录不存在: $BACKEND_DIR"
        return 1
    fi
    
    # 检查安装脚本
    if [ ! -f "$BACKEND_DIR/install.sh" ]; then
        error "后端安装脚本不存在: $BACKEND_DIR/install.sh"
        return 1
    fi
    
    # 检查是否已安装
    if [ -f "$BACKEND_DIR/install.lock" ] && [ "$safety_mode" = "safe" ]; then
        warning "后端已安装，检测到 install.lock 文件"
        info "文件位置: $BACKEND_DIR/install.lock"
        echo ""
        
        if confirm "是否重新部署后端? (将保留数据表)" "n"; then
            info "继续部署..."
        else
            info "跳过后端部署"
            return 0
        fi
    fi
    
    # 配置数据库
    if ! configure_database; then
        error "数据库配置失败"
        return 1
    fi
    
    # 生成环境配置文件
    if ! generate_backend_env "$safety_mode"; then
        error "环境配置文件生成失败"
        return 1
    fi
    
    # 测试数据库连接
    test_database_connection
    
    # 执行后端安装
    info "开始执行后端安装脚本..."
    cd "$BACKEND_DIR"
    chmod +x install.sh
    
    # 传递参数给 install.sh
    export TABLE_MODE="$safety_mode"
    export ENV_MODE="$safety_mode"
    
    if ! ./install.sh; then
        error "后端安装脚本执行失败"
        cd "$PROJECT_ROOT"
        return 1
    fi
    
    # 验证安装结果
    if [ -f "$BACKEND_DIR/install.lock" ]; then
        success "后端部署成功"
        info "Install lock: $BACKEND_DIR/install.lock"
        cd "$PROJECT_ROOT"
        return 0
    else
        warning "安装脚本执行完成，但未检测到 install.lock 文件"
        info "手动创建 install.lock..."
        echo "Installation completed at: $(get_formatted_time)" > "$BACKEND_DIR/install.lock"
        cd "$PROJECT_ROOT"
        return 0
    fi
}

# 仅配置后端（不执行安装）
configure_backend_only() {
    step "CONFIG" "仅配置后端环境"
    
    # 检查后端目录
    if [ ! -d "$BACKEND_DIR" ]; then
        error "后端目录不存在: $BACKEND_DIR"
        return 1
    fi
    
    # 配置数据库
    if ! configure_database; then
        error "数据库配置失败"
        return 1
    fi
    
    # 生成环境配置文件
    if ! generate_backend_env "force"; then
        error "环境配置文件生成失败"
        return 1
    fi
    
    # 测试数据库连接
    test_database_connection
    
    success "后端环境配置完成"
    info "配置文件: $BACKEND_DIR/.env"
    info "您可以手动运行后端安装脚本: cd $BACKEND_DIR && ./install.sh"
    
    return 0
}

# ============================================
# 后端管理
# ============================================

# 启动后端服务
start_backend() {
    info "启动后端服务..."
    
    cd "$BACKEND_DIR"
    
    if [ -f "start.sh" ]; then
        chmod +x start.sh
        ./start.sh &
        local pid=$!
        echo $pid > .backend_pid
        success "后端服务已启动 (PID: $pid)"
    else
        # 使用 Python 直接启动
        if [ -f "main.py" ]; then
            nohup python3 main.py > logs/backend.log 2>&1 &
            local pid=$!
            echo $pid > .backend_pid
            success "后端服务已启动 (PID: $pid)"
        else
            error "无法找到启动脚本或 main.py"
            return 1
        fi
    fi
    
    cd "$PROJECT_ROOT"
    return 0
}

# 停止后端服务
stop_backend() {
    info "停止后端服务..."
    
    cd "$BACKEND_DIR"
    
    if [ -f ".backend_pid" ]; then
        local pid=$(cat .backend_pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f .backend_pid
            success "后端服务已停止"
        else
            warning "后端服务未运行"
            rm -f .backend_pid
        fi
    else
        warning "未找到 PID 文件"
    fi
    
    cd "$PROJECT_ROOT"
    return 0
}

# 查看后端状态
status_backend() {
    cd "$BACKEND_DIR"
    
    if [ -f ".backend_pid" ]; then
        local pid=$(cat .backend_pid)
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}●${NC} 后端服务运行中 (PID: $pid)"
        else
            echo -e "${RED}○${NC} 后端服务未运行 (PID 文件存在但进程不存在)"
        fi
    else
        echo -e "${RED}○${NC} 后端服务未运行"
    fi
    
    cd "$PROJECT_ROOT"
}

# ============================================
# 信息显示
# ============================================

# 显示后端部署信息
show_backend_info() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}              ${YELLOW}后端服务信息${NC}                                 ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 读取 .env 文件中的配置
    local env_file="$BACKEND_DIR/.env"
    local port="8000"
    local host="localhost"
    
    if [ -f "$env_file" ]; then
        port=$(grep "^PORT=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "8000")
        host=$(grep "^HOST=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "localhost")
    fi
    
    echo -e "${YELLOW}🌐 访问地址:${NC}"
    echo -e "  API 地址:      ${GREEN}http://${host}:${port}${NC}"
    echo -e "  Swagger 文档:  ${GREEN}http://${host}:${port}/docs${NC}"
    echo -e "  Redoc 文档:    ${GREEN}http://${host}:${port}/redoc${NC}"
    echo ""
    
    echo -e "${YELLOW}📁 目录信息:${NC}"
    echo -e "  后端目录:      $BACKEND_DIR"
    echo -e "  环境配置:      $BACKEND_DIR/.env"
    echo -e "  日志目录:      $BACKEND_DIR/logs"
    echo ""
    
    echo -e "${YELLOW}🔧 常用命令:${NC}"
    echo -e "  启动服务:      ${CYAN}cd $BACKEND_DIR && ./start.sh${NC}"
    echo -e "  查看日志:      ${CYAN}tail -f $BACKEND_DIR/logs/app.log${NC}"
    echo -e "  安装依赖:      ${CYAN}cd $BACKEND_DIR && pip install -r requirements.txt${NC}"
    echo ""
    
    # 显示服务状态
    status_backend
}

# 显示后端配置摘要
show_backend_config_summary() {
    local env_file="$BACKEND_DIR/.env"
    
    echo ""
    echo -e "${CYAN}后端配置摘要:${NC}"
    separator
    
    if [ -f "$env_file" ]; then
        # 读取数据库类型
        local db_type=$(grep "^DB_TYPE=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "未设置")
        echo -e "  数据库类型:    ${GREEN}$db_type${NC}"
        
        case $db_type in
            mysql)
                local mysql_host=$(grep "^MYSQL_HOST=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "localhost")
                local mysql_port=$(grep "^MYSQL_PORT=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "3306")
                local mysql_db=$(grep "^MYSQL_DB=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "zayum_admin")
                echo -e "  MySQL 主机:    ${GREEN}$mysql_host:$mysql_port${NC}"
                echo -e "  MySQL 数据库:  ${GREEN}$mysql_db${NC}"
                ;;
            postgresql)
                local pg_host=$(grep "^POSTGRES_HOST=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "localhost")
                local pg_port=$(grep "^POSTGRES_PORT=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "5432")
                local pg_db=$(grep "^POSTGRES_DB=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "zayum_admin")
                echo -e "  PostgreSQL 主机: ${GREEN}$pg_host:$pg_port${NC}"
                echo -e "  PostgreSQL 数据库: ${GREEN}$pg_db${NC}"
                ;;
            sqlite)
                local sqlite_db=$(grep "^SQLITE_DB=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "db.sqlite3")
                echo -e "  SQLite 文件:   ${GREEN}$sqlite_db${NC}"
                ;;
        esac
        
        local port=$(grep "^PORT=" "$env_file" | cut -d'=' -f2 | tr -d '"' || echo "8000")
        echo -e "  服务端口:      ${GREEN}$port${NC}"
    else
        echo -e "  ${RED}未找到配置文件${NC}"
    fi
    
    separator
}
