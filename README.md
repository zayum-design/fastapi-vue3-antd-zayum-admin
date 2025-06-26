# FastAPI + Vue3 栈鱼（Zayum）Admin 后台管理系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Note: The Vue frontend (frontend-vue-app/) is based on [vue-vben-admin](https://github.com/vbenjs/vue-vben-admin) (MIT licensed) with modifications. Only `src/views` and `src/api` directories contain original frontend code. The FastAPI backend is fully original.

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

- 用户管理
  - 用户注册/登录
  - 权限控制
  - 角色管理
- 系统管理
  - 菜单管理
  - 权限管理
  - 日志管理
- 文件管理
  - 文件上传
  - 文件分类
- 插件系统
  - 插件管理
  - 插件开发

## 项目结构

```
fastapi-vue3-antd-zayum-admin/
├── backend-fastapi-app/        # 后端代码
│   ├── app/                       # 应用核心
│   │   ├── api/                   # API 路由
│   │   ├── core/                  # 核心功能
│   │   ├── crud/                  # 数据库操作
│   │   ├── models/                # 数据模型
│   │   ├── schemas/               # Pydantic 模型
│   │   └── services/              # 业务逻辑
│   ├── alembic/                   # 数据库迁移
│   └── tests/                     # 单元测试
├── frontend-vue-app/                   # 前端代码
│   ├── src/                       # 源代码
│   │   ├── api/                   # API 请求
│   │   ├── assets/                # 静态资源
│   │   ├── components/            # 公共组件
│   │   ├── layouts/               # 页面布局
│   │   ├── router/                # 路由配置
│   │   ├── stores/                # 状态管理
│   │   └── views/                 # 页面视图
└── README.md                      # 项目说明
```

## 快速开始

### 后端

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

#### 配置文件设置
1. 修改 alembic.ini 中的数据库连接：
```ini
sqlalchemy.url = mysql://root:yourpassword@localhost:3306/your_database?charset=utf8mb4
```

2. 更新 alembic/env.py 引入模型：
```python
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))

from app.models import Base  # 导入所有SQLAlchemy模型
target_metadata = Base.metadata
```

#### 迁移操作指南
```bash
# 生成迁移脚本（模型变更后）
alembic revision --autogenerate -m "描述修改内容"

# 应用最新迁移
alembic upgrade head

# 回滚到指定版本
alembic downgrade <版本号>

# 查看迁移历史
alembic history --verbose

# 生成SQL预览文件
alembic upgrade head --sql > migration.sql
```

#### 最佳实践
1. 开发环境：
```bash
# 完整迁移流程示例
alembic revision --autogenerate -m "添加用户表"
alembic upgrade head
python3 app/initialize_db.py
```

2. 生产环境：
```bash
# 安全执行迁移（先生成审查SQL）
alembic upgrade head --sql > prod_migration.sql
# 审查后应用
alembic upgrade head
```

4. 初始化基础数据

```bash
python -m app.initialize_db
```

5. 运行服务
```bash
uvicorn app.main:app --reload
```

### 前端

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
```

### 配置说明

#### 后端配置 (backend-fastapi-app/supervisord.conf)
- 监听端口: 9001
- 默认用户名/密码: admin/88888888
- 日志文件: supervisord.log
- 包含配置: supervisor/conf.d/*.conf

#### 前端配置 (frontend-vue-app/supervisord.conf)
- 工作目录: 配置文件所在目录
- 启动命令: pnpm run dev
- 日志文件: logs/vue_app_out.log 和 logs/vue_app_err.log
- 环境变量: NODE_ENV="development"

## 脚本说明

### 后端启动脚本 (backend-fastapi-app/start.sh)
```bash
#!/bin/bash
# 使用supervisord启动后端服务
# 访问地址: http://localhost:8000
supervisord -c supervisord.conf
```

### 前端启动脚本 (frontend-vue-app/start.sh)
```bash
#!/bin/bash
# 使用npm/pnpm运行前端开发服务器
# 访问地址: http://localhost:3000
npm run dev
```

### 一键启动脚本 (start_all.sh)
```bash
#!/bin/bash
# 同时启动前后端服务
# 后端在后台运行(使用supervisord)
# 前端在前台运行(方便查看日志)
# 访问地址:
#  前端: http://localhost:3000
#  后端: http://localhost:8000
```

## 国际化与语言包管理

### msgfmt 语言包使用指南

本项目使用 gettext 的 msgfmt 工具管理多语言翻译文件。语言文件位于 `backend-fastapi-app/lang/` 目录下。

#### 语言文件结构
```
lang/
├── en/              # 英文翻译
│   └── LC_MESSAGES/
│       ├── messages.po  # 翻译文本
│       └── messages.mo  # 编译后的二进制
└── zh_CN/           # 中文翻译
    └── LC_MESSAGES/
        ├── messages.po
        └── messages.mo
```

#### 基本操作流程

1. 编辑 .po 文件
```bash
# 编辑翻译文本
vim backend-fastapi-app/lang/en/LC_MESSAGES/messages.po
```

2. 编译 .mo 文件
```bash
# 进入语言目录
cd backend-fastapi-app/lang/en/LC_MESSAGES/

# 使用 msgfmt 编译
msgfmt messages.po -o messages.mo
```

3. 更新翻译缓存
```bash
# 重启后端服务使新翻译生效
supervisorctl restart backend
```

#### 常用 msgfmt 命令

| 命令 | 说明 |
|------|------|
| `msgfmt messages.po -o messages.mo` | 编译 .po 到 .mo |
| `msgfmt -c messages.po` | 检查 .po 文件语法 |
| `msgfmt --statistics messages.po` | 显示翻译统计 |

```
cd backend-fastapi-app && python babel.py compile
```
#### 翻译文件格式说明

.po 文件示例:
```po
msgid "Welcome"
msgstr "欢迎"

msgid "User not found"
msgstr "用户不存在"
```

- `msgid`: 原始文本 (英文)
- `msgstr`: 翻译文本



## 贡献指南

欢迎提交 Pull Request 或 Issue

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件
