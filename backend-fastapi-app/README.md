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

## 🛠️ 安装部署

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

### 2. 配置环境变量

复制环境配置文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库和其他设置：
```env
# 项目基本配置
PROJECT_NAME=FastAPI Admin
TIMEZONE=Asia/Shanghai

# 系统路由
ARROW_ROUTES=["auth", "captcha", "admin","admin_rule", "plugins","user","general_config","general_category"]

API_ADMIN_STR=/api
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REDIS_URL=redis://localhost:6379/0

BABEL_DEFAULT_LOCALE=en

# MySQL 数据库配置
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=fastapi_admin
MYSQL_HOST=localhost
MYSQL_PORT=3306

# 插件配置
GENERATOR_ENABLED=true

# 文件上传配置
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=["jpg","png","gif","txt","pdf","webp"]
UPLOAD_DIR=./uploads
PLUGINS_DIR=./plugins
```

### 3. 数据库初始化

确保 MySQL 服务运行，并创建对应的数据库：
```sql
CREATE DATABASE fastapi_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 启动应用

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

应用启动后，访问以下地址：
- API 文档: http://localhost:8000/docs (使用国内 CDN 加速，加载更快)
- OpenAPI 文档: http://localhost:8000/api/v1/openapi.json

## 📁 项目结构

```
backend-fastapi-app/
├── app/                    # 应用主目录
│   ├── api/               # API 路由
│   │   ├── admin/         # 管理员相关接口
│   │   ├── user/          # 用户相关接口
│   │   └── common/        # 公共接口
│   ├── core/              # 核心功能模块
│   │   ├── config.py      # 配置管理
│   │   ├── security.py    # 安全相关
│   │   └── cache.py       # 缓存管理
│   ├── crud/              # 数据库操作
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic 模式
│   ├── services/          # 业务逻辑
│   ├── dependencies/      # 依赖注入
│   ├── middleware/        # 中间件
│   ├── plugins/           # 插件系统
│   └── utils/             # 工具函数
├── alembic/               # 数据库迁移
├── lang/                  # 多语言文件
├── plugins/               # 插件目录
├── sql/                   # SQL 脚本
├── tests/                 # 测试文件
└── uploads/               # 文件上传目录
```

## 🔧 API 接口

### 认证相关
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/refresh` - 刷新令牌
- `GET /api/auth/me` - 获取当前用户信息

### 用户管理
- `GET /api/user` - 获取用户列表
- `POST /api/user` - 创建用户
- `PUT /api/user/{id}` - 更新用户
- `DELETE /api/user/{id}` - 删除用户

### 管理员管理
- `GET /api/admin` - 获取管理员列表
- `POST /api/admin` - 创建管理员
- `PUT /api/admin/{id}` - 更新管理员
- `DELETE /api/admin/{id}` - 删除管理员

### 文件上传
- `POST /api/upload` - 文件上传
- `GET /api/upload/{file_id}` - 获取文件信息

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

### 单独构建镜像

```bash
# 构建镜像
docker build -t fastapi-admin-backend .

# 运行容器
docker run -d -p 8000:8000 --env-file .env fastapi-admin-backend
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_user.py

# 生成测试覆盖率报告
pytest --cov=app tests/
```

## 🔌 插件开发

### 创建插件

在 `plugins/` 目录下创建插件目录结构：

```
plugins/my-plugin/
├── __init__.py
├── plugin.json
├── routes.py
└── services.py
```

### 插件配置

`plugin.json` 示例：
```json
{
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "示例插件",
    "author": "Your Name",
    "enabled": true
}
```

## 📝 开发指南

### 代码规范
- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写详细的文档字符串
- 添加适当的单元测试

### 数据库迁移

使用 Alembic 进行数据库迁移：

```bash
# 创建新的迁移
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 MySQL 服务是否运行
   - 验证 `.env` 文件中的数据库配置
   - 确认数据库用户权限

2. **Redis 连接失败**
   - 检查 Redis 服务是否运行
   - 验证 Redis 配置

3. **文件上传失败**
   - 检查 `uploads/` 目录权限
   - 验证文件大小限制配置

### 日志查看

应用日志位于 `logs/` 目录，可通过以下方式查看：

```bash
# 查看最新日志
tail -f logs/app.log
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](../LICENSE) 文件了解详情。

## 📞 支持

- 文档: [项目文档](../docs/)
- 问题: [GitHub Issues](https://github.com/zayum-design/fastapi-vue3-antd-zayum-admin/issues)
- 邮箱: 联系项目维护者

---

**注意**: 首次启动时，系统会自动检测安装状态。如果未找到 `install.lock` 文件，将仅加载安装路由，需要完成安装流程后才能使用完整功能。
