# 后端部署指南

## 部署方式选择

Zayum Admin 后端提供多种部署方式，您可以根据需求选择最适合的方式：

### 1. 使用部署脚本（推荐）

我们提供了强大的自动化部署脚本 `deploy.sh`，支持一键部署后端：

```bash
# 仅部署后端
./deploy.sh --backend

# 完整部署（后端 + 前端）
./deploy.sh --all

# 交互式选择部署模式
./deploy.sh
```

#### 部署脚本特性：
- **自动化环境检查**：自动检测 Python、数据库、Redis 等环境
- **依赖自动安装**：自动安装 Python 依赖和系统依赖
- **数据库配置**：自动配置数据库（MySQL/PostgreSQL/SQLite）
- **管理员设置**：交互式设置管理员账号
- **服务管理**：自动配置 Supervisor 服务管理
- **详细日志输出**：提供详细的部署日志，便于排查问题

### 2. 手动部署

如果您希望手动部署后端，可以参考以下步骤：

#### 步骤 1：安装系统依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv redis-server

# CentOS/RHEL
sudo yum install python3 python3-pip python3-venv redis

# macOS
brew install python3 redis
```

#### 步骤 2：安装 Python 依赖

```bash
cd backend-fastapi-app
pip install -r requirements.txt
```

#### 步骤 3：数据库配置

```bash
# 运行数据库初始化脚本
python -m app.initialize_db

# 或使用安装脚本（推荐）
./install.sh
```

#### 步骤 4：启动服务

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（使用 Supervisor）
./start.sh

# 或直接使用 Supervisor
supervisord -c supervisord.conf
```

### 3. 使用 Docker 部署

对于生产环境，我们推荐使用 Docker 进行部署：

```bash
# 构建 Docker 镜像
docker build -t zayum-admin-backend .

# 运行容器
docker run -p 8000:8000 zayum-admin-backend

# 或使用 Docker Compose（推荐）
docker-compose up -d
```

## 数据库配置

### 支持的数据库

后端支持以下数据库：
- **SQLite**（默认，适合开发和测试）
- **MySQL**（生产环境推荐）
- **PostgreSQL**（生产环境推荐）

### 数据库配置示例

在 `.env` 文件中配置数据库连接：

```env
# SQLite（默认）
DATABASE_URL=sqlite:///./zayum_admin.db

# MySQL
DATABASE_URL=mysql://username:password@localhost:3306/zayum_admin

# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/zayum_admin
```

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

## 服务管理

### Supervisor 配置

后端使用 Supervisor 进行进程管理，配置文件位于 `supervisord.conf`：

```ini
[program:fastapi]
command=uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/path/to/backend-fastapi-app
autostart=true
autorestart=true
stderr_logfile=/var/log/fastapi.err.log
stdout_logfile=/var/log/fastapi.out.log
```

### Supervisor 常用命令

```bash
# 启动所有服务
supervisorctl start all

# 停止所有服务
supervisorctl stop all

# 重启所有服务
supervisorctl restart all

# 查看服务状态
supervisorctl status

# 重新加载配置
supervisorctl reread
supervisorctl update
```

## 环境配置

### 环境变量

后端支持以下环境变量：

```env
# 数据库配置
DATABASE_URL=sqlite:///./zayum_admin.db

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
APP_ENV=development  # development/production
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin@888
ADMIN_EMAIL=admin@example.com
```

### 配置文件

主要配置文件：
- `.env` - 环境变量配置文件
- `alembic.ini` - 数据库迁移配置
- `supervisord.conf` - Supervisor 进程管理配置

## 安全配置

### 1. 修改默认密码

部署后务必修改默认管理员密码：

```bash
# 使用安装脚本修改密码
./install.sh --change-password

# 或通过 API 修改
curl -X PUT http://localhost:8000/api/admin/users/1 \
  -H "Content-Type: application/json" \
  -d '{"password": "NewStrongPassword123!"}'
```

### 2. 配置 HTTPS

生产环境必须启用 HTTPS：

```bash
# 使用 Nginx 反向代理配置 SSL
# nginx.conf 示例配置
server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # API（仅内网）
sudo ufw enable
```

## 监控和维护

### 日志查看

```bash
# 查看实时日志
tail -f /var/log/fastapi.out.log

# 查看错误日志
tail -f /var/log/fastapi.err.log

# 查看 Supervisor 日志
tail -f /var/log/supervisor/supervisord.log
```

### 性能监控

1. **API 监控**：使用 FastAPI 内置的 `/docs` 和 `/redoc` 接口
2. **数据库监控**：监控数据库连接数和查询性能
3. **系统监控**：使用 `top`、`htop`、`iotop` 等工具
4. **应用监控**：集成 Prometheus 和 Grafana

### 健康检查

```bash
# 检查 API 健康状态
curl http://localhost:8000/api/health

# 检查数据库连接
curl http://localhost:8000/api/health/db

# 检查 Redis 连接
curl http://localhost:8000/api/health/redis
```

## 备份和恢复

### 数据库备份

```bash
# SQLite 备份
cp zayum_admin.db zayum_admin.db.backup.$(date +%Y%m%d)

# MySQL 备份
mysqldump -u username -p zayum_admin > backup_$(date +%Y%m%d).sql

# PostgreSQL 备份
pg_dump -U username zayum_admin > backup_$(date +%Y%m%d).sql
```

### 配置文件备份

```bash
# 备份重要配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  .env \
  alembic.ini \
  supervisord.conf \
  requirements.txt
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :8000
   # 杀死进程
   kill -9 <PID>
   ```

2. **依赖安装失败**
   ```bash
   # 使用国内镜像源
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. **数据库连接失败**
   ```bash
   # 检查数据库服务状态
   sudo systemctl status mysql
   # 或
   sudo systemctl status postgresql
   ```

4. **Supervisor 服务启动失败**
   ```bash
   # 检查配置文件语法
   supervisord -c supervisord.conf --check
   # 查看详细日志
   tail -f /var/log/supervisor/supervisord.log
   ```

### 获取帮助

如果遇到问题，可以通过以下方式获取帮助：

1. 查看项目文档：http://doc.zayumadmin.com
2. 查看 GitHub Issues：https://github.com/zayum-design/fastapi-vue3-antd-zayum-admin/issues
3. 查看部署脚本帮助：`./deploy.sh --help`

---

**注意**：生产环境部署前，请务必进行充分的测试，确保系统稳定运行。定期备份数据和配置文件，制定灾难恢复计划。
