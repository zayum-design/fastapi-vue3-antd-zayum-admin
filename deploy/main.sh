#!/bin/bash

# 主部署脚本 - 模块化版本 v3.0
# 整合所有模块，提供完整的部署流程

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"

# 加载所有模块
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/database_utils.sh"
source "$SCRIPT_DIR/backend_utils.sh"
source "$SCRIPT_DIR/frontend_utils.sh"

# ============================================
# 部署流程
# ============================================

# 完整部署
run_full_deploy() {
    step "START" "开始完整部署"
    
    # 检查环境
    if ! check_environment; then
        error "环境检查失败，请先安装必要的依赖"
        exit 1
    fi
    
    # 检查项目结构
    if ! check_project_structure; then
        error "项目结构检查失败"
        exit 1
    fi
    
    # 显示当前状态
    show_deploy_status
    
    # 选择部署安全模式
    local safety_mode=$(select_deployment_safety_mode)
    
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}         ${GREEN}即将开始完整部署${NC}                                   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}         部署模式: ${YELLOW}${safety_mode}${NC}                                   ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if ! confirm "确认开始部署"; then
        info "部署已取消"
        exit 0
    fi
    
    # 部署后端
    if ! deploy_backend "$safety_mode"; then
        error "后端部署失败"
        exit 1
    fi
    
    echo ""
    separator
    echo ""
    
    # 选择前端模式
    local frontend_mode=$(select_frontend_mode)
    
    if [ "$frontend_mode" = "cancel" ]; then
        warning "跳过前端部署"
    else
        # 部署前端
        if ! deploy_frontend "$frontend_mode"; then
            error "前端部署失败"
            exit 1
        fi
    fi
    
    # 保存配置
    save_config
    
    # 显示部署信息
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}              ${GREEN}🎉 部署完成！${NC}                                  ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    show_backend_info
    echo ""
    show_frontend_info "$frontend_mode"
    
    echo ""
    echo -e "${YELLOW}💡 使用提示:${NC}"
    echo "   1. 后端 API 服务将在后台运行"
    echo "   2. 前端开发服务器需要手动启动 (如果使用开发模式)"
    echo "   3. 默认管理员账号: admin / admin123"
    echo "   4. 配置文件已保存在 $PROJECT_ROOT/.deploy-config"
    echo ""
    
    success "部署流程全部完成"
}

# 仅部署后端
run_backend_deploy() {
    step "START" "开始后端部署"
    
    # 检查环境
    if ! check_environment; then
        error "环境检查失败"
        exit 1
    fi
    
    # 检查项目结构
    if ! check_project_structure; then
        error "项目结构检查失败"
        exit 1
    fi
    
    # 显示当前状态
    show_deploy_status
    
    # 选择部署安全模式
    local safety_mode=$(select_deployment_safety_mode)
    
    if ! confirm "确认开始后端部署"; then
        info "部署已取消"
        exit 0
    fi
    
    # 部署后端
    if ! deploy_backend "$safety_mode"; then
        error "后端部署失败"
        exit 1
    fi
    
    # 保存配置
    save_config
    
    # 显示信息
    echo ""
    show_backend_info
    
    success "后端部署完成"
}

# 仅部署前端
run_frontend_deploy() {
    step "START" "开始前端部署"
    
    # 检查环境
    if ! check_environment; then
        error "环境检查失败"
        exit 1
    fi
    
    # 检查项目结构
    if ! check_project_structure; then
        error "项目结构检查失败"
        exit 1
    fi
    
    # 显示当前状态
    show_deploy_status
    
    # 选择前端模式
    local frontend_mode=$(select_frontend_mode)
    
    if [ "$frontend_mode" = "cancel" ]; then
        info "部署已取消"
        exit 0
    fi
    
    if ! confirm "确认开始前端部署"; then
        info "部署已取消"
        exit 0
    fi
    
    # 部署前端
    if ! deploy_frontend "$frontend_mode"; then
        error "前端部署失败"
        exit 1
    fi
    
    # 显示信息
    echo ""
    show_frontend_info "$frontend_mode"
    
    success "前端部署完成"
}

