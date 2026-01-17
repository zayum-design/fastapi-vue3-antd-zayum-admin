#!/bin/bash

# 后端安装脚本 - FastAPI 管理系统后端
# 使用方法: ./install.sh

set -e

# 显示帮助信息
show_help() {
    echo "用法: ./install.sh [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -v, --version  显示版本信息"
    echo ""
    echo "功能:"
    echo "  自动化安装 Zayum Admin 后端系统，包括："
    echo "  - 环境检查"
    echo "  - Python 依赖安装"
    echo "  - 数据库配置 (MySQL/PostgreSQL/SQLite)"
    echo "  - 管理员设置"
    echo "  - 数据库迁移和初始数据恢复"
    echo "  - 可选的服务启动"
    echo ""
    echo "示例:"
    echo "  ./install.sh          # 开始安装"
    echo "  ./install.sh --help   # 显示帮助"
}

# 显示版本信息
show_version() {
    echo "Zayum Admin 后端安装脚本 v1.0.0"
    echo "适用于 FastAPI + Vue3 管理系统"
}

# 处理命令行参数
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    -v|--version)
        show_version
        exit 0
        ;;
    "")
        # 无参数，继续执行安装
        ;;
    *)
        echo "错误: 未知参数 '$1'"
        echo "使用 './install.sh --help' 查看帮助信息"
        exit 1
        ;;
esac

echo "🚀 开始安装 Zayum Admin 后端系统..."
echo "=========================================="

# 检查是否已安装系统
echo "🔍 检查系统安装状态..."
if [ -f "install.lock" ]; then
    echo "⚠️  系统已安装，检测到 install.lock 文件"
    echo "💡 系统可能已经安装过，重新安装可能会清空现有数据"
    read -p "是否继续覆盖安装？(y/n, 默认: n): " overwrite_install
    overwrite_install=${overwrite_install:-n}
    
    if [ "$overwrite_install" = "y" ] || [ "$overwrite_install" = "Y" ]; then
        echo "⚠️  警告：您选择了覆盖安装，现有数据可能会被清空！"
        echo "删除安装锁定文件..."
        rm -f install.lock
        echo "✅ 安装锁定文件已删除，继续安装流程..."
    else
        echo "✅ 取消安装，系统保持原状"
        exit 0
    fi
else
    echo "✅ 系统未安装，继续安装流程..."
fi

# 检查必要工具
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 未安装，请先安装 $1"
        return 1
    fi
    return 0
}

echo "🔍 检查系统环境..."
check_command python3 || exit 1
check_command pip3 || exit 1
echo "✅ 系统环境检查通过"

# 安装Python依赖
echo "📦 安装 Python 依赖..."
if [ -f "requirements.txt" ]; then
    echo "安装 Python 依赖包..."
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Python 依赖安装成功"
    else
        echo "❌ Python 依赖安装失败"
        exit 1
    fi
else
    echo "❌ 未找到 requirements.txt 文件"
    exit 1
fi

# 数据库类型选择
echo ""
echo "🗄️  数据库配置"
echo "=========================================="

echo "请选择数据库类型："
echo "1) MySQL (默认)"
echo "2) PostgreSQL"
echo "3) SQLite"
read -p "请选择 (1-3, 默认: 1): " db_choice
db_choice=${db_choice:-1}

case $db_choice in
    1)
        db_type="mysql"
        echo "✅ 选择 MySQL 数据库"
        ;;
    2)
        db_type="postgresql"
        echo "✅ 选择 PostgreSQL 数据库"
        ;;
    3)
        db_type="sqlite"
        echo "✅ 选择 SQLite 数据库"
        ;;
    *)
        db_type="mysql"
        echo "✅ 使用默认 MySQL 数据库"
        ;;
esac

# 数据库配置
if [ "$db_type" = "mysql" ]; then
    echo ""
    echo "📝 MySQL 数据库配置"
    echo "------------------------------------------"
    
    read -p "请输入 MySQL 用户名 (默认: root): " db_user
    db_user=${db_user:-root}

    read -s -p "请输入 MySQL 密码 (默认: password): " db_password
    db_password=${db_password:-password}
    echo ""

    read -p "请输入数据库名称 (默认: zayum_admin): " db_name
    db_name=${db_name:-zayum_admin}

    read -p "请输入 MySQL 主机地址 (默认: localhost): " db_host
    db_host=${db_host:-localhost}

    read -p "请输入 MySQL 端口 (默认: 3306): " db_port
    db_port=${db_port:-3306}

