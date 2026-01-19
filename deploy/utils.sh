#!/bin/bash

# 工具模块 - 通用工具函数

# 加载配置
source "$(dirname "$0")/config.sh"

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
    echo "项目根目录: $PROJECT_ROOT"
    echo "模块目录: deploy/"
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
            echo "$DEPLOY_MODE_ALL"
            ;;
        2)
            echo "$DEPLOY_MODE_BACKEND"
            ;;
        3)
            echo "$DEPLOY_MODE_FRONTEND"
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
    
    echo "$mode"
}
