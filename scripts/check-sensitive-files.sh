#!/bin/bash

# =============================================================================
# 敏感信息检查脚本
# 用于检测项目中是否有敏感文件被跟踪或即将被提交
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 退出码
EXIT_SUCCESS=0
EXIT_ERROR=1

# 敏感文件/目录模式
SENSITIVE_PATTERNS=(
    # 环境配置
    '\.env$'
    '\.env\.local$'
    '\.env\.(development|production|test)\.local$'
    
    # 密钥文件
    '\.pem$'
    '\.key$'
    '\.crt$'
    '\.p12$'
    '\.pfx$'
    'id_rsa$'
    'id_dsa$'
    'id_ecdsa$'
    'id_ed25519$'
    
    # 密码文件
    '\.password$'
    '\.secret$'
    
    # 数据库文件
    '\.sqlite3?$'
    '\.db$'
    
    # 私有部署
    'deploy-private'
    'push-private'
    'zayum-deploy-private'
    'private/'
    
    # 日志文件
    '\.log$'
)

# 敏感内容模式
SENSITIVE_CONTENT_PATTERNS=(
    'password\s*=\s*["\''][^"\'']{3,}["\'']'
    'secret\s*=\s*["\''][^"\'']{8,}["\'']'
    'api_key\s*=\s*["\''][^"\'']{10,}["\'']'
    'token\s*=\s*["\''][^"\'']{10,}["\'']'
    'private_key\s*=\s*["\''][^"\'']{20,}["\'']'
    '-----BEGIN\s+(RSA|DSA|EC|OPENSSH)\s+PRIVATE\s+KEY-----'
    'AKIA[0-9A-Z]{16}'  # AWS Access Key
    'ghp_[a-zA-Z0-9]{36}'  # GitHub Token
    'glpat-[a-zA-Z0-9\-]{20}'  # GitLab Token
    'sk-[a-zA-Z0-9]{48}'  # OpenAI API Key
)

# 打印函数
print_header() {
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查 git 是否初始化
check_git() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "当前目录不是 Git 仓库"
        exit $EXIT_ERROR
    fi
}

# 检查已跟踪的敏感文件
check_tracked_sensitive_files() {
    print_header "检查已跟踪的敏感文件"
    
    local found=0
    local tracked_files=$(git ls-files)
    
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        local matches=$(echo "$tracked_files" | grep -E "$pattern" || true)
        if [ -n "$matches" ]; then
            if [ $found -eq 0 ]; then
                print_error "发现以下敏感文件已被 Git 跟踪："
                echo ""
            fi
            echo "$matches" | while read -r file; do
                print_error "  - $file"
            done
            found=1
        fi
    done
    
    if [ $found -eq 0 ]; then
        print_success "未发现已跟踪的敏感文件"
    fi
    
    return $found
}

# 检查暂存区的敏感文件
check_staged_sensitive_files() {
    print_header "检查暂存区的敏感文件"
    
    local found=0
    local staged_files=$(git diff --cached --name-only --diff-filter=A)
    
    if [ -z "$staged_files" ]; then
        print_info "暂存区没有新增文件"
        return 0
    fi
    
    for pattern in "${SENSITIVE_PATTERNS[@]}"; do
        local matches=$(echo "$staged_files" | grep -E "$pattern" || true)
        if [ -n "$matches" ]; then
            if [ $found -eq 0 ]; then
                print_error "发现以下敏感文件在暂存区："
                echo ""
            fi
            echo "$matches" | while read -r file; do
                print_error "  - $file"
            done
            found=1
        fi
    done
    
    if [ $found -eq 0 ]; then
        print_success "暂存区未发现敏感文件"
    fi
    
    return $found
}

