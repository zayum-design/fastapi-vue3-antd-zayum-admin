# 文档运行指南

本文档说明如何运行本项目的文档网站。

## 项目概述

文档使用 [VitePress](https://vitepress.dev/) 构建，是一个静态站点生成器，基于 Vue 3 和 Vite。

## 环境要求

- Node.js 18 或更高版本
- npm 或 pnpm（推荐 pnpm）

## 运行步骤

### 1. 进入文档目录

```bash
cd docs
```

### 2. 安装依赖

如果尚未安装依赖，请执行：

```bash
npm install
```

或使用 pnpm：

```bash
pnpm install
```

### 3. 启动开发服务器

在本地启动开发服务器，支持热重载：

```bash
npm run dev
```

或

```bash
pnpm run dev
```

服务器启动后，打开浏览器访问 [http://localhost:5173](http://localhost:5173)。

### 4. 构建文档

生成静态文件，用于生产环境部署：

```bash
npm run build
```

或

```bash
pnpm run build
```

构建后的文件位于 `docs/.vitepress/dist`。

### 5. 预览构建结果

在本地预览构建后的静态站点：

```bash
npm run serve
```

或

```bash
pnpm run serve
```

## 脚本说明

- `dev`：启动开发服务器
- `build`：构建静态文件
- `serve`：预览构建结果

## 常见问题

### 依赖安装失败

确保 Node.js 版本符合要求（建议 18+）。如果使用 npm，可以尝试清除缓存：

```bash
npm cache clean --force
```

然后重新安装。

### 端口占用

如果默认端口 5173 被占用，可以在 `src/.vitepress/config.js` 中配置 `server.port`。

### 缺少依赖

如果运行脚本时提示模块未找到，请确保已安装所有依赖：

```bash
npm ci
```

## 更多信息

查看 [VitePress 官方文档](https://vitepress.dev/) 了解更多配置和用法。

## 贡献

欢迎提交 Issue 或 Pull Request 改进文档。
