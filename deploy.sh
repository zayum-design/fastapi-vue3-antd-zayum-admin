#!/bin/bash

# 一键部署脚本 - FastAPI + Vue3 管理系统
# 使用方法: ./deploy.sh

set -e

echo "🚀 开始部署 Zayum Admin 系统..."
echo "=========================================="

# 检查是否已安装系统
echo "🔍 检查系统安装状态..."
if [ -f "backend-fastapi-app/install.lock" ]; then
    echo "❌ 系统已安装，检测到 install.lock 文件"
    echo "💡 如需重新部署，请先删除 install.lock 文件："
    echo "   rm backend-fastapi-app/install.lock"
    echo "⚠️  注意：删除 install.lock 文件后，系统将重新执行安装流程"
    exit 1
fi
echo "✅ 系统未安装，继续部署流程..."

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
check_command node || exit 1
check_command npm || exit 1
echo "✅ 系统环境检查通过"

# 安装后端依赖
echo "📦 安装后端依赖..."
cd backend-fastapi-app
if [ -f "requirements.txt" ]; then
    echo "安装 Python 依赖..."
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 后端依赖安装成功"
    else
        echo "❌ 后端依赖安装失败"
        exit 1
    fi
else
    echo "❌ 未找到 requirements.txt 文件"
    exit 1
fi
cd ..

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend-vue-app
if [ -f "package.json" ]; then
    echo "安装 Node.js 依赖..."
    npm install
    if [ $? -eq 0 ]; then
        echo "✅ 前端依赖安装成功"
    else
        echo "❌ 前端依赖安装失败"
        exit 1
    fi
else
    echo "❌ 未找到 package.json 文件"
    exit 1
fi
cd ..

# 数据库配置
echo ""
echo "🗄️  数据库配置"
echo "=========================================="

read -p "请输入 MySQL 用户名 (默认: root): " mysql_user
mysql_user=${mysql_user:-root}

read -s -p "请输入 MySQL 密码 (默认: password): " mysql_password
mysql_password=${mysql_password:-password}
echo ""

read -p "请输入数据库名称 (默认: zayum_admin): " mysql_db
mysql_db=${mysql_db:-zayum_admin}

read -p "请输入 MySQL 主机地址 (默认: localhost): " mysql_host
mysql_host=${mysql_host:-localhost}

read -p "请输入 MySQL 端口 (默认: 3306): " mysql_port
mysql_port=${mysql_port:-3306}

read -p "请输入系统域名 (例如: demo.zayumadmin.com): " system_domain
system_domain=${system_domain:-demo.zayumadmin.com}

# 保存配置到 backend-fastapi-app/.env
echo "💾 保存数据库配置到 .env 文件..."
cat > backend-fastapi-app/.env << EOF
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
MYSQL_USER=$mysql_user
MYSQL_PASSWORD=$mysql_password
MYSQL_DB=$mysql_db
MYSQL_HOST=$mysql_host
MYSQL_PORT=$mysql_port

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

echo "✅ .env 配置文件已创建"

# 更新 alembic.ini 配置
echo "💾 更新 alembic.ini 配置..."
cd backend-fastapi-app
sed -i.bak "s|mysql+pymysql://.*|mysql+pymysql://$mysql_user:$mysql_password@$mysql_host:$mysql_port/$mysql_db?charset=utf8mb4|" alembic.ini
cd ..

echo "✅ alembic.ini 配置已更新"

# 管理员配置
echo ""
echo "👤 管理员配置"
echo "=========================================="

read -p "是否使用默认管理员信息？(y/n, 默认: y): " use_default_admin
use_default_admin=${use_default_admin:-y}

if [ "$use_default_admin" = "y" ] || [ "$use_default_admin" = "Y" ]; then
    echo "✅ 使用默认管理员信息"
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
cd backend-fastapi-app