elif [ "$db_type" = "postgresql" ]; then
    echo ""
    echo "📝 PostgreSQL 数据库配置"
    echo "------------------------------------------"
    
    read -p "请输入 PostgreSQL 用户名 (默认: postgres): " db_user
    db_user=${db_user:-postgres}

    read -s -p "请输入 PostgreSQL 密码 (默认: password): " db_password
    db_password=${db_password:-password}
    echo ""

    read -p "请输入数据库名称 (默认: zayum_admin): " db_name
    db_name=${db_name:-zayum_admin}

    read -p "请输入 PostgreSQL 主机地址 (默认: localhost): " db_host
    db_host=${db_host:-localhost}

    read -p "请输入 PostgreSQL 端口 (默认: 5432): " db_port
    db_port=${db_port:-5432}

else
    # SQLite 配置
    echo ""
    echo "📝 SQLite 数据库配置"
    echo "------------------------------------------"
    db_file="db.sqlite3"
    echo "✅ 使用 SQLite 数据库文件: $db_file"
fi

read -p "请输入系统域名 (例如: demo.zayum.com): " system_domain
system_domain=${system_domain:-demo.zayum.com}

# 保存配置到 .env
echo "💾 保存数据库配置到 .env 文件..."

if [ "$db_type" = "mysql" ]; then
    cat > .env << EOF
# 项目基本配置
PROJECT_NAME=Zayum Admin
TIMEZONE=Asia/Shanghai

#系统路由
ARROW_ROUTES=["auth", "captcha", "admin","admin_rule", "plugins","user","general_config","general_category"]

API_ADMIN_STR=/api
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REDIS_URL=redis://localhost:6379/0

BABEL_DEFAULT_LOCALE=en

# MySQL 数据库配置
MYSQL_USER=$db_user
MYSQL_PASSWORD=$db_password
MYSQL_DB=$db_name
MYSQL_HOST=$db_host
MYSQL_PORT=$db_port

# 插件配置
GENERATOR_ENABLED=true

# 最大文件大小（单位：字节）
MAX_FILE_SIZE=10485760

# 允许的文件扩展名，多个用逗号分隔
ALLOWED_EXTENSIONS=["jpg","png","gif","txt","pdf","webp"]

# 文件保存目录
UPLOAD_DIR=./uploads

# 插件目录
PLUGINS_DIR=./plugins

# CORS 配置
ALLOW_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173", "http://$system_domain","https://$system_domain"]
ALLOW_CREDENTIALS=true
ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
ALLOW_HEADERS=["*", "X-Captcha-Id"]
EXPOSE_HEADERS=["X-Captcha-Id"]

# Swagger UI 配置
SWAGGER_CSS_URL=https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui.css
SWAGGER_FAVICON_URL=https://fastapi.tiangolo.com/img/favicon.png
SWAGGER_BUNDLE_JS_URLS=["https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-bundle.js", "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"]
SWAGGER_PRESET_JS_URLS=["https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-standalone-preset.js", "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"]
SWAGGER_LOADING_TEXT=正在加载 API 文档...
SWAGGER_ERROR_MESSAGE=无法加载 API 文档资源。请检查网络连接或使用 OpenAPI JSON 文件
EOF

elif [ "$db_type" = "postgresql" ]; then
    cat > .env << EOF
# 项目基本配置
PROJECT_NAME=Zayum Admin
TIMEZONE=Asia/Shanghai

#系统路由
ARROW_ROUTES=["auth", "captcha", "admin","admin_rule", "plugins","user","general_config","general_category"]

API_ADMIN_STR=/api
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REDIS_URL=redis://localhost:6379/0

BABEL_DEFAULT_LOCALE=en

# PostgreSQL 数据库配置
POSTGRES_USER=$db_user
POSTGRES_PASSWORD=$db_password
POSTGRES_DB=$db_name
POSTGRES_HOST=$db_host
POSTGRES_PORT=$db_port

# 插件配置
GENERATOR_ENABLED=true

# 最大文件大小（单位：字节）
MAX_FILE_SIZE=10485760

# 允许的文件扩展名，多个用逗号分隔
ALLOWED_EXTENSIONS=["jpg","png","gif","txt","pdf","webp"]

