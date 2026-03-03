#!/bin/bash

# 前端工具模块 - 前端部署相关函数
# 包含前端环境配置、构建和启动功能

# 加载配置
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/config.sh"

# ============================================
# 域名配置
# ============================================

# 交互式配置域名
configure_domain_interactive() {
    local mode="$1"  # dev 或 prod
    
    local default_access_domain=""
    local default_api_domain=""
    local default_attachment_domain=""
    local protocol="http"
    
    if [ "$mode" = "prod" ]; then
        default_access_domain="$DEFAULT_PROD_ACCESS_DOMAIN"
        default_api_domain="$DEFAULT_PROD_API_DOMAIN"
        default_attachment_domain="$DEFAULT_PROD_ATTACHMENT_DOMAIN"
    else
        default_access_domain="$DEFAULT_DEV_ACCESS_DOMAIN"
        default_api_domain="$DEFAULT_DEV_API_DOMAIN"
        default_attachment_domain="$DEFAULT_DEV_ATTACHMENT_DOMAIN"
    fi
    
    echo ""
    echo -e "${CYAN}配置 ${mode} 环境域名:${NC}"
    separator
    
    echo -e "${YELLOW}💡 提示:${NC}"
    echo "   - 可以输入完整 URL (如 http://example.com)"
    echo "   - 或直接输入域名 (如 example.com)"
    echo "   - 直接按回车使用默认值"
    echo ""
    
    # 访问域名
    echo -e "${BLUE}1. 访问域名 (前端页面访问地址)${NC}"
    ACCESS_DOMAIN=$(prompt_input "访问域名" "$default_access_domain")
    
    # 规范化域名
    if [[ ! "$ACCESS_DOMAIN" =~ ^https?:// ]]; then
        ACCESS_DOMAIN="${protocol}://$ACCESS_DOMAIN"
    fi
    
    # API 域名
    echo ""
    echo -e "${BLUE}2. API 域名 (后端接口地址)${NC}"
    API_DOMAIN=$(prompt_input "API 域名" "$default_api_domain")
    
    if [[ ! "$API_DOMAIN" =~ ^https?:// ]]; then
        API_DOMAIN="${protocol}://$API_DOMAIN"
    fi
    
    # 附件域名
    echo ""
    echo -e "${BLUE}3. 附件域名 (文件上传/头像等)${NC}"
    ATTACHMENT_DOMAIN=$(prompt_input "附件域名" "$default_attachment_domain")
    
    if [[ ! "$ATTACHMENT_DOMAIN" =~ ^https?:// ]]; then
        ATTACHMENT_DOMAIN="${protocol}://$ATTACHMENT_DOMAIN"
    fi
    
    # 显示配置摘要
    echo ""
    echo -e "${CYAN}域名配置摘要:${NC}"
    separator
    echo -e "  访问域名:      ${GREEN}$ACCESS_DOMAIN${NC}"
    echo -e "  API 域名:      ${GREEN}$API_DOMAIN${NC}"
    echo -e "  附件域名:      ${GREEN}$ATTACHMENT_DOMAIN${NC}"
    separator
    
    if confirm "是否确认以上配置"; then
        success "域名配置完成"
    else
        warning "重新配置域名"
        configure_domain_interactive "$mode"
    fi
}

# ============================================
# 环境文件管理
# ============================================

# 更新环境文件
update_env_file() {
    local env_file="$1"
    local access_domain="$2"
    local api_domain="$3"
    local attachment_domain="$4"
    
    info "更新 $env_file 文件..."
    
    # 创建临时文件
    local temp_file="${env_file}.tmp"
    
    # 如果文件不存在，创建基础文件
    if [ ! -f "$env_file" ]; then
        touch "$env_file"
    fi
    
    # 读取并更新文件
    local url_found=false
    local api_found=false
    local attachment_found=false
    
    # 复制文件内容，跳过旧的变量定义
    while IFS= read -r line; do
        # 跳过旧的环境变量定义
        if [[ "$line" =~ ^VITE_GLOB_URL= ]]; then
            url_found=true
            continue
        fi
        if [[ "$line" =~ ^VITE_GLOB_API_URL= ]]; then
            api_found=true
            continue
        fi
        if [[ "$line" =~ ^VITE_GLOB_ATTACHMENT_URL= ]]; then
            attachment_found=true
            continue
        fi
        echo "$line" >> "$temp_file"
    done < "$env_file"
    
    # 添加新的环境变量
    echo "" >> "$temp_file"
    echo "# API 配置 - 生成时间: $(get_formatted_time)" >> "$temp_file"
    echo "VITE_GLOB_URL=$access_domain" >> "$temp_file"
    echo "VITE_GLOB_API_URL=$api_domain" >> "$temp_file"
    echo "VITE_GLOB_ATTACHMENT_URL=$attachment_domain" >> "$temp_file"
    
    # 添加路由前缀配置（如果不存在）
    if ! grep -q "VITE_ADMIN_ROUTE_PREFIX" "$temp_file"; then
        echo "" >> "$temp_file"
        echo "# 路由配置" >> "$temp_file"
        echo "VITE_ADMIN_ROUTE_PREFIX=admin" >> "$temp_file"
        echo "VITE_USER_ROUTE_PREFIX=user" >> "$temp_file"
        echo "VITE_WEB_ROUTE_PREFIX=web" >> "$temp_file"
    fi
    
    # 替换原文件
    mv "$temp_file" "$env_file"
    chmod 644 "$env_file"
    
    success "环境文件更新完成"
    return 0
}

# ============================================
# 前端部署
# ============================================

# 部署前端（主函数）
deploy_frontend() {
    local frontend_mode="$1"
    
    step "FRONTEND" "前端部署"
    
    # 检查前端目录
    if [ ! -d "$FRONTEND_DIR" ]; then
        error "前端目录不存在: $FRONTEND_DIR"
        return 1
    fi
    
    # 检查启动脚本
    if [ ! -f "$FRONTEND_DIR/start.sh" ]; then
        error "前端启动脚本不存在: $FRONTEND_DIR/start.sh"
        return 1
    fi
    
    # 检查是否已安装
    if [ -f "$FRONTEND_DIR/install.lock" ]; then
        warning "前端已安装，检测到 install.lock 文件"
        info "文件位置: $FRONTEND_DIR/install.lock"
        echo ""
        
        if confirm "是否重新部署前端?" "n"; then
            info "继续部署..."
        else
            info "跳过前端部署"
            return 0
        fi
    fi
    
    cd "$FRONTEND_DIR"
    chmod +x start.sh
    
    # 根据模式执行
    case $frontend_mode in
        "$FRONTEND_MODE_DEV")
            deploy_frontend_dev
            ;;
        "$FRONTEND_MODE_PROD")
            deploy_frontend_prod
            ;;
        "$FRONTEND_MODE_BUILD")
            deploy_frontend_build
            ;;
        *)
            error "未知的前端模式: $frontend_mode"
            cd "$PROJECT_ROOT"
            return 1
            ;;
    esac
    
    local result=$?
    
    if [ $result -eq 0 ]; then
        # 创建 install.lock
        echo "Frontend installation completed at: $(get_formatted_time)" > "$FRONTEND_DIR/install.lock"
        echo "Mode: $frontend_mode" >> "$FRONTEND_DIR/install.lock"
        success "前端部署成功"
        cd "$PROJECT_ROOT"
        return 0
    else
        error "前端部署失败"
        cd "$PROJECT_ROOT"
        return 1
    fi
}

# 开发模式部署
deploy_frontend_dev() {
    echo ""
    info "配置开发环境..."
    
    # 确保 .env.development 文件存在
    if [ ! -f ".env.development" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env.development
            info "已创建 .env.development 文件"
        else
            touch .env.development
            info "已创建空的 .env.development 文件"
        fi
    fi
    
    # 配置域名
    configure_domain_interactive "dev"
    
    # 更新环境文件
    if ! update_env_file ".env.development" "$ACCESS_DOMAIN" "$API_DOMAIN" "$ATTACHMENT_DOMAIN"; then
        error "开发环境配置失败"
        return 1
    fi
    
    # 安装依赖
    info "安装前端依赖..."
    if ! npm install; then
        error "npm install 失败"
        return 1
    fi
    
    success "开发环境配置完成"
    
    # 提示用户如何启动
    echo ""
    echo -e "${CYAN}开发服务器启动说明:${NC}"
    separator
    echo -e "${YELLOW}前端开发服务器需要手动启动${NC}"
    echo ""
    echo -e "启动命令: ${GREEN}cd $FRONTEND_DIR && ./start.sh --dev${NC}"
    echo "或:       ${GREEN}cd $FRONTEND_DIR && npm run dev${NC}"
    echo ""
    echo -e "访问地址: ${GREEN}http://localhost:5173${NC}"
    echo ""
    
    if confirm "是否立即启动开发服务器"; then
        ./start.sh --dev
    else
        info "您可以稍后手动启动开发服务器"
    fi
    
    return 0
}

# 生产模式部署
deploy_frontend_prod() {
    echo ""
    info "配置生产环境..."
    
    # 确保 .env.production 文件存在
    if [ ! -f ".env.production" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env.production
            info "已创建 .env.production 文件"
        else
            touch .env.production
            info "已创建空的 .env.production 文件"
        fi
    fi
    
    # 配置域名
    configure_domain_interactive "prod"
    
    # 更新环境文件
    if ! update_env_file ".env.production" "$ACCESS_DOMAIN" "$API_DOMAIN" "$ATTACHMENT_DOMAIN"; then
        error "生产环境配置失败"
        return 1
    fi
    
    # 安装依赖
    info "安装前端依赖..."
    if ! npm install; then
        error "npm install 失败"
        return 1
    fi
    
    success "生产环境配置完成"
    
    # 构建
    info "构建生产版本..."
    if ! npm run build; then
        error "构建失败"
        return 1
    fi
    
    success "生产版本构建完成"
    
    # 提示用户
    echo ""
    echo -e "${CYAN}生产环境部署说明:${NC}"
    separator
    echo -e "${YELLOW}构建产物位于 dist/ 目录${NC}"
    echo ""
    echo -e "您可以将 dist/ 目录部署到任何静态文件服务器:"
    echo -e "  • Nginx"
    echo -e "  • Apache"
    echo -e "  • CDN"
    echo -e "  • 云存储"
    echo ""
    
    return 0
}

# 构建模式部署
deploy_frontend_build() {
    echo ""
    info "配置构建环境..."
    
    # 确保 .env.production 文件存在
    if [ ! -f ".env.production" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env.production
            info "已创建 .env.production 文件"
        else
            touch .env.production
            info "已创建空的 .env.production 文件"
        fi
    fi
    
    # 配置域名
    configure_domain_interactive "prod"
    
    # 更新环境文件
    if ! update_env_file ".env.production" "$ACCESS_DOMAIN" "$API_DOMAIN" "$ATTACHMENT_DOMAIN"; then
        error "构建环境配置失败"
        return 1
    fi
    
    # 安装依赖
    info "安装前端依赖..."
    if ! npm install; then
        error "npm install 失败"
        return 1
    fi
    
    success "构建环境配置完成"
    
    # 构建
    info "开始构建..."
    if ! npm run build; then
        error "构建失败"
        return 1
    fi
    
    success "构建完成"
    info "构建产物: $FRONTEND_DIR/dist"
    
    return 0
}

# ============================================
# 信息显示
# ============================================

# 显示前端部署信息
show_frontend_info() {
    local frontend_mode="${1:-dev}"
    
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}              ${YELLOW}前端服务信息${NC}                                 ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 确定环境文件
    local env_file=""
    local default_url=""
    
    case $frontend_mode in
        "$FRONTEND_MODE_DEV")
            env_file=".env.development"
            default_url="http://localhost:5173"
            ;;
        "$FRONTEND_MODE_PROD"|"$FRONTEND_MODE_BUILD")
            env_file=".env.production"
            default_url="http://localhost"
            ;;
    esac
    
    # 读取环境变量
    local vite_url=""
    local admin_prefix="admin"
    
    if [ -n "$env_file" ] && [ -f "$FRONTEND_DIR/$env_file" ]; then
        vite_url=$(grep "^VITE_GLOB_URL=" "$FRONTEND_DIR/$env_file" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        admin_prefix=$(grep "^VITE_ADMIN_ROUTE_PREFIX=" "$FRONTEND_DIR/$env_file" | cut -d'=' -f2- | tr -d '"' | tr -d "'" || echo "admin")
    fi
    
    # 构建访问地址
    local admin_login_url=""
    if [ -n "$vite_url" ]; then
        if [[ "$vite_url" != */ ]]; then
            vite_url="$vite_url/"
        fi
        admin_login_url="${vite_url}${admin_prefix}/login"
    else
        admin_login_url="${default_url}/${admin_prefix}/login"
    fi
    
    echo -e "${YELLOW}🌐 访问地址:${NC}"
    echo -e "  后台登录:      ${GREEN}$admin_login_url${NC}"
    echo -e "  默认账号:      ${CYAN}admin / admin123${NC}"
    echo ""
    
    echo -e "${YELLOW}📁 目录信息:${NC}"
    echo -e "  前端目录:      $FRONTEND_DIR"
    echo -e "  环境配置:      $FRONTEND_DIR/$env_file"
    case $frontend_mode in
        "$FRONTEND_MODE_PROD"|"$FRONTEND_MODE_BUILD")
            echo -e "  构建目录:      $FRONTEND_DIR/dist"
            ;;
    esac
    echo ""
    
    echo -e "${YELLOW}🔧 常用命令:${NC}"
    echo -e "  开发模式:      ${CYAN}cd $FRONTEND_DIR && ./start.sh --dev${NC}"
    echo -e "  构建生产版:    ${CYAN}cd $FRONTEND_DIR && npm run build${NC}"
    echo -e "  安装依赖:      ${CYAN}cd $FRONTEND_DIR && npm install${NC}"
    echo ""
}

# 显示前端配置摘要
show_frontend_config_summary() {
    echo ""
    echo -e "${CYAN}前端配置摘要:${NC}"
    separator
    
    # 检查开发环境配置
    if [ -f "$FRONTEND_DIR/.env.development" ]; then
        local dev_url=$(grep "^VITE_GLOB_URL=" "$FRONTEND_DIR/.env.development" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        echo -e "  开发环境:      ${GREEN}${dev_url:-未配置}${NC}"
    else
        echo -e "  开发环境:      ${YELLOW}未配置${NC}"
    fi
    
    # 检查生产环境配置
    if [ -f "$FRONTEND_DIR/.env.production" ]; then
        local prod_url=$(grep "^VITE_GLOB_URL=" "$FRONTEND_DIR/.env.production" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        echo -e "  生产环境:      ${GREEN}${prod_url:-未配置}${NC}"
    else
        echo -e "  生产环境:      ${YELLOW}未配置${NC}"
    fi
    
    separator
}
