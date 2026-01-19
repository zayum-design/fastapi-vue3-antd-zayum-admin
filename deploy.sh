#!/bin/bash

# Zayum Admin 部署脚本 - 模块化版本
# 这是主入口脚本，调用 deploy/ 目录中的模块化脚本

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
    echo "  -m, --modular      使用模块化部署系统 (默认)"
    echo "  -o, --original     使用原始部署脚本"
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
    echo -e "${YELLOW}模块化系统:${NC}"
    echo "  脚本已模块化处理，模块文件位于 deploy/ 目录中"
    echo "  包括: config.sh, utils.sh, backend_utils.sh, frontend_utils.sh, main.sh"
    echo ""
    echo -e "${YELLOW}注意事项:${NC}"
    echo "  • 确保系统已安装必要的开发工具"
    echo "  • 生产环境建议使用 HTTPS 和防火墙"
    echo "  • 定期备份数据库和配置文件"
}

# 显示版本信息
show_version() {
    echo -e "${BLUE}Zayum Admin 部署脚本 v2.0.0${NC}"
    echo "适用于 FastAPI + Vue3 管理系统"
    echo "项目根目录: $(pwd)"
    echo "模块目录: deploy/"
    echo "模块化版本: 已重构为模块化系统"
}

# 检查模块化系统
check_modular_system() {
    if [ ! -d "deploy" ]; then
        echo -e "${RED}❌ 模块化部署系统不存在${NC}"
        echo -e "${YELLOW}请确保 deploy/ 目录存在并包含必要的模块文件${NC}"
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

# 使用原始脚本
use_original_script() {
    echo -e "${YELLOW}⚠️  使用原始部署脚本${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # 检查原始备份文件是否存在
    if [ ! -f "deploy.sh.backup" ]; then
        echo -e "${RED}❌ 原始部署脚本备份文件不存在${NC}"
        echo -e "${YELLOW}请先备份原始 deploy.sh 文件${NC}"
        exit 1
    fi
    
    # 执行原始脚本
    ./deploy.sh.backup "$@"
}

# 主函数
main() {
    local use_modular=true
    local show_help_flag=false
    local show_version_flag=false
    local other_args=()
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help_flag=true
                shift
                ;;
            -v|--version)
                show_version_flag=true
                shift
                ;;
            -m|--modular)
                use_modular=true
                shift
                ;;
            -o|--original)
                use_modular=false
                shift
                ;;
            -a|--all|-b|--backend|-f|--frontend)
                other_args+=("$1")
                shift
                ;;
            *)
                echo -e "${RED}错误: 未知选项 '$1'${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示帮助信息
    if $show_help_flag; then
        show_help
        exit 0
    fi
    
    # 显示版本信息
    if $show_version_flag; then
        show_version
        exit 0
    fi
    
    # 根据选择执行
    if $use_modular; then
        use_modular_system "${other_args[@]}"
    else
        use_original_script "${other_args[@]}"
    fi
}

# 运行主函数
main "$@"
