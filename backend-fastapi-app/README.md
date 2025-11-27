# FastAPI Admin Backend

基于 FastAPI 构建的现代化后台管理系统后端，提供完整的用户管理、权限控制、插件系统等功能。

## 🚀 功能特性

### 核心功能
- **用户管理**: 完整的用户注册、登录、权限管理
- **权限控制**: 基于角色的访问控制 (RBAC)
- **插件系统**: 支持动态加载和卸载插件
- **多语言支持**: 内置国际化支持 (i18n)
- **文件上传**: 支持多种文件格式上传和管理
- **日志系统**: 完整的操作日志记录
- **验证码**: 图形验证码和滑块验证码支持

### 技术特性
- **FastAPI**: 高性能异步 Web 框架
- **SQLAlchemy**: ORM 数据库操作
- **JWT 认证**: 安全的身份验证机制
- **Redis**: 缓存和会话管理
- **MySQL**: 主要数据库支持
- **Docker**: 容器化部署支持

## 📋 系统要求

- Python 3.8+
- MySQL 5.7+
- Redis 6.0+

## 🛠️ 快速安装

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd backend-fastapi-app

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

复制环境配置文件并编辑：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接：
```env
# MySQL 数据库配置
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=fastapi_admin
MYSQL_HOST=localhost
MYSQL_PORT=3306

# 应用配置
SECRET_KEY=your_secret_key_here
REDIS_URL=redis://localhost:6379/0
```

### 3. 数据库准备

创建数据库：
```sql
CREATE DATABASE fastapi_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 启动应用

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：http://localhost:8000/docs

## 📁 核心目录

```
backend-fastapi-app/
├── app/                    # 应用主目录
│   ├── api/               # API 路由
│   ├── core/              # 核心配置
│   ├── crud/              # 数据库操作
│   ├── models/            # 数据模型
│   └── utils/             # 工具函数
├── install/               # 安装模块（独立目录）
├── alembic/               # 数据库迁移
└── uploads/               # 文件上传
```

## 🐳 Docker 部署

```bash
# 使用 Docker Compose
docker-compose up -d

# 单独构建
docker build -t fastapi-admin-backend .
docker run -d -p 8000:8000 --env-file .env fastapi-admin-backend
```

## 🧪 测试

```bash
# 运行测试
pytest

# 覆盖率报告
pytest --cov=app tests/
```

---

**注意**: 首次启动时，系统会自动检测安装状态。如果未找到 `install.lock` 文件，将仅加载安装路由，需要完成安装流程后才能使用完整功能。
