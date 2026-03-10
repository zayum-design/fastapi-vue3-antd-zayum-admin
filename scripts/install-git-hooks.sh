#!/bin/bash

# =============================================================================
# Git Hooks 安装脚本
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  安装 Git Hooks${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
echo ""

# 检查 git 仓库
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ 当前目录不是 Git 仓库${NC}"
    exit 1
fi

# 项目根目录
PROJECT_ROOT=$(git rev-parse --show-toplevel)
HOOKS_SOURCE="$PROJECT_ROOT/.githooks"
HOOKS_TARGET="$PROJECT_ROOT/.git/hooks"

# 确保源目录存在
if [ ! -d "$HOOKS_SOURCE" ]; then
    echo -e "${RED}❌ 未找到 .githooks 目录${NC}"
    exit 1
fi

# 安装 hooks
for hook in "$HOOKS_SOURCE"/*; do
    if [ -f "$hook" ]; then
        hook_name=$(basename "$hook")
        cp "$hook" "$HOOKS_TARGET/$hook_name"
        chmod +x "$HOOKS_TARGET/$hook_name"
        echo -e "${GREEN}✅ 已安装: $hook_name${NC}"
    fi
done

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Git Hooks 安装完成${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}提示:${NC}"
echo "  • 每次提交前会自动运行安全检查"
echo "  • 如需跳过检查，使用: git commit --no-verify"
echo ""