# 文件保存目录
UPLOAD_DIR=./uploads

# 插件目录
PLUGINS_DIR=./plugins

# CORS 配置
ALLOW_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173", "http://$system_domain","https://$system_domain"]
ALLOW_CREDENTIALS=true
ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
ALLOW_HEADERS=["*", "X-Captcha-Id"]
EXPOSE_HEADERS=["X-Captcha-Id"]

# Swagger UI 配置
SWAGGER_CSS_URL=https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui.css
SWAGGER_FAVICON_URL=https://fastapi.tiangolo.com/img/favicon.png
SWAGGER_BUNDLE_JS_URLS=["https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-bundle.js", "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"]
SWAGGER_PRESET_JS_URLS=["https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-standalone-preset.js", "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"]
SWAGGER_LOADING_TEXT=正在加载 API 文档...
SWAGGER_ERROR_MESSAGE=无法加载 API 文档资源。请检查网络连接或使用 OpenAPI JSON 文件
EOF

else
    # SQLite 配置
    cat > .env << EOF
# 项目基本配置
PROJECT_NAME=Zayum Admin
TIMEZONE=Asia/Shanghai

#系统路由
ARROW_ROUTES=["auth", "captcha", "admin","admin_rule", "plugins","user","general_config","general_category"]

API_ADMIN_STR=/api
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REDIS_URL=redis://localhost:6379/0

BABEL_DEFAULT_LOCALE=en

# SQLite 数据库配置
SQLITE_DB=$db_file

# 插件配置
GENERATOR_ENABLED=true

# 最大文件大小（单位：字节）
MAX_FILE_SIZE=10485760

# 允许的文件扩展名，多个用逗号分隔
ALLOWED_EXTENSIONS=["jpg","png","gif","txt","pdf","webp"]

# 文件保存目录
UPLOAD_DIR=./uploads

# 插件目录
PLUGINS_DIR=./plugins

# CORS 配置
ALLOW_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173", "http://$system_domain","https://$system_domain"]
ALLOW_CREDENTIALS=true
ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
ALLOW_HEADERS=["*", "X-Captcha-Id"]
EXPOSE_HEADERS=["X-Captcha-Id"]

# Swagger UI 配置
SWAGGER_CSS_URL=https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui.css
SWAGGER_FAVICON_URL=https://fastapi.tiangolo.com/img/favicon.png
SWAGGER_BUNDLE_JS_URLS=["https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-bundle.js", "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"]
SWAGGER_PRESET_JS_URLS=["https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-standalone-preset.js", "https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"]
SWAGGER_LOADING_TEXT=正在加载 API 文档...
SWAGGER_ERROR_MESSAGE=无法加载 API 文档资源。请检查网络连接或使用 OpenAPI JSON 文件
EOF
fi

echo "✅ .env 配置文件已创建"

# 更新 alembic.ini 配置（仅MySQL和PostgreSQL需要）
if [ "$db_type" = "mysql" ]; then
    echo "💾 更新 alembic.ini 配置..."
    sed -i.bak "s|mysql+pymysql://.*|mysql+pymysql://$db_user:$db_password@$db_host:$db_port/$db_name?charset=utf8mb4|" alembic.ini
    echo "✅ alembic.ini 配置已更新"
elif [ "$db_type" = "postgresql" ]; then
    echo "💾 更新 alembic.ini 配置..."
    sed -i.bak "s|postgresql://.*|postgresql://$db_user:$db_password@$db_host:$db_port/$db_name|" alembic.ini
    echo "✅ alembic.ini 配置已更新"
fi

# 管理员配置
echo ""
echo "👤 管理员配置"
echo "=========================================="

read -p "是否使用默认管理员信息？(y/n, 默认: y): " use_default_admin
use_default_admin=${use_default_admin:-y}

if [ "$use_default_admin" = "y" ] || [ "$use_default_admin" = "Y" ]; then
    echo "✅ 使用默认管理员信息(用户名：admin,密码：Admin@888)"
    admin_username="admin"
    admin_password="Admin@888"
    admin_nickname="系统管理员"
    admin_email="13800000000@qq.com"
    admin_mobile="13800000000"
