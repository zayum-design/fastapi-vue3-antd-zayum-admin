# 基础概念

## 前端架构

Zayum Admin 前端基于以下核心架构设计：

1. **组件化开发**
   - 使用 Vue3 Composition API
   - 基于 Ant Design Vue 组件库
   - 自定义业务组件

2. **状态管理**
   - Pinia 状态管理
   - 模块化 store 设计
   - 类型安全的 TypeScript 支持

3. **路由系统**
   - 基于 Vue Router 4
   - 动态路由加载
   - 路由权限控制

## 核心目录结构

```
frontend-vue-app/
├── src/
│   ├── _core/                  # 核心业务组件
│   ├── api/                    # API 请求封装
│   ├── assets/                 # 静态资源
│   ├── components/             # 公共组件
│   ├── constants/              # 常量定义
│   ├── layouts/                # 页面布局
│   ├── locales/                # 国际化
│   ├── plugins/                # 插件系统
│   ├── router/                 # 路由配置
│   ├── stores/                 # 状态管理
│   ├── utils/                  # 工具函数
│   └── views/                  # 页面视图
```

## 开发规范

1. **命名约定**
   - 组件: PascalCase (如 `UserList.vue`)
   - 变量: camelCase
   - 常量: UPPER_CASE

2. **代码风格**
   - 使用 TypeScript 严格模式
   - ESLint + Prettier 代码规范
   - 组件单文件结构规范

3. **API 调用**
   - 使用 axios 封装
   - 统一的请求拦截
   - 类型化的响应处理
