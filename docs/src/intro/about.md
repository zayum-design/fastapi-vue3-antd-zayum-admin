# 关于 Zayum Admin

Zayum Admin 是一个基于 FastAPI 和 Vue3 的前后端分离后台管理系统，采用 Ant Design Vue 作为 UI 组件库，提供完整的权限管理和 CRUD 操作功能。

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
├── frontend-vue-app/        # 前端代码
│   ├── src/                       # 源代码
│   │   ├── api/                   # API 请求
│   │   ├── assets/                # 静态资源
│   │   ├── components/            # 公共组件
│   │   ├── layouts/               # 页面布局
│   │   ├── router/                # 路由配置
│   │   ├── stores/                # 状态管理
│   │   └── views/                 # 页面视图
└── README.md                      # 项目说明