else
    echo "📝 请输入自定义管理员信息"
    read -p "请输入管理员用户名 (默认: admin): " admin_username
    admin_username=${admin_username:-admin}

    read -s -p "请输入管理员密码 (默认: Admin@888): " admin_password
    admin_password=${admin_password:-Admin@888}
    echo ""

    read -p "请输入管理员昵称 (默认: 系统管理员): " admin_nickname
    admin_nickname=${admin_nickname:-系统管理员}

    read -p "请输入管理员邮箱 (默认: 13800000000@qq.com): " admin_email
    admin_email=${admin_email:-13800000000@qq.com}

    read -p "请输入管理员手机号 (默认: 13800000000): " admin_mobile
    admin_mobile=${admin_mobile:-13800000000}
fi

# 更新管理员信息到 auto_insert_data.py
echo "💾 更新管理员信息到初始数据文件..."

# 生成密码哈希
echo "生成密码哈希..."
hashed_password=$(python3 -c "
import bcrypt
password = '$admin_password'
pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(pw_hash.decode('utf8'))
")

# 更新 auto_insert_data.py 文件中的管理员信息
echo "更新 auto_insert_data.py 文件..."
if [ -f "alembic/versions/auto_insert_data.py" ]; then
    # 使用 Python 来处理文件更新，避免 sed 特殊字符问题
    python3 -c "
import re

# 读取文件内容
with open('alembic/versions/auto_insert_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换管理员信息
content = re.sub(r\"'username': 'admin'\", \"'username': '$admin_username'\", content)
content = re.sub(r\"'nickname': 'SupperAdmin'\", \"'nickname': '$admin_nickname'\", content)
content = re.sub(r\"'password': '[^']*'\", \"'password': '$hashed_password'\", content)
content = re.sub(r\"'email': '[^']*'\", \"'email': '$admin_email'\", content)
content = re.sub(r\"'mobile': '[^']*'\", \"'mobile': '$admin_mobile'\", content)

# 写入更新后的内容
with open('alembic/versions/auto_insert_data.py', 'w', encoding='utf-8') as f:
    f.write(content)
"
    echo "✅ 管理员信息已更新到初始数据文件"
else
    echo "⚠️  警告：未找到 auto_insert_data.py 文件，跳过管理员信息更新"
fi

# 数据库迁移
echo ""
echo "🔄 数据库迁移"
echo "=========================================="

echo "执行数据库迁移..."
# 先测试数据库连接
echo "测试数据库连接..."
if [ "$db_type" = "mysql" ]; then
    python3 -c "
import pymysql
try:
    conn = pymysql.connect(
        host='$db_host',
        port=$db_port,
        user='$db_user',
        password='$db_password',
        database='$db_name',
        charset='utf8mb4'
    )
    conn.close()
    print('✅ 数据库连接测试成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
"
elif [ "$db_type" = "postgresql" ]; then
    python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='$db_host',
        port=$db_port,
        user='$db_user',
        password='$db_password',
        database='$db_name'
    )
    conn.close()
    print('✅ 数据库连接测试成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
"
fi

# 先创建表结构
echo "创建数据库表结构..."
python3 -c "
import sys
import os
sys.path.append('.')
from app.models import Base
from app.core.config import settings
from sqlalchemy import create_engine

# 根据数据库类型创建连接字符串
if '$db_type' == 'mysql':
    db_url = f'mysql+pymysql://$db_user:$db_password@$db_host:$db_port/$db_name?charset=utf8mb4'
elif '$db_type' == 'postgresql':
    db_url = f'postgresql://$db_user:$db_password@$db_host:$db_port/$db_name'
else:
    db_url = 'sqlite:///$db_file'

engine = create_engine(db_url)
Base.metadata.create_all(engine)
print('✅ 数据库表结构创建成功')
"

echo "执行数据库迁移..."
alembic upgrade head
if [ $? -eq 0 ]; then
    echo "✅ 数据库迁移成功"
else
    echo "❌ 数据库迁移失败，请检查："
    echo "  1. 数据库服务是否正在运行"
    echo "  2. 数据库用户是否有足够的权限"
    echo "  3. 数据库名称是否存在"
    echo "  4. 网络连接是否正常"
    exit 1
fi

# 插入初始数据
echo ""
echo "📊 插入初始数据"
echo "=========================================="

echo "✅ 初始数据已通过数据库迁移自动插入"

# 创建安装锁定文件
echo "💾 创建安装锁定文件..."
echo "Installation completed at: $(date)" > install.lock
echo "✅ 安装锁定文件已创建"

# 询问是否启动项目
echo ""
echo "🚀 项目启动选项"
echo "=========================================="

read -p "是否立即启动后端服务？(y/n, 默认: y): " start_service
start_service=${start_service:-y}

if [ "$start_service" = "y" ] || [ "$start_service" = "Y" ]; then
    echo "🚀 启动后端服务..."
    echo "执行命令: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    echo "等待后端服务启动..."
    sleep 5
    
    # 检查后端服务是否正常
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端服务启动成功"
        echo "📊 服务进程信息："
        echo "  进程ID (PID): $BACKEND_PID"
        echo "  启动命令: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    else
        echo "❌ 后端服务启动失败"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    
    # 保存进程ID
    echo $BACKEND_PID > .backend_pid
    echo "✅ 后端进程ID已保存到 .backend_pid 文件"
else
    echo "✅ 跳过服务启动，安装完成"
    BACKEND_PID="未启动"
fi

# 显示安装结果
echo ""
echo "🎉 后端安装完成！"
echo "=========================================="
echo "📊 服务访问信息："
echo "后端 API 地址: http://localhost:8000"
echo "Swagger 文档: http://localhost:8000/docs"
echo "健康检查: http://localhost:8000/health"
echo ""
echo "👤 管理员登录信息："
echo "用户名: $admin_username"
echo "密码: $admin_password"
echo "邮箱: $admin_email"
echo "手机号: $admin_mobile"
echo ""
echo "🗄️  数据库信息："
echo "数据库类型: $db_type"
if [ "$db_type" = "mysql" ]; then
    echo "数据库地址: $db_host:$db_port"
    echo "数据库名称: $db_name"
elif [ "$db_type" = "postgresql" ]; then
    echo "数据库地址: $db_host:$db_port"
    echo "数据库名称: $db_name"
else
    echo "数据库文件: $db_file"
fi
echo ""
echo "🔧 服务管理命令："
if [ "$start_service" = "y" ] || [ "$start_service" = "Y" ]; then
    echo "📊 当前运行进程信息："
    echo "  进程ID (PID): $BACKEND_PID"
    echo "  进程文件: .backend_pid"
    echo ""
    echo "🛑 停止服务命令："
    echo "  kill $BACKEND_PID"
    echo "  或使用进程文件: kill \$(cat .backend_pid)"
    echo ""
    echo "🔄 重启服务命令："
    echo "  kill $BACKEND_PID && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &"
    echo "  或使用进程文件: kill \$(cat .backend_pid) && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &"
    echo ""
    echo "📋 查看服务状态："
    echo "  ps aux | grep uvicorn"
    echo "  curl http://localhost:8000/health"
    echo ""
    echo "📝 查看服务日志："
    echo "  直接运行: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
else
    echo "🚀 启动服务命令："
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
fi
echo ""
echo "🔄 系统管理命令："
echo "重新运行安装: ./install.sh"
echo "手动启动服务: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "💡 安装说明："
echo "1. 配置文件已保存到 .env"
echo "2. 安装锁定文件已创建: install.lock"
if [ "$start_service" = "y" ] || [ "$start_service" = "Y" ]; then
    echo "3. 后端服务已在后台运行 (PID: $BACKEND_PID)"
    echo "4. 进程ID已保存到 .backend_pid 文件"
else
    echo "3. 后端服务未启动，如需启动请运行: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
fi
echo "=========================================="

echo ""
echo "📝 后续步骤："
echo "1. 配置前端应用以连接此后端 API"
echo "2. 配置域名和 SSL 证书"
echo "3. 设置系统服务以确保后端服务自动重启"
echo "4. 配置数据库备份策略"
echo "5. 配置 Redis 服务（如使用缓存功能）"
echo ""
echo "🎯 快速开始："
echo "1. 访问 Swagger 文档: http://localhost:8000/docs"
echo "2. 使用管理员账号登录系统"
echo "3. 配置前端应用连接此后端服务"
echo "4. 开始使用 Zayum Admin 管理系统"
echo ""
echo "🔔 重要提醒："
echo "• 请妥善保管管理员密码和数据库连接信息"
echo "• 定期备份数据库和配置文件"
echo "• 生产环境建议使用 HTTPS 和防火墙保护"
echo "• 如需重新安装，请先删除 install.lock 文件"
