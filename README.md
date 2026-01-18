# FastAPI + Vue3 栈鱼（Zayum）Admin 后台管理系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 注意：Vue前端基于 [vue-vben-admin](https://github.com/vbenjs/vue-vben-admin) (MIT许可) 进行修改，仅 `src/views` 和 `src/api` 目录包含原始前端代码。FastAPI后端完全原创。

一个基于 FastAPI 和 Vue3 的前后端分离后台管理系统，采用 Ant Design Vue 作为 UI 组件库，提供完整的权限管理和 CRUD 操作功能。

## 技术栈

### 后端
- Python 3.13.3
- FastAPI
- SQLAlchemy
- Alembic（数据库迁移）
- Redis（缓存）
- JWT（认证）

### 前端
- Vue 3
- TypeScript
- Vite
- Ant Design Vue
- Tailwind CSS

## 功能特性

- 用户管理（注册/登录、权限控制、角色管理）
- 系统管理（菜单管理、权限管理、日志管理）
- 文件管理（文件上传、文件分类）
- 插件系统（插件管理、插件开发）

## 快速部署

### 一键部署（推荐）

使用部署脚本快速启动整个系统：

```bash
# 显示帮助信息
./deploy.sh --help

# 完整部署（后端 + 前端）
./deploy.sh --all 

# 仅部署后端
./deploy.sh --backend 

# 仅部署前端
./deploy.sh --frontend

# 交互式选择部署模式
./deploy.sh
```

### 手动部署

#### 后端部署

1. 安装依赖
```bash
cd backend-fastapi-app
pip install -r requirements.txt
```

2. 运行安装脚本
```bash
./install.sh
```

3. 启动服务
```bash
./start.sh
```

#### 前端部署

1. 安装依赖
```bash
cd frontend-vue-app
npm install
```

2. 启动开发服务器
```bash
./start.sh
```

## 访问地址

- 前端应用：http://localhost:5173
- 后端API：http://localhost:8000
- Swagger文档：http://localhost:8000/docs

## 服务管理

### 停止服务

#### 停止后端服务
```bash
cd backend-fastapi-app
# 停止 Supervisor 管理的所有服务
supervisorctl stop all
# 或者停止特定的 FastAPI 服务
supervisorctl stop fastapi
```

#### 停止前端服务
前端服务通常运行在终端中，可以通过以下方式停止：
1. 在运行前端服务的终端中按 `Ctrl + C`
2. 或者查找并杀死相关进程：
```bash
# 查找前端进程
ps aux | grep "npm run dev" | grep -v grep
# 杀死进程（将 PID 替换为实际的进程ID）
kill -9 <PID>
```

### 重启服务

#### 重启后端服务
```bash
cd backend-fastapi-app
# 重启 Supervisor 管理的所有服务
supervisorctl restart all
# 或者重启特定的 FastAPI 服务
supervisorctl restart fastapi
```

#### 重启前端服务
```bash
cd frontend-vue-app
# 停止当前服务（按 Ctrl + C），然后重新启动
./start.sh
```

### 查看服务状态

#### 查看后端服务状态
```bash
cd backend-fastapi-app
# 查看 Supervisor 管理的所有服务状态
supervisorctl status
# 查看特定服务的详细状态
supervisorctl status fastapi
```

#### 查看前端服务状态
前端服务状态可以通过访问 http://localhost:5173 来检查，或者查看终端输出。

## 默认管理员账号

- 用户名：admin
- 密码：Admin@888

## 项目结构

```
fastapi-vue3-antd-zayum-admin/
├── backend-fastapi-app/        # 后端代码
│   ├── app/                    # 应用核心
│   ├── alembic/                # 数据库迁移
│   ├── install.sh              # 后端安装脚本
│   └── start.sh                # 后端启动脚本
├── frontend-vue-app/           # 前端代码
│   ├── src/                    # 源代码
│   ├── start.sh                # 前端启动脚本
│   └── package.json            # 依赖配置
├── deploy.sh                   # 一键部署脚本
└── README.md                   # 项目说明
```

## 脚本说明

### deploy.sh
一键部署脚本，支持多种部署模式：
- 完整部署：后端安装 + 前端启动
- 单独部署：仅后端或仅前端
- 环境检查：自动检测系统环境
- 配置管理：数据库、管理员等配置

### backend-fastapi-app/install.sh
后端安装脚本，功能包括：
- 环境检查
- Python依赖安装
- 数据库配置（MySQL/PostgreSQL/SQLite）
- 管理员设置
- 数据库迁移和初始数据恢复
- 可选的服务启动

### frontend-vue-app/start.sh
前端启动脚本，支持多种模式：
- 开发者模式（Development）
- 生产模式（Production）
- 构建模式（Build）
- 交互式配置域名

## 贡献指南

欢迎提交 Pull Request 或 Issue：
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件