# 生成密码哈希
echo "生成密码哈希..."
hashed_password=$(python3 -c "
import bcrypt
pw_hash = bcrypt.hashpw(b'$admin_password', bcrypt.gensalt())
print(pw_hash.decode('utf8'))
")

# 更新 auto_insert_data.py 文件中的管理员信息
echo "更新 auto_insert_data.py 文件..."
sed -i.bak "s/'username': 'admin'/'username': '$admin_username'/" alembic/versions/auto_insert_data.py
sed -i.bak "s/'nickname': 'SupperAdmin'/'nickname': '$admin_nickname'/" alembic/versions/auto_insert_data.py
sed -i.bak "s/'password': '[^']*'/'password': '$hashed_password'/" alembic/versions/auto_insert_data.py
sed -i.bak "s/'email': '[^']*'/'email': '$admin_email'/" alembic/versions/auto_insert_data.py
sed -i.bak "s/'mobile': '[^']*'/'mobile': '$admin_mobile'/" alembic/versions/auto_insert_data.py

echo "✅ 管理员信息已更新到初始数据文件"
cd ..

# 数据库迁移
echo ""
echo "🔄 数据库迁移"
echo "=========================================="

cd backend-fastapi-app
echo "执行数据库迁移..."
alembic upgrade head
if [ $? -eq 0 ]; then
    echo "✅ 数据库迁移成功"
else
    echo "❌ 数据库迁移失败，请检查数据库连接"
    exit 1
fi
cd ..

# 插入初始数据
echo ""
echo "📊 插入初始数据"
echo "=========================================="

cd backend-fastapi-app
echo "执行数据插入..."
python3 -c "
import sys
sys.path.append('.')
from alembic.auto_insert_data import upgrade
upgrade()
print('✅ 初始数据插入成功')
"
if [ $? -eq 0 ]; then
    echo "✅ 初始数据插入成功"
else
    echo "❌ 初始数据插入失败"
    exit 1
fi
cd ..

# 启动后端服务
echo ""
echo "🚀 启动后端服务"
echo "=========================================="

cd backend-fastapi-app
echo "启动 FastAPI 后端服务..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

echo "等待后端服务启动..."
sleep 5

# 检查后端服务是否正常
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功 (PID: $BACKEND_PID)"
else
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# 构建前端
echo ""
echo "🏗️  构建前端应用"
echo "=========================================="

cd frontend-vue-app
echo "构建前端应用..."
npm run build
if [ $? -eq 0 ]; then
    echo "✅ 前端构建成功"
    FRONTEND_DIST="$(pwd)/dist"
else
    echo "❌ 前端构建失败"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi
cd ..

# 显示部署结果
echo ""
echo "🎉 部署完成！"
echo "=========================================="
echo "📊 服务访问信息："
echo "后端 API 地址: http://localhost:8000"
echo "前端静态文件目录: $FRONTEND_DIST"
echo "Swagger 文档: http://localhost:8000/docs"
echo ""
echo "👤 管理员登录信息："
echo "用户名: $admin_username"
echo "密码: $admin_password"
echo ""
echo "🔧 管理命令："
echo "停止后端服务: kill $BACKEND_PID"
echo "查看后端日志: cd backend-fastapi-app && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "重新构建前端: cd frontend-vue-app && npm run build"
echo ""
echo "💡 部署说明："
echo "1. 后端服务已在后台运行 (PID: $BACKEND_PID)"
echo "2. 前端已构建完成，静态文件位于: $FRONTEND_DIST"
echo "3. 您可以使用 Nginx 等 Web 服务器来提供前端静态文件"
echo "4. 数据库配置已保存到 backend-fastapi-app/.env"
echo "=========================================="

# 保存进程ID以便后续管理
echo $BACKEND_PID > .backend_pid
echo "后端进程ID已保存到 .backend_pid 文件"

echo ""
echo "📝 后续步骤："
echo "1. 配置 Web 服务器 (如 Nginx) 来提供前端静态文件"
echo "2. 配置域名和 SSL 证书"
echo "3. 设置系统服务以确保后端服务自动重启"
echo "4. 配置数据库备份策略"
