#!/bin/bash

# 主部署脚本 - 模块化版本
# 使用方法: ./main.sh [选项]
# 选项: -a, --all (完整部署) | -b, --backend (仅后端) | -f, --frontend (仅前端)

set -e

# 加载所有模块
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/utils.sh"
source "$SCRIPT_DIR/backend_utils.sh"
source "$SCRIPT_DIR/frontend_utils.sh"

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
    
    # 选择前端模式
    frontend_mode=$(select_frontend_mode)
    if [ "$frontend_mode" = "cancel" ]; then
        echo -e "${YELLOW}取消前端部署${NC}"
        return 0
    fi
    
    # 部署前端
    if ! deploy_frontend "$frontend_mode"; then
        echo -e "${RED}❌ 前端部署失败${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}🎉 完整部署完成！${NC}"
    echo -e "${BLUE}==========================================${NC}"
    
    # 显示部署信息
    show_backend_info
    echo ""
    show_frontend_info "$frontend_mode"
    echo ""
    
    echo -e "${YELLOW}💡 部署说明：${NC}"
    echo "1. 后端服务已在后台运行"
    echo "2. 前端开发服务器已启动"
    echo "3. 您可以在浏览器中访问前端地址开始使用系统"
    echo "4. 生产环境建议使用 Nginx 等 Web 服务器"
}

# 主函数
main() {
    # 解析命令行参数
    DEPLOY_MODE=$(parse_arguments "$@")
    
    # 交互式选择标志
    local interactive=false
    
    # 如果没有指定部署模式，则交互式选择
    if [ -z "$DEPLOY_MODE" ]; then
        interactive=true
        DEPLOY_MODE=$(select_deploy_mode)
    fi

    # 处理特殊返回值
    if [ "$DEPLOY_MODE" = "__SHOW_HELP__" ]; then
        show_help
        exit 0
    fi
    
    if [ "$DEPLOY_MODE" = "__EXIT__" ]; then
        echo -e "${YELLOW}退出部署${NC}"
        exit 0
    fi

    # 只在非交互式模式下显示标题
    if [ "$interactive" = false ]; then
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}    Zayum Admin 部署脚本${NC}"
        echo -e "${BLUE}========================================${NC}"
    fi
    
    echo -e "${YELLOW}部署模式: ${DEPLOY_MODE}${NC}"
    echo ""
    
    # 根据模式执行部署
    case $DEPLOY_MODE in
        "$DEPLOY_MODE_ALL")
            deploy_all
            ;;
        "$DEPLOY_MODE_BACKEND")
            if ! check_environment; then
                echo -e "${RED}❌ 环境检查失败，请先安装必要的工具${NC}"
                exit 1
            fi
            deploy_backend
            echo ""
            show_backend_info
            ;;
        "$DEPLOY_MODE_FRONTEND")
            if ! check_environment; then
                echo -e "${RED}❌ 环境检查失败，请先安装必要的工具${NC}"
                exit 1
            fi
            frontend_mode=$(select_frontend_mode)
            if [ "$frontend_mode" = "cancel" ]; then
                echo -e "${YELLOW}取消前端部署${NC}"
                exit 0
            fi
            deploy_frontend "$frontend_mode"
            echo ""
            show_frontend_info "$frontend_mode"
            ;;
        *)
            echo -e "${RED}错误: 未知模式 '$DEPLOY_MODE'${NC}"
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🎯 部署完成！${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 运行主函数
main "$@"
