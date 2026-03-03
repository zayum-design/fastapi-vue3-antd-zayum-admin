#!/bin/bash

# 数据库工具模块 - 数据库配置和管理
# 支持 MySQL、PostgreSQL、SQLite 三种数据库类型

# 加载配置
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/config.sh"

# ============================================
# 数据库类型选择
# ============================================

# 交互式选择数据库类型
select_database_type() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}              ${YELLOW}数据库类型选择${NC}                               ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${GREEN}MySQL${NC} - 流行的开源关系型数据库，适合生产环境"
    echo "   • 高性能、高可用"
    echo "   • 支持复杂的查询和事务"
    echo "   • 需要单独安装 MySQL 服务"
    echo ""
    
    echo -e "${GREEN}PostgreSQL${NC} - 功能强大的开源关系型数据库"
    echo "   • 支持高级数据类型和扩展"
    echo "   • 严格的数据完整性"
    echo "   • 需要单独安装 PostgreSQL 服务"
    echo ""
    
    echo -e "${GREEN}SQLite${NC} - 轻量级嵌入式数据库，零配置"
    echo "   • 无需单独安装服务"
    echo "   • 单文件存储，便于迁移"
    echo "   • 适合开发测试和小型应用"
    echo ""
    
    local options=(
        "MySQL - 生产环境推荐"
        "PostgreSQL - 功能丰富"
        "SQLite - 轻量快速，适合开发"
    )
    
    local choice=$(select_option "请选择数据库类型:" "${options[@]}")
    
    case $choice in
        1)
            echo "$DB_TYPE_MYSQL"
            ;;
        2)
            echo "$DB_TYPE_POSTGRESQL"
            ;;
        3)
            echo "$DB_TYPE_SQLITE"
            ;;
    esac
}

# ============================================
# MySQL 配置
# ============================================

# 配置 MySQL 数据库
configure_mysql() {
    echo ""
    step "DB-1" "MySQL 数据库配置"
    
    echo -e "${CYAN}请提供 MySQL 连接信息:${NC}"
    echo -e "${YELLOW}提示: 如果不确定，请使用默认值或咨询数据库管理员${NC}"
    echo ""
    
    # 主机地址
    MYSQL_HOST=$(prompt_input "MySQL 主机地址" "$DEFAULT_MYSQL_HOST")
    export MYSQL_HOST
    
    # 端口
    MYSQL_PORT=$(prompt_input "MySQL 端口" "$DEFAULT_MYSQL_PORT")
    export MYSQL_PORT
    
    # 用户名
    MYSQL_USER=$(prompt_input "MySQL 用户名" "$DEFAULT_MYSQL_USER" true)
    export MYSQL_USER
    
    # 密码
    MYSQL_PASSWORD=$(prompt_input "MySQL 密码" "" true true)
    export MYSQL_PASSWORD
    
    # 数据库名
    MYSQL_DB=$(prompt_input "数据库名称" "$DEFAULT_MYSQL_DB")
    export MYSQL_DB
    
    # 显示配置摘要
    echo ""
    echo -e "${CYAN}MySQL 配置摘要:${NC}"
    separator
    echo -e "  主机: ${GREEN}${MYSQL_HOST}:${MYSQL_PORT}${NC}"
    echo -e "  用户: ${GREEN}${MYSQL_USER}${NC}"
    echo -e "  密码: ${GREEN}********${NC}"
    echo -e "  数据库: ${GREEN}${MYSQL_DB}${NC}"
    separator
    
    # 确认配置
    if confirm "是否确认以上配置"; then
        success "MySQL 配置完成"
        return 0
    else
        warning "重新配置 MySQL"
        configure_mysql
    fi
}

# ============================================
# PostgreSQL 配置
# ============================================

