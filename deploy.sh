#!/bin/bash

# Zayum Admin 本地部署脚本 - 模块化版本 v3.0
# 适用于 FastAPI + Vue3 全栈项目的本地开发/生产环境部署
#
# 使用方法: ./deploy.sh [选项]
#   -a, --all       完整部署 (后端 + 前端)
#   -b, --backend   仅部署后端
#   -f, --frontend  仅部署前端
#   -c, --config    仅配置环境 (不部署)
#   -h, --help      显示帮助信息
#   -v, --version   显示版本信息
#
# 交互式模式: 直接运行 ./deploy.sh 不加参数，将进入交互式菜单

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 版本信息
VERSION="3.0.0"

# 显示横幅
show_banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║${NC}     ${GREEN}Zayum Admin 本地部署脚本${NC}                    ${CYAN}v${VERSION}${NC}   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}     ${YELLOW}FastAPI + Vue3 全栈项目一键部署工具${NC}                  ${CYAN}║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# 显示帮助信息
show_help() {
    show_banner
    echo -e "${BLUE}📖 用法: $0 [选项]${NC}"
    echo ""
    echo -e "${YELLOW}选项:${NC}"
    echo -e "  ${GREEN}-a, --all${NC}          完整部署 (后端 + 前端)"
    echo -e "  ${GREEN}-b, --backend${NC}      仅部署后端"
    echo -e "  ${GREEN}-f, --frontend${NC}     仅部署前端"
    echo -e "  ${GREEN}-c, --config${NC}       仅配置环境 (初始化数据库和域名配置)"
    echo -e "  ${GREEN}-h, --help${NC}         显示此帮助信息"
    echo -e "  ${GREEN}-v, --version${NC}      显示版本信息"
    echo ""
    echo -e "${YELLOW}💡 使用示例:${NC}"
    echo -e "  ${CYAN}$0${NC}                    # 交互式选择部署模式"
    echo -e "  ${CYAN}$0 --all${NC}              # 一键完整部署"
    echo -e "  ${CYAN}$0 --backend${NC}          # 仅部署后端服务"
    echo -e "  ${CYAN}$0 --frontend${NC}         # 仅部署前端服务"
    echo -e "  ${CYAN}$0 --config${NC}           # 仅配置环境变量"
    echo ""
    echo -e "${YELLOW}🎯 功能特性:${NC}"
    echo "  • 智能环境检测 - 自动检查 Python、Node.js 等依赖"
    echo "  • 数据库向导 - 交互式配置 MySQL/PostgreSQL/SQLite"
    echo "  • 域名配置助手 - 引导式配置前后端域名"
    echo "  • 安全部署模式 - 支持安全模式/强制模式部署"
    echo "  • 完整日志记录 - 详细的部署过程记录"
    echo ""
    echo -e "${YELLOW}⚠️  注意事项:${NC}"
    echo "  • 首次部署建议使用交互式模式: ./deploy.sh"
    echo "  • 确保系统已安装 Python 3.8+ 和 Node.js 16+"
    echo "  • 生产环境建议使用 HTTPS 和防火墙"
    echo "  • 定期备份数据库和配置文件"
    echo ""
    echo -e "${BLUE}📚 详细文档: 请查看 deploy.md${NC}"
}

# 显示版本信息
show_version() {
    show_banner
    echo -e "${BLUE}📦 版本信息:${NC}"
    echo "  脚本版本: $VERSION"
    echo "  项目类型: FastAPI + Vue3 全栈应用"
    echo "  适用场景: 本地开发环境 / 本地生产环境"
    echo "  项目目录: $(pwd)"
    echo "  模块目录: deploy/"
}

# 检查模块化系统
check_modular_system() {
    if [ ! -d "deploy" ]; then
        echo -e "${RED}❌ 模块化部署系统不存在${NC}"
        echo -e "${YELLOW}💡 请确保 deploy/ 目录存在并包含必要的模块文件${NC}"
        return 1
    fi
    
    # 检查必要的模块文件
    local required_files=("config.sh" "utils.sh" "backend_utils.sh" "frontend_utils.sh" "main.sh")
    for file in "${required_files[@]}"; do
        if [ ! -f "deploy/$file" ]; then
            echo -e "${RED}❌ 模块文件 deploy/$file 不存在${NC}"
            return 1
        fi
    done
    
    # 检查文件权限
    for file in "${required_files[@]}"; do
        if [ ! -x "deploy/$file" ]; then
            chmod +x "deploy/$file"
        fi
    done
    
    return 0
}

# 使用模块化系统
use_modular_system() {
    if ! check_modular_system; then
        echo -e "${RED}❌ 模块化系统检查失败，无法继续${NC}"
        exit 1
    fi
    
    # 执行模块化主脚本
    ./deploy/main.sh "$@"
}

# 主函数
main() {
    # 如果没有参数，显示横幅并进入交互模式
    if [ $# -eq 0 ]; then
        show_banner
    fi
    
    # 解析命令行参数
    local other_args=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                show_version
                exit 0
                ;;
            -a|--all|-b|--backend|-f|--frontend|-c|--config)
                other_args+=("$1")
                shift
                ;;
            *)
                echo -e "${RED}❌ 错误: 未知选项 '$1'${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 使用模块化系统执行
    use_modular_system "${other_args[@]}"
}

# 运行主函数
main "$@"
