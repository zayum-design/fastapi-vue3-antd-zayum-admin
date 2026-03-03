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

## 在线演示

我们提供了在线演示环境，您可以直接体验系统功能：

### 前端演示
- **演示地址**：https://demo.admin.zayum.com/web/home
- **功能**：完整的前端界面展示，包含所有用户功能

### 后端管理
- **登录地址**：https://demo.admin.zayum.com/admin
- **用户名**：admin
- **密码**：Admin@888
- **功能**：完整的后台管理系统，包含用户管理、系统配置、权限控制等

### 演示说明
1. 前端演示展示了完整的用户界面和交互体验
2. 后端管理演示需要登录，使用上述管理员账号即可访问
3. 演示环境数据会定期重置，请勿保存重要数据
4. 如需长期使用，请部署自己的实例

## 快速部署

### 一键部署（推荐）

我们提供了强大的模块化部署脚本 `deploy.sh v3.0`，支持交互式和命令行两种模式：

#### 交互式模式（适合新手）
```bash
# 直接运行，跟随向导完成部署
./deploy.sh
```

#### 命令行模式（适合熟练用户）
```bash
# 显示帮助信息
./deploy.sh --help

# 完整部署（后端 + 前端）
./deploy.sh --all 

# 仅部署后端
./deploy.sh --backend 

# 仅部署前端
./deploy.sh --frontend

# 仅配置环境（不部署）
./deploy.sh --config

# 显示版本信息
./deploy.sh --version
```

#### 部署脚本特性 v3.0
- **🎯 智能环境检测**：自动检查 Python、Node.js 等必要依赖
- **🗄️ 数据库向导**：交互式配置 MySQL / PostgreSQL / SQLite
- **🌐 域名配置助手**：引导式配置前后端域名和 API 地址
- **🔒 安全部署模式**：支持安全模式（保留数据）和强制模式（全新安装）
- **📝 完整日志记录**：详细的部署过程记录到 `logs/deploy.log`
- **🎨 新手友好界面**：可视化的菜单、智能默认值、详细提示

#### 数据库支持
| 数据库 | 适用场景 | 特点 |
|--------|----------|------|
| **MySQL** | 生产环境 | 高性能、高可用、支持复杂查询 |
| **PostgreSQL** | 生产/开发 | 功能丰富、严格的数据完整性 |
| **SQLite** | 开发测试 | 零配置、单文件、轻量快速 |

#### 部署说明：
1. 确保脚本有执行权限：`chmod +x deploy.sh`
2. 首次部署建议使用交互式模式：`./deploy.sh`
3. 脚本会引导完成数据库选择、域名配置等步骤
4. 部署完成后会显示访问地址和登录信息
5. 详细文档请参考 [deploy.md](deploy.md)

---

### 手动部署

如果您希望手动部署系统，可以参考以下步骤：

#### 后端部署

1. 安装依赖
```bash
cd backend-fastapi-app
pip install -r requirements.txt
```

2. 配置环境变量
```bash
# 复制示例配置文件
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息
```

3. 运行安装脚本
```bash
./install.sh
```

4. 启动服务
```bash
./start.sh
```

#### 前端部署

1. 安装依赖
```bash
cd frontend-vue-app
npm install
```

2. 配置环境变量
```bash
# 开发环境
cp .env.example .env.development
# 生产环境
cp .env.example .env.production
```

3. 启动开发服务器
```bash
./start.sh
```

---

### Docker 部署（生产环境推荐）

对于生产环境，我们推荐使用 Docker 进行部署：

```bash
# 使用 Docker Compose 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 停止服务
docker-compose down
```

---

## 访问地址

部署完成后，可以通过以下地址访问：

- 前端应用：http://localhost:5173
- 后端API：http://localhost:8000
- Swagger文档：http://localhost:8000/docs
- 后台登录：http://localhost:5173/admin/login

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
│   ├── start.sh                # 后端启动脚本
│   └── .env                    # 环境配置文件
├── frontend-vue-app/           # 前端代码
│   ├── src/                    # 源代码
│   ├── start.sh                # 前端启动脚本
│   ├── package.json            # 依赖配置
│   ├── .env.development        # 开发环境配置
│   └── .env.production         # 生产环境配置
├── deploy/                     # 部署脚本模块（v3.0）
│   ├── main.sh                 # 主脚本入口
│   ├── config.sh               # 配置模块
│   ├── utils.sh                # 工具模块
│   ├── database_utils.sh       # 数据库模块
│   ├── backend_utils.sh        # 后端模块
│   └── frontend_utils.sh       # 前端模块
├── deploy.sh                   # 一键部署脚本（入口）
├── deploy.md                   # 部署脚本使用文档
└── README.md                   # 项目说明
```

## 脚本说明

### deploy.sh
一键部署脚本（v3.0 模块化版本），功能包括：
- **多种部署模式**：完整部署、单独部署后端或前端、仅配置环境
- **数据库向导**：交互式配置 MySQL / PostgreSQL / SQLite
- **域名配置**：引导式配置前后端域名
- **安全模式**：保护现有数据或全新安装
- **环境检查**：自动检测系统依赖
- **详细日志**：完整的部署过程记录

📖 **详细文档**：[deploy.md](deploy.md)

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

## 故障排查

### 部署脚本问题

请参考 [deploy.md](deploy.md) 中的故障排查章节。

### 常见问题

1. **环境检查失败**：确保已安装 Python 3.8+ 和 Node.js 16+
2. **数据库连接失败**：检查数据库服务是否运行，用户名密码是否正确
3. **前端依赖安装失败**：尝试清除 npm 缓存后重新安装
4. **端口被占用**：修改 `.env` 文件中的端口号或停止占用端口的进程

## 贡献指南

欢迎提交 Pull Request 或 Issue：
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件
