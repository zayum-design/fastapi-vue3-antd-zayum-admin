# 快速开始

## 后端

1. 安装依赖
```bash
cd backend-fastapi-app
pip install -r requirements.txt
```

2. 配置环境变量
复制 `.env.example` 为 `.env` 并修改以下配置：

```ini
# 后端配置 (backend-fastapi-app/.env)
DATABASE_URL=mysql://root:yourpassword@localhost:3306/your_database?charset=utf8mb4

# Alembic 配置 (backend-fastapi-app/alembic.ini)
sqlalchemy.url = mysql://root:yourpassword@localhost:3306/your_database?charset=utf8mb4
```

3. 数据库迁移管理

#### 安装与初始化 Alembic
```bash
# 确保已安装Alembic（项目依赖已包含）
cd backend-fastapi-app

# 初始化迁移环境（仅首次需要）
alembic init alembic
```

4. 初始化基础数据
```bash
python -m app.initialize_db
```

5. 运行服务
```bash
uvicorn app.main:app --reload
```

## 前端

1. 安装依赖（任选一种方式）
```bash
cd frontend-vue-app
npm install   # 使用 npm
# 或
pnpm install  # 使用 pnpm
# 或
yarn          # 使用 yarn
```

2. 运行开发服务器
```bash
npm run dev   # 使用 npm
# 或 
pnpm dev      # 使用 pnpm
# 或
yarn dev      # 使用 yarn
```

## Supervisor管理

### 安装指南

| 平台   | 安装命令 |
|--------|----------|
| Linux  | `sudo apt-get install supervisor` (Debian/Ubuntu)<br>`sudo yum install supervisor` (CentOS/RHEL) |
| MacOS  | `brew install supervisor` |
| Windows | 1. 下载Python并安装<br>2. `pip install supervisor`<br>3. 将Python Scripts目录添加到PATH |

### 常用命令

```bash
# 启动所有/指定服务
supervisorctl start all
supervisorctl start <服务名>

# 停止所有/指定服务  
supervisorctl stop all
supervisorctl stop <服务名>

# 重启所有/指定服务
supervisorctl restart all 
supervisorctl restart <服务名>

# 查看服务状态
supervisorctl status

# 查看服务日志
supervisorctl tail <服务名>
supervisorctl tail -f <服务名>  # 实时日志

# 重新加载配置
supervisorctl reread
supervisorctl update

# 进入交互式控制台
supervisorctl
