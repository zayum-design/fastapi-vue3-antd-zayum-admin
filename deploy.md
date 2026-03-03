# Zayum Admin 部署脚本使用文档

> 适用于 FastAPI + Vue3 全栈项目的本地部署工具

## 📋 目录

- [简介](#简介)
- [快速开始](#快速开始)
- [功能特性](#功能特性)
- [使用方法](#使用方法)
- [数据库配置](#数据库配置)
- [模块说明](#模块说明)
- [故障排查](#故障排查)
- [常见问题](#常见问题)

---

## 简介

`deploy.sh` 是 Zayum Admin 项目的本地部署脚本，采用模块化设计，提供交互式和命令行两种部署方式。脚本支持一键部署完整应用、单独部署前后端、以及灵活的环境配置。

### 版本信息

- **版本**: v3.0.0
- **适用系统**: macOS / Linux
- **依赖要求**: 
  - Python 3.8+
  - Node.js 16+
  - npm 或 yarn

---

## 快速开始

### 1. 进入项目目录

```bash
cd /path/to/fastapi-vue3-antd-zayum-admin
```

### 2. 运行部署脚本

**交互式模式**（推荐新手）：
```bash
./deploy.sh
```

**命令行模式**（适合熟练用户）：
```bash
# 完整部署
./deploy.sh --all

# 仅部署后端
./deploy.sh --backend

# 仅部署前端
./deploy.sh --frontend

# 仅配置环境
./deploy.sh --config
```

### 3. 按照提示完成配置

脚本会引导您完成：
1. 环境检查
2. 数据库选择和配置
3. 域名配置
4. 部署执行

---

## 功能特性

### 🎯 核心功能

| 功能 | 说明 |
|------|------|
| **智能环境检测** | 自动检查 Python、Node.js 等依赖是否安装 |
| **数据库向导** | 交互式配置 MySQL / PostgreSQL / SQLite |
| **域名配置助手** | 引导式配置前后端域名和 API 地址 |
| **安全部署模式** | 支持安全模式（保留数据）和强制模式（全新安装） |
| **完整日志记录** | 详细的部署过程记录到 `logs/deploy.log` |

### 📦 部署模式

| 模式 | 命令 | 说明 |
|------|------|------|
| 完整部署 | `--all` / `-a` | 部署后端 + 前端 |
| 仅后端 | `--backend` / `-b` | 只部署 FastAPI 后端服务 |
| 仅前端 | `--frontend` / `-f` | 只部署 Vue3 前端应用 |
| 仅配置 | `--config` / `-c` | 初始化数据库和域名配置 |

### 🗄️ 支持的数据库

| 数据库 | 适用场景 | 特点 |
|--------|----------|------|
| **MySQL** | 生产环境 | 高性能、高可用、支持复杂查询 |
| **PostgreSQL** | 生产/开发 | 功能丰富、严格的数据完整性 |
| **SQLite** | 开发测试 | 零配置、单文件、轻量快速 |

---

## 使用方法

### 交互式模式

直接运行脚本不加参数：

```bash
./deploy.sh
```

您将看到如下菜单：

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     Zayum Admin 本地部署脚本                    v3.0.0       ║
║     FastAPI + Vue3 全栈项目一键部署工具                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

══════════════════════════════════════════════════════════════
  请选择部署模式
══════════════════════════════════════════════════════════════

  1) 完整部署 - 后端 + 前端 (推荐首次使用)
  2) 仅部署后端 - 只部署 FastAPI 后端服务
  3) 仅部署前端 - 只部署 Vue3 前端应用
  4) 仅配置环境 - 初始化数据库和域名配置
  5) 显示帮助信息
  6) 退出

请选择 [1-6]:
```

### 命令行参数

```bash
# 显示帮助
./deploy.sh --help

# 显示版本
./deploy.sh --version

# 完整部署
./deploy.sh --all

# 仅部署后端（安全模式）
./deploy.sh --backend

# 仅部署前端（开发模式）
./deploy.sh --frontend

# 仅配置环境
./deploy.sh --config
```

### 部署安全模式

在交互式部署时，脚本会询问部署模式：

- **安全模式**（推荐）：保护现有数据表和配置文件，适用于更新部署
- **强制模式**：覆盖所有已有配置，适用于全新安装或重置环境

---

## 数据库配置

### MySQL 配置示例

```
MySQL 主机地址 [默认: localhost]: localhost
MySQL 端口 [默认: 3306]: 3306
MySQL 用户名: root
MySQL 密码: [输入密码]
数据库名称 [默认: zayum_admin]: zayum_admin
```

### PostgreSQL 配置示例

```
PostgreSQL 主机地址 [默认: localhost]: localhost
PostgreSQL 端口 [默认: 5432]: 5432
PostgreSQL 用户名: postgres
PostgreSQL 密码: [输入密码]
数据库名称 [默认: zayum_admin]: zayum_admin
```

### SQLite 配置示例

```
SQLite 数据库文件名 [默认: db.sqlite3]: db.sqlite3
```

### 数据库连接测试

配置完成后，脚本会自动测试数据库连接。如果连接失败，脚本会继续执行并在安装时自动创建数据库。

---

## 模块说明

### 目录结构

```
deploy/
├── main.sh           # 主脚本入口，整合所有模块
├── config.sh         # 配置模块，包含常量和工具函数
├── utils.sh          # 工具模块，环境检查和菜单
├── database_utils.sh # 数据库模块，数据库配置和管理
├── backend_utils.sh  # 后端模块，后端部署和管理
└── frontend_utils.sh # 前端模块，前端部署和管理
```

### 各模块职责

#### config.sh
- 颜色定义和输出格式
- 路径配置（项目根目录、前后端目录）
- 常量定义（部署模式、数据库类型）
- 默认配置（域名、端口）
- 通用工具函数（日志、确认提示等）

#### utils.sh
- 帮助和版本信息显示
- 环境检查（Python、Node.js、Git）
- 项目结构检查
- 交互式菜单（部署模式选择）
- 命令行参数解析
- 部署状态管理
- 配置保存和加载

#### database_utils.sh
- 数据库类型选择向导
- MySQL / PostgreSQL / SQLite 配置
- 后端 `.env` 文件生成
- 数据库连接测试

#### backend_utils.sh
- 后端部署主流程
- 仅配置后端环境
- 后端服务管理（启动/停止/状态）
- 后端信息显示

#### frontend_utils.sh
- 前端域名配置向导
- 环境文件管理（`.env.development` / `.env.production`）
- 开发/生产/构建三种模式部署
- 前端信息显示

---

## 故障排查

### 环境检查失败

**问题**: 提示 Python 或 Node.js 未安装

**解决**:
```bash
# macOS (使用 Homebrew)
brew install python@3.11
brew install node

# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nodejs npm

# CentOS/RHEL
sudo yum install python3 python3-pip nodejs npm
```

### 数据库连接失败

**问题**: 配置 MySQL/PostgreSQL 后连接测试失败

**解决**:
1. 检查数据库服务是否运行：
   ```bash
   # MySQL
   sudo systemctl status mysql
   
   # PostgreSQL
   sudo systemctl status postgresql
   ```

2. 检查用户名密码是否正确

3. 检查数据库是否存在（脚本会在安装时自动创建）

4. 使用 SQLite 绕过数据库服务问题

### 前端安装依赖失败

**问题**: `npm install` 报错

**解决**:
```bash
# 清除缓存后重试
cd frontend-vue-app
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### 端口被占用

**问题**: 后端启动提示端口 8000 被占用

**解决**:
1. 修改 `backend-fastapi-app/.env` 中的 `PORT` 值
2. 或查找并停止占用端口的进程：
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

### 查看日志

部署日志保存在 `logs/deploy.log`：
```bash
tail -f logs/deploy.log
```

后端日志：
```bash
tail -f backend-fastapi-app/logs/app.log
```

---

## 常见问题

### Q: 如何重新部署？

**A**: 
1. 安全模式重新部署（保留数据）：
   ```bash
   ./deploy.sh --all
   # 选择"安全模式"
   ```

2. 强制模式重新部署（全新安装）：
   ```bash
   rm -f backend-fastapi-app/install.lock frontend-vue-app/install.lock
   ./deploy.sh --all
   # 选择"强制模式"
   ```

### Q: 如何修改数据库配置？

**A**: 运行配置模式：
```bash
./deploy.sh --config
# 选择"配置后端环境"
```

或直接编辑 `backend-fastapi-app/.env` 文件。

### Q: 如何修改前端域名？

**A**: 运行配置模式：
```bash
./deploy.sh --config
# 选择"配置前端环境"
```

或直接编辑：
- 开发环境：`frontend-vue-app/.env.development`
- 生产环境：`frontend-vue-app/.env.production`

### Q: 部署后如何访问？

**A**: 
- 后端 API: `http://localhost:8000`
- Swagger 文档: `http://localhost:8000/docs`
- 前端开发服务器: `http://localhost:5173`
- 后台登录: `http://localhost:5173/admin/login`
- 默认账号: `admin / admin123`

### Q: 如何停止服务？

**A**:
```bash
# 停止后端
cd backend-fastapi-app
kill $(cat .backend_pid)

# 停止前端（开发服务器）
# 按 Ctrl+C 即可
```

### Q: 配置文件保存在哪里？

**A**:
- 部署配置: `.deploy-config`（项目根目录）
- 后端配置: `backend-fastapi-app/.env`
- 前端开发配置: `frontend-vue-app/.env.development`
- 前端生产配置: `frontend-vue-app/.env.production`
- 部署日志: `logs/deploy.log`

---

## 更新日志

### v3.0.0
- ✅ 全新模块化架构设计
- ✅ 交互式数据库配置向导
- ✅ 支持 MySQL / PostgreSQL / SQLite
- ✅ 安全模式和强制模式部署
- ✅ 完善的日志记录系统
- ✅ 新手友好的交互提示

---

## 技术支持

如有问题，请：
1. 查看本文档的故障排查章节
2. 检查日志文件 `logs/deploy.log`
3. 提交 Issue 到项目仓库

---

**祝您部署顺利！** 🚀