# 检查文件内容中的敏感信息
check_file_content() {
    print_header "检查文件内容中的敏感信息"
    
    local found=0
    local staged_files=$(git diff --cached --name-only --diff-filter=ACM)
    
    if [ -z "$staged_files" ]; then
        print_info "暂存区没有修改的文件"
        return 0
    fi
    
    for file in $staged_files; do
        # 只检查文本文件
        if file "$file" | grep -q "text"; then
            for pattern in "${SENSITIVE_CONTENT_PATTERNS[@]}"; do
                if git diff --cached "$file" | grep -qE "$pattern" 2>/dev/null; then
                    if [ $found -eq 0 ]; then
                        print_error "发现以下文件包含可疑敏感信息："
                        echo ""
                    fi
                    print_error "  - $file (匹配模式: $pattern)"
                    found=1
                    break
                fi
            done
        fi
    done
    
    if [ $found -eq 0 ]; then
        print_success "未发现文件内容包含敏感信息"
    fi
    
    return $found
}

# 检查 git 历史中的敏感信息
check_git_history() {
    print_header "检查 Git 历史中的敏感信息"
    
    print_info "正在扫描 Git 历史（这可能需要一些时间）..."
    
    local found=0
    
    for pattern in "${SENSITIVE_CONTENT_PATTERNS[@]}"; do
        local matches=$(git log --all -p -G "$pattern" -- '*.py' '*.sh' '*.js' '*.ts' '*.json' '*.yaml' '*.yml' '*.env*' 2>/dev/null | head -5 || true)
        if [ -n "$matches" ]; then
            if [ $found -eq 0 ]; then
                print_warning "Git 历史中发现可疑模式，请手动检查："
                echo ""
            fi
            print_warning "  模式: $pattern"
            found=1
        fi
    done
    
    if [ $found -eq 0 ]; then
        print_success "Git 历史未发现明显的敏感信息泄露"
    else
        print_info "建议运行: git log --all -p | grep -E 'pattern' 进一步检查"
    fi
    
    return 0
}

# 检查 .gitignore 配置
check_gitignore() {
    print_header "检查 .gitignore 配置"
    
    if [ ! -f ".gitignore" ]; then
        print_error "未找到 .gitignore 文件"
        return 1
    fi
    
    local required_patterns=(
        '\.env'
        '\.key'
        '\.pem'
        'private/'
    )
    
    local missing=()
    for pattern in "${required_patterns[@]}"; do
        if ! grep -qE "$pattern" .gitignore 2>/dev/null; then
            missing+=("$pattern")
        fi
    done
    
    if [ ${#missing[@]} -eq 0 ]; then
        print_success ".gitignore 配置完善"
    else
        print_warning ".gitignore 可能缺少以下规则："
        for pattern in "${missing[@]}"; do
            print_warning "  - $pattern"
        done
    fi
    
    return 0
}

# 显示建议
show_recommendations() {
    print_header "安全建议"
    
    echo -e "${CYAN}1. 如果发现敏感文件已被提交:${NC}"
    echo "   git rm --cached <file>          # 从 Git 移除但保留本地文件"
    echo "   git commit -m 'Remove sensitive files'"
    echo ""
    echo -e "${CYAN}2. 如果敏感信息已泄露到远程仓库:${NC}"
    echo "   # 使用 git-filter-repo 清理历史（需安装）"
    echo "   git filter-repo --path <file> --invert-paths"
    echo "   # 或查看: https://docs.github.com/zh/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository"
    echo ""
    echo -e "${CYAN}3. 安装 pre-commit hook:${NC}"
    echo "   ./scripts/install-git-hooks.sh"
    echo ""
    echo -e "${CYAN}4. 定期运行检查:${NC}"
    echo "   ./scripts/check-sensitive-files.sh"
}

# 主函数
main() {
    print_header "敏感信息安全检查"
    
    check_git
    
    local total_errors=0
    
    check_tracked_sensitive_files || total_errors=$((total_errors + 1))
    echo ""
    
    check_staged_sensitive_files || total_errors=$((total_errors + 1))
    echo ""
    
    check_file_content || total_errors=$((total_errors + 1))
    echo ""
    
    check_git_history
    echo ""
    
    check_gitignore
    echo ""
    
    show_recommendations
    echo ""
    
    if [ $total_errors -eq 0 ]; then
        print_header "检查完成：未发现安全问题"
        exit $EXIT_SUCCESS
    else
        print_header "检查完成：发现安全问题"
        print_error "请在提交前解决上述问题"
        exit $EXIT_ERROR
    fi
}

# 运行主函数
main "$@"
