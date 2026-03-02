#!/bin/bash
# =============================================================================
# FastAPI 测试运行脚本
# =============================================================================
# 描述: 提供便捷的测试运行命令
# 用法: ./scripts/run_tests.sh [选项]
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 激活虚拟环境（如果存在）
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 打印帮助信息
print_help() {
    echo -e "${BLUE}FastAPI 测试运行脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  all                运行所有测试"
    echo "  unit               仅运行单元测试"
    echo "  integration        仅运行集成测试"
    echo "  e2e               仅运行端到端测试"
    echo "  coverage          运行测试并生成覆盖率报告"
    echo "  watch             监视模式运行测试（文件变化时自动重跑）"
    echo "  ci                CI 模式运行测试"
    echo "  help              显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 unit           # 运行单元测试"
    echo "  $0 coverage       # 生成覆盖率报告"
    echo "  $0 all -v         # 详细输出运行所有测试"
}

# 检查 pytest 是否安装
check_pytest() {
    if ! command -v pytest &> /dev/null; then
        echo -e "${RED}错误: pytest 未安装${NC}"
        echo "请先安装测试依赖: pip install pytest pytest-asyncio httpx"
        exit 1
    fi
}

# 运行所有测试
run_all_tests() {
    echo -e "${BLUE}运行所有测试...${NC}"
    pytest tests/ -v --tb=short
}

# 运行单元测试
run_unit_tests() {
    echo -e "${BLUE}运行单元测试...${NC}"
    pytest tests/unit -v -m unit --tb=short
}

# 运行集成测试
run_integration_tests() {
    echo -e "${BLUE}运行集成测试...${NC}"
    pytest tests/integration -v -m integration --tb=short
}

# 运行端到端测试
run_e2e_tests() {
    echo -e "${BLUE}运行端到端测试...${NC}"
    pytest tests/e2e -v -m e2e --tb=short
}

# 运行覆盖率测试
run_coverage() {
    echo -e "${BLUE}运行测试并生成覆盖率报告...${NC}"
    
    # 检查是否安装 pytest-cov
    if ! python -c "import pytest_cov" 2>/dev/null; then
        echo -e "${YELLOW}警告: pytest-cov 未安装，正在安装...${NC}"
        pip install pytest-cov
    fi
    
    pytest tests/ \
        --cov=app \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-report=xml:coverage.xml \
        -v
    
    echo -e "${GREEN}覆盖率报告已生成:${NC}"
    echo "  - HTML: htmlcov/index.html"
    echo "  - XML: coverage.xml"
}

# 监视模式运行测试
run_watch_mode() {
    echo -e "${BLUE}以监视模式运行测试...${NC}"
    
    # 检查是否安装 pytest-watch
    if ! command -v ptw &> /dev/null; then
        echo -e "${YELLOW}警告: pytest-watch 未安装，正在安装...${NC}"
        pip install pytest-watch
    fi
    
    ptw tests/ -- -v
}

# CI 模式运行测试
run_ci_mode() {
    echo -e "${BLUE}以 CI 模式运行测试...${NC}"
    
    # 检查是否安装 pytest-cov
    if ! python -c "import pytest_cov" 2>/dev/null; then
        pip install pytest-cov
    fi
    
    # 运行所有测试并生成报告
    pytest tests/ \
        --cov=app \
        --cov-report=xml:coverage.xml \
        --cov-report=term \
        --junitxml=test-results.xml \
        --tb=short \
        --strict-markers \
        -v
    
    echo -e "${GREEN}CI 测试完成${NC}"
}

# 主函数
main() {
    check_pytest
    
    case "${1:-all}" in
        all)
            run_all_tests
            ;;
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        e2e)
            run_e2e_tests
            ;;
        coverage)
            run_coverage
            ;;
        watch)
            run_watch_mode
            ;;
        ci)
            run_ci_mode
            ;;
        help|--help|-h)
            print_help
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            print_help
            exit 1
            ;;
    esac
}

main "$@"
