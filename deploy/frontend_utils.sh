#!/bin/bash

# 前端工具模块 - 前端部署相关函数

# 加载配置
source "$(dirname "$0")/config.sh"

# 选择前端启动模式
select_frontend_mode() {
    echo -e "${BLUE}请选择前端启动模式:${NC}" >&2
    echo -e "  ${GREEN}1${NC}) 开发者模式 (Development) - 用于开发调试" >&2
    echo -e "  ${GREEN}2${NC}) 生产模式 (Production) - 生产环境" >&2
    echo -e "  ${GREEN}3${NC}) 构建模式 (Build) - 构建生产版本" >&2
    echo -e "  ${GREEN}4${NC}) 返回上级菜单" >&2
    echo "" >&2
    read -p "请输入选项 [1-4] (直接按回车选择默认值 1): " choice >&2
    
    case $choice in
        1|"")
            echo "$FRONTEND_MODE_DEV"
            ;;
        2)
            echo "$FRONTEND_MODE_PROD"
            ;;
        3)
            echo "$FRONTEND_MODE_BUILD"
            ;;
        4)
            echo "cancel"
            ;;
        *)
            echo -e "${RED}错误: 无效选项 '$choice'${NC}" >&2
            select_frontend_mode
            ;;
    esac
}

# 函数：交互式配置域名
configure_domain_interactive() {
    local mode="$1"  # dev 或 prod
    local default_access_domain=""
    local default_api_domain=""
    local protocol="http"
    
    if [ "$mode" = "prod" ]; then
        default_access_domain="$DEFAULT_PROD_ACCESS_DOMAIN"
        default_api_domain="$DEFAULT_PROD_API_DOMAIN"
        protocol="https"
    else
        default_access_domain="$DEFAULT_DEV_ACCESS_DOMAIN"
        default_api_domain="$DEFAULT_DEV_API_DOMAIN"
        protocol="http"
    fi
    
    # 直接输出到标准错误，避免污染函数返回值
    echo -e "${BLUE}请配置 ${mode} 环境域名:${NC}" >&2
    echo "" >&2
    
    # 配置访问域名（前端域名）
    echo -e "${YELLOW}1. 访问域名 (VITE_GLOB_URL) - 用户访问前端的地址${NC}" >&2
    echo -e "${YELLOW}默认值: ${default_access_domain}${NC}" >&2
    echo -e "${YELLOW}提示: 可以输入完整 URL (如 ${protocol}://example.com) 或裸域名 (如 example.com)${NC}" >&2
    echo "" >&2
    
    # 从标准输入读取，输出提示到标准错误
    read -p "请输入访问域名 (直接回车使用默认值): " access_domain >&2
    
    if [ -z "$access_domain" ]; then
        access_domain="$default_access_domain"
        echo -e "${GREEN}使用默认访问域名: $access_domain${NC}" >&2
    else
        # 去除可能的前后空格
        access_domain=$(echo "$access_domain" | xargs)
        echo -e "${GREEN}使用自定义访问域名: $access_domain${NC}" >&2
    fi
    
    # 规范化域名
    if [[ ! "$access_domain" =~ ^https?:// ]]; then
        access_domain="${protocol}://$access_domain"
    fi
    
    echo -e "${GREEN}规范化后的访问域名: $access_domain${NC}" >&2
    echo "" >&2
    
    # 配置 API 域名（后端域名）
    echo -e "${YELLOW}2. API 域名 (VITE_GLOB_API_URL) - 前端访问后端的地址${NC}" >&2
    echo -e "${YELLOW}默认值: ${default_api_domain}${NC}" >&2
    echo -e "${YELLOW}提示: 可以输入完整 URL (如 ${protocol}://api.example.com) 或裸域名 (如 api.example.com)${NC}" >&2
    echo "" >&2
    
    read -p "请输入 API 域名 (直接回车使用默认值): " api_domain >&2
    
    if [ -z "$api_domain" ]; then
        api_domain="$default_api_domain"
        echo -e "${GREEN}使用默认 API 域名: $api_domain${NC}" >&2
    else
        # 去除可能的前后空格
        api_domain=$(echo "$api_domain" | xargs)
        echo -e "${GREEN}使用自定义 API 域名: $api_domain${NC}" >&2
    fi
    
    # 规范化域名
    if [[ ! "$api_domain" =~ ^https?:// ]]; then
        api_domain="${protocol}://$api_domain"
    fi
    
    echo -e "${GREEN}规范化后的 API 域名: $api_domain${NC}" >&2
    echo "" >&2
    
    # 返回结果（只包含域名，不包含颜色代码）
    echo "$access_domain $api_domain"
}

# 函数：更新环境变量文件
update_env_file() {
    local env_file="$1"
    local access_domain="$2"
    local api_domain="$3"
    
    # 创建临时文件
    local temp_file="${env_file}.tmp"
    
    # 如果文件不存在，创建它
    if [ ! -f "$env_file" ]; then
        touch "$env_file"
    fi
    
    # 检查是否已经包含正确的环境变量
    local url_found=false
    local api_found=false
    
    # 读取文件并检查
    while IFS= read -r line; do
        # 跳过注释行和空行
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue
        
        # 检查 VITE_GLOB_URL
        if [[ "$line" =~ ^VITE_GLOB_URL=(.*)$ ]]; then
            local value="${BASH_REMATCH[1]}"
            # 去除可能的引号和空格
            value=$(echo "$value" | sed -e 's/^["'\'']//' -e 's/["'\'']$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
            if [[ "$value" == "$access_domain" ]]; then
                url_found=true
            fi
        fi
        
        # 检查 VITE_GLOB_API_URL
        if [[ "$line" =~ ^VITE_GLOB_API_URL=(.*)$ ]]; then
            local value="${BASH_REMATCH[1]}"
            # 去除可能的引号和空格
            value=$(echo "$value" | sed -e 's/^["'\'']//' -e 's/["'\'']$//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
            if [[ "$value" == "$api_domain" ]]; then
                api_found=true
            fi
        fi
    done < "$env_file"
    
    # 如果环境变量已经正确设置，直接返回成功
    if $url_found && $api_found; then
        echo -e "${GREEN}✅ 环境变量已正确配置${NC}"
        return 0
    fi
    
    # 备份原始文件（只在需要修改时创建备份）
    cp "$env_file" "${env_file}.bak"
    
    # 使用更安全的方法更新环境变量
    # 先删除现有的行（如果存在）
    grep -v "^VITE_GLOB_URL=" "$env_file" > "$temp_file"
    
    # 在适当的位置插入 VITE_GLOB_URL
    # 查找 "# Web 地址（前端访问地址）" 注释，并在其下一行插入
    if grep -q "# Web 地址（前端访问地址）" "$temp_file"; then
        # 使用 sed 在注释后插入
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS 系统
            sed -i '' '/# Web 地址（前端访问地址）/a\
VITE_GLOB_URL='"${access_domain}"'
' "$temp_file"
        else
            # Linux 和其他系统
            sed -i '/# Web 地址（前端访问地址）/a\VITE_GLOB_URL='"${access_domain}" "$temp_file"
        fi
    else
        # 如果找不到注释，直接追加
        echo "VITE_GLOB_URL=${access_domain}" >> "$temp_file"
    fi
    
    # 再次处理 API URL
    grep -v "^VITE_GLOB_API_URL=" "$temp_file" > "${temp_file}2"
    
    # 在适当的位置插入 VITE_GLOB_API_URL
    # 查找 "# 接口地址（后端 API 地址）" 注释，并在其下一行插入
    if grep -q "# 接口地址（后端 API 地址）" "${temp_file}2"; then
        # 使用 sed 在注释后插入
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS 系统
            sed -i '' '/# 接口地址（后端 API 地址）/a\
VITE_GLOB_API_URL='"${api_domain}"'
' "${temp_file}2"
        else
            # Linux 和其他系统
            sed -i '/# 接口地址（后端 API 地址）/a\VITE_GLOB_API_URL='"${api_domain}" "${temp_file}2"
        fi
    else
        # 如果找不到注释，直接追加
        echo "VITE_GLOB_API_URL=${api_domain}" >> "${temp_file}2"
    fi
    
    # 替换原文件
    mv "${temp_file}2" "$env_file"
    rm -f "$temp_file"
    
    # 确保环境变量文件有正确的权限
    chmod 644 "$env_file"
    
    # 验证环境变量是否已正确写入
    echo -e "${GREEN}✅ 环境变量已正确写入 $env_file 文件${NC}"
    return 0
}

# 部署前端
deploy_frontend() {
    local frontend_mode="$1"
    
    echo -e "${BLUE}🚀 开始部署前端系统...${NC}"
    echo -e "${BLUE}==========================================${NC}"
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo -e "${RED}❌ 前端目录 $FRONTEND_DIR 不存在${NC}"
        return 1
    fi
    
    if [ ! -f "$FRONTEND_DIR/start.sh" ]; then
        echo -e "${RED}❌ 前端启动脚本 $FRONTEND_DIR/start.sh 不存在${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}执行前端启动脚本 (模式: $frontend_mode)...${NC}"
    cd "$FRONTEND_DIR"
    chmod +x start.sh
    
    # 根据选择的模式执行
    case $frontend_mode in
        "$FRONTEND_MODE_DEV")
            # 开发模式：交互式配置开发环境变量
            echo -e "${YELLOW}配置开发环境...${NC}"
            
            # 确保 .env.development 文件存在
            if [ ! -f ".env.development" ]; then
                if [ -f ".env.example" ]; then
                    cp .env.example .env.development
                    echo -e "${GREEN}✓ 已创建 .env.development 文件${NC}"
                else
                    echo -e "${RED}✗ 错误: .env.example 文件不存在${NC}"
                    cd "$PROJECT_ROOT"
                    return 1
                fi
            fi
            
            # 交互式配置域名
            domain_config=$(configure_domain_interactive "dev")
            # 使用更可靠的方法解析结果，避免awk处理特殊字符
            access_domain=$(echo "$domain_config" | cut -d' ' -f1)
            api_domain=$(echo "$domain_config" | cut -d' ' -f2-)
            
            echo -e "${GREEN}使用访问域名: $access_domain${NC}"
            echo -e "${GREEN}使用 API 域名: $api_domain${NC}"
            
            # 更新 .env.development 文件
            if update_env_file ".env.development" "$access_domain" "$api_domain"; then
                echo -e "${GREEN}✓ 开发环境配置完成${NC}"
            else
                echo -e "${RED}✗ 开发环境配置失败${NC}"
                cd "$PROJECT_ROOT"
                return 1
            fi
            
            # 启动开发服务器
            echo -e "${YELLOW}启动开发服务器...${NC}"
            ./start.sh --dev
            ;;
        "$FRONTEND_MODE_PROD")
            # 生产模式：交互式配置生产环境变量
            echo -e "${YELLOW}配置生产环境...${NC}"
            
            # 确保 .env.production 文件存在
            if [ ! -f ".env.production" ]; then
                if [ -f ".env.example" ]; then
                    cp .env.example .env.production
                    echo -e "${GREEN}✓ 已创建 .env.production 文件${NC}"
                else
                    echo -e "${RED}✗ 错误: .env.example 文件不存在${NC}"
                    cd "$PROJECT_ROOT"
                    return 1
                fi
            fi
            
            # 交互式配置域名
            domain_config=$(configure_domain_interactive "prod")
            # 使用更可靠的方法解析结果，避免awk处理特殊字符
            access_domain=$(echo "$domain_config" | cut -d' ' -f1)
            api_domain=$(echo "$domain_config" | cut -d' ' -f2-)
            
            echo -e "${GREEN}使用访问域名: $access_domain${NC}"
            echo -e "${GREEN}使用 API 域名: $api_domain${NC}"
            
            # 更新 .env.production 文件
            if update_env_file ".env.production" "$access_domain" "$api_domain"; then
                echo -e "${GREEN}✓ 生产环境配置完成${NC}"
            else
                echo -e "${RED}✗ 生产环境配置失败${NC}"
                cd "$PROJECT_ROOT"
                return 1
            fi
            
            # 启动生产服务器，传递环境变量避免重复配置
            echo -e "${YELLOW}启动生产服务器...${NC}"
            # 设置环境变量，这样 start.sh 可以检测到已经配置
            export VITE_GLOB_URL="$access_domain"
            export VITE_GLOB_API_URL="$api_domain"
            ./start.sh --prod
            ;;
        "$FRONTEND_MODE_BUILD")
            # 构建模式：交互式配置生产环境变量并构建
            echo -e "${YELLOW}配置构建环境...${NC}"
            
            # 确保 .env.production 文件存在
            if [ ! -f ".env.production" ]; then
                if [ -f ".env.example" ]; then
                    cp .env.example .env.production
                    echo -e "${GREEN}✓ 已创建 .env.production 文件${NC}"
                else
                    echo -e "${RED}✗ 错误: .env.example 文件不存在${NC}"
                    cd "$PROJECT_ROOT"
                    return 1
                fi
            fi
            
            # 交互式配置域名
            domain_config=$(configure_domain_interactive "prod")
            # 使用更可靠的方法解析结果，避免awk处理特殊字符
            access_domain=$(echo "$domain_config" | cut -d' ' -f1)
            api_domain=$(echo "$domain_config" | cut -d' ' -f2-)
            
            echo -e "${GREEN}使用访问域名: $access_domain${NC}"
            echo -e "${GREEN}使用 API 域名: $api_domain${NC}"
            
            # 更新 .env.production 文件
            if update_env_file ".env.production" "$access_domain" "$api_domain"; then
                echo -e "${GREEN}✓ 构建环境配置完成${NC}"
            else
                echo -e "${RED}✗ 构建环境配置失败${NC}"
                cd "$PROJECT_ROOT"
                return 1
            fi
            
            # 启动构建
            echo -e "${YELLOW}开始构建应用...${NC}"
            ./start.sh --prod --build 2>/dev/null || echo "3" | ./start.sh
            ;;
        *)
            echo -e "${RED}错误: 未知前端模式 '$frontend_mode'${NC}"
            cd "$PROJECT_ROOT"
            return 1
            ;;
    esac
    
    local frontend_result=$?
    cd "$PROJECT_ROOT"
    
    if [ $frontend_result -eq 0 ]; then
        echo -e "${GREEN}✅ 前端部署成功 (模式: $frontend_mode)${NC}"
        return 0
    else
        echo -e "${RED}❌ 前端部署失败 (模式: $frontend_mode)${NC}"
        return 1
    fi
}

# 显示前端部署信息
show_frontend_info() {
    local frontend_mode="$1"
    
    echo -e "${YELLOW}📊 前端服务信息：${NC}"
    case $frontend_mode in
        "$FRONTEND_MODE_DEV")
            echo "前端开发服务器: http://localhost:5173"
            echo "访问域名: 根据 .env.development 配置"
            ;;
        "$FRONTEND_MODE_PROD")
            echo "前端生产服务器: 根据 .env.production 配置"
            echo "访问域名: 根据 .env.production 配置"
            ;;
        "$FRONTEND_MODE_BUILD")
            echo "构建输出目录: $FRONTEND_DIR/dist"
            echo "访问域名: 根据 .env.production 配置"
            ;;
    esac
    echo "前端目录: $FRONTEND_DIR"
    echo ""
    echo -e "${YELLOW}🔧 前端管理命令：${NC}"
    echo "停止前端服务: 按 Ctrl+C 停止开发服务器"
    echo "重新启动前端: cd $FRONTEND_DIR && ./start.sh"
}
