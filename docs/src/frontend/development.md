# 本地开发

## 环境准备

1. **Node.js 环境**
   - 推荐版本: v16.x 或更高
   - 安装方式:
     ```bash
     # 使用nvm安装
     nvm install 16
     nvm use 16
     ```

2. **包管理器**
   - 推荐使用 pnpm:
     ```bash
     npm install -g pnpm
     ```

## 启动开发服务器

1. 安装依赖
```bash
cd frontend-vue-app
pnpm install
```

2. 启动开发服务器
```bash
pnpm dev
```

3. 访问开发环境
```
http://localhost:3000
```

## 开发工具配置

1. **VSCode 推荐插件**
   - Volar (Vue 官方插件)
   - TypeScript Vue Plugin
   - ESLint
   - Prettier
   - Tailwind CSS IntelliSense

2. **调试配置**
   - Chrome Vue Devtools
   - Vue 3 SFC 调试支持

## 热重载与构建

1. **开发模式**
   - 实时热重载
   - 错误覆盖层
   - 类型检查

2. **构建生产版本**
```bash
pnpm build
```

3. **预览生产构建**
```bash
pnpm preview
```

## 代码质量检查

1. **ESLint 检查**
```bash
pnpm lint
```

2. **类型检查**
```bash
pnpm type-check
```

3. **格式化代码**
```bash
pnpm format