# 配置 PostgreSQL 数据库
configure_postgresql() {
    echo ""
    step "DB-1" "PostgreSQL 数据库配置"
    
    echo -e "${CYAN}请提供 PostgreSQL 连接信息:${NC}"
    echo -e "${YELLOW}提示: 如果不确定，请使用默认值或咨询数据库管理员${NC}"
    echo ""
    
    # 主机地址
    POSTGRES_HOST=$(prompt_input "PostgreSQL 主机地址" "$DEFAULT_POSTGRES_HOST")
    export POSTGRES_HOST
    
    # 端口
    POSTGRES_PORT=$(prompt_input "PostgreSQL 端口" "$DEFAULT_POSTGRES_PORT")
    export POSTGRES_PORT
    
    # 用户名
    POSTGRES_USER=$(prompt_input "PostgreSQL 用户名" "$DEFAULT_POSTGRES_USER" true)
    export POSTGRES_USER
    
    # 密码
    POSTGRES_PASSWORD=$(prompt_input "PostgreSQL 密码" "" true true)
    export POSTGRES_PASSWORD
    
    # 数据库名
    POSTGRES_DB=$(prompt_input "数据库名称" "$DEFAULT_POSTGRES_DB")
    export POSTGRES_DB
    
    # 显示配置摘要
    echo ""
    echo -e "${CYAN}PostgreSQL 配置摘要:${NC}"
    separator
    echo -e "  主机: ${GREEN}${POSTGRES_HOST}:${POSTGRES_PORT}${NC}"
    echo -e "  用户: ${GREEN}${POSTGRES_USER}${NC}"
    echo -e "  密码: ${GREEN}********${NC}"
    echo -e "  数据库: ${GREEN}${POSTGRES_DB}${NC}"
    separator
    
    # 确认配置
    if confirm "是否确认以上配置"; then
        success "PostgreSQL 配置完成"
        return 0
    else
        warning "重新配置 PostgreSQL"
        configure_postgresql
    fi
}

# ============================================
# SQLite 配置
# ============================================

# 配置 SQLite 数据库
configure_sqlite() {
    echo ""
    step "DB-1" "SQLite 数据库配置"
    
    echo -e "${CYAN}SQLite 是零配置的嵌入式数据库${NC}"
    echo -e "${YELLOW}数据将存储在单个文件中，无需额外服务${NC}"
    echo ""
    
    # 数据库文件路径
    SQLITE_DB=$(prompt_input "SQLite 数据库文件名" "$DEFAULT_SQLITE_DB")
    export SQLITE_DB
    
    # 确保路径在后端目录下
    if [[ ! "$SQLITE_DB" =~ ^/ ]]; then
        SQLITE_DB="$BACKEND_DIR/$SQLITE_DB"
    fi
    
    # 显示配置摘要
    echo ""
    echo -e "${CYAN}SQLite 配置摘要:${NC}"
    separator
    echo -e "  数据库文件: ${GREEN}${SQLITE_DB}${NC}"
    separator
    
    # 确认配置
    if confirm "是否确认以上配置"; then
        success "SQLite 配置完成"
        return 0
    else
        warning "重新配置 SQLite"
        configure_sqlite
    fi
}

# ============================================
# 数据库配置主流程
# ============================================

# 配置数据库（主入口）
configure_database() {
    step "DB" "数据库配置"
    
    # 选择数据库类型
    DB_TYPE=$(select_database_type)
    export DB_TYPE
    
    success "选择的数据库类型: $DB_TYPE"
    
    # 根据类型配置
    case $DB_TYPE in
        mysql)
            configure_mysql
            ;;
        postgresql)
            configure_postgresql
            ;;
        sqlite)
            configure_sqlite
            ;;
        *)
            error "未知的数据库类型: $DB_TYPE"
            return 1
            ;;
    esac
    
    return 0
}

# ============================================
# 后端环境文件生成
# ============================================