# 仅配置环境
run_config_only() {
    step "START" "仅配置环境"
    
    # 检查项目结构
    if ! check_project_structure; then
        error "项目结构检查失败"
        exit 1
    fi
    
    # 显示当前状态
    show_deploy_status
    
    echo ""
    echo -e "${CYAN}配置选项:${NC}"
    separator
    
    local options=(
        "配置后端环境 - 数据库和 API 设置"
        "配置前端环境 - 域名和路由设置"
        "配置全部环境 - 后端 + 前端"
        "返回主菜单"
    )
    
    local choice=$(select_option "选择配置项:" "${options[@]}")
    
    case $choice in
        1)
            configure_backend_only
            save_config
            show_backend_config_summary
            ;;
        2)
            local frontend_mode=$(select_frontend_mode)
            if [ "$frontend_mode" != "cancel" ]; then
                case $frontend_mode in
                    "$FRONTEND_MODE_DEV")
                        cd "$FRONTEND_DIR"
                        configure_domain_interactive "dev"
                        update_env_file ".env.development" "$ACCESS_DOMAIN" "$API_DOMAIN" "$ATTACHMENT_DOMAIN"
                        ;;
                    "$FRONTEND_MODE_PROD"|"$FRONTEND_MODE_BUILD")
                        cd "$FRONTEND_DIR"
                        configure_domain_interactive "prod"
                        update_env_file ".env.production" "$ACCESS_DOMAIN" "$API_DOMAIN" "$ATTACHMENT_DOMAIN"
                        ;;
                esac
                cd "$PROJECT_ROOT"
                show_frontend_config_summary
            fi
            ;;
        3)
            configure_backend_only
            cd "$FRONTEND_DIR"
            configure_domain_interactive "dev"
            update_env_file ".env.development" "$ACCESS_DOMAIN" "$API_DOMAIN" "$ATTACHMENT_DOMAIN"
            configure_domain_interactive "prod"
            update_env_file ".env.production" "$ACCESS_DOMAIN" "$API_DOMAIN" "$ATTACHMENT_DOMAIN"
            cd "$PROJECT_ROOT"
            save_config
            show_backend_config_summary
            show_frontend_config_summary
            ;;
        4)
            info "返回主菜单"
            return 0
            ;;
    esac
    
    success "环境配置完成"
}

# ============================================
# 主函数
# ============================================

main() {
    # 解析命令行参数
    local deploy_mode=$(parse_arguments "$@")
    
    # 如果没有指定模式，进入交互式选择
    if [ -z "$deploy_mode" ]; then
        deploy_mode=$(select_deploy_mode)
    fi
    
    # 处理特殊返回值
    case $deploy_mode in
        "__SHOW_HELP__")
            show_help
            exit 0
            ;;
        "__EXIT__")
            echo ""
            echo -e "${YELLOW}感谢使用，再见！${NC}"
            exit 0
            ;;
    esac
    
    # 记录开始时间
    local start_time=$(date +%s)
    
    # 创建日志目录
    mkdir -p "$LOG_DIR"
    
    # 记录部署开始
    log_message "INFO" "=========================================="
    log_message "INFO" "部署开始 - 模式: $deploy_mode"
    log_message "INFO" "=========================================="
    
    # 根据模式执行
    case $deploy_mode in
        "$DEPLOY_MODE_ALL")
            run_full_deploy
            ;;
        "$DEPLOY_MODE_BACKEND")
            run_backend_deploy
            ;;
        "$DEPLOY_MODE_FRONTEND")
            run_frontend_deploy
            ;;
        "$DEPLOY_MODE_CONFIG")
            run_config_only
            ;;
        *)
            error "未知的部署模式: $deploy_mode"
            exit 1
            ;;
    esac
    
    # 计算耗时
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    # 记录部署结束
    log_message "INFO" "=========================================="
    log_message "INFO" "部署完成 - 耗时: ${minutes}分${seconds}秒"
    log_message "INFO" "=========================================="
    
    echo ""
    echo -e "${BLUE}⏱️  总耗时: ${minutes}分${seconds}秒${NC}"
    echo ""
    
    exit 0
}

# 运行主函数
main "$@"