# 生成后端 .env 文件
generate_backend_env() {
    local env_file="$BACKEND_DIR/.env"
    local env_mode="${1:-safe}"  # safe 或 force
    
    step "ENV" "生成后端环境配置"
    
    # 检查是否已存在
    if [ -f "$env_file" ] && [ "$env_mode" = "safe" ]; then
        warning ".env 文件已存在，跳过生成 (安全模式)"
        info "如需重新生成，请使用强制模式部署"
        return 0
    fi
    
    info "生成 $env_file 文件..."
    
    # 备份现有文件
    if [ -f "$env_file" ]; then
        cp "$env_file" "$env_file.bak.$(get_timestamp)"
        info "已备份原有配置文件"
    fi
    
    # 生成环境文件内容
    cat > "$env_file" << EOF
# Zayum Admin 后端环境配置
# 生成时间: $(get_formatted_time)
# 数据库类型: $DB_TYPE

# ============================================
# 数据库配置
# ============================================
DB_TYPE=$DB_TYPE

EOF

    # 根据数据库类型添加相应配置
    case $DB_TYPE in
        mysql)
            cat >> "$env_file" << EOF
# MySQL 配置
MYSQL_HOST=$MYSQL_HOST
MYSQL_PORT=$MYSQL_PORT
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_DB=$MYSQL_DB

# 数据库连接池配置
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

EOF
            ;;
        postgresql)
            cat >> "$env_file" << EOF
# PostgreSQL 配置
POSTGRES_HOST=$POSTGRES_HOST
POSTGRES_PORT=$POSTGRES_PORT
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB

# 数据库连接池配置
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

EOF
            ;;
        sqlite)
            cat >> "$env_file" << EOF
# SQLite 配置
SQLITE_DB=$SQLITE_DB

EOF
            ;;
    esac

    # 添加通用配置
    cat >> "$env_file" << EOF
# ============================================
# 应用配置
# ============================================
APP_NAME=Zayum Admin
APP_ENV=production
DEBUG=false

# ============================================
# 服务器配置
# ============================================
HOST=${BACKEND_HOST:-0.0.0.0}
PORT=${BACKEND_PORT:-8000}

# ============================================
# 安全配置
# ============================================
# JWT 密钥 (请修改为随机字符串)
SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || date +%s | sha256sum | base64 | head -c 32)
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# ============================================
# 日志配置
# ============================================
LOG_LEVEL=${LOG_LEVEL:-info}
LOG_DIR=logs

# ============================================
# CORS 配置
# ============================================
CORS_ORIGINS=["http://localhost:5173","http://localhost:5666","http://127.0.0.1:5173"]

# ============================================
# 附件上传配置
# ============================================
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=["jpg","jpeg","png","gif","pdf","doc","docx","xls","xlsx"]
EOF

    chmod 600 "$env_file"
    success "环境配置文件生成完成: $env_file"
    
    return 0
}

# 测试数据库连接
test_database_connection() {
    step "DB-TEST" "测试数据库连接"
    
    info "正在测试 $DB_TYPE 数据库连接..."
    
    case $DB_TYPE in
        mysql)
            if check_command mysql; then
                if mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1;" "$MYSQL_DB" &>/dev/null; then
                    success "MySQL 连接测试成功"
                    return 0
                else
                    warning "MySQL 连接测试失败，将在安装时自动创建数据库"
                    return 0
                fi
            else
                warning "未检测到 mysql 客户端命令，跳过连接测试"
                return 0
            fi
            ;;
        postgresql)
            if check_command psql; then
                export PGPASSWORD="$POSTGRES_PASSWORD"
                if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" &>/dev/null; then
                    success "PostgreSQL 连接测试成功"
                    return 0
                else
                    warning "PostgreSQL 连接测试失败，将在安装时自动创建数据库"
                    return 0
                fi
            else
                warning "未检测到 psql 客户端命令，跳过连接测试"
                return 0
            fi
            ;;
        sqlite)
            # SQLite 无需测试连接
            success "SQLite 配置正确"
            return 0
            ;;
    esac
    
    return 0
}
