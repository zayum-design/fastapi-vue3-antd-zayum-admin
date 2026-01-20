# 前端部署指南

## 部署方式选择

Zayum Admin 前端提供多种部署方式，您可以根据需求选择最适合的方式：

### 1. 使用部署脚本（推荐）

我们提供了强大的自动化部署脚本 `deploy.sh`，支持一键部署前端：

```bash
# 仅部署前端
./deploy.sh --frontend

# 完整部署（后端 + 前端）
./deploy.sh --all

# 交互式选择部署模式
./deploy.sh
```

#### 部署脚本特性：
- **自动化环境检查**：自动检测 Node.js、npm/pnpm 等环境
- **依赖自动安装**：自动安装项目所需的所有依赖
- **多种运行模式**：支持开发模式、生产模式、构建模式
- **交互式配置**：提供友好的交互界面，可配置访问域名
- **详细日志输出**：提供详细的部署日志，便于排查问题

### 2. 手动部署

如果您希望手动部署前端，可以参考以下步骤：

#### 步骤 1：安装依赖

```bash
cd frontend-vue-app
npm install
# 或使用 pnpm（推荐）
pnpm install
```

#### 步骤 2：配置环境变量

复制环境变量示例文件并配置：

```bash
cp .env.example .env.development
# 编辑 .env.development 文件，配置 API 地址等
```

#### 步骤 3：启动服务

```bash
# 开发模式（热重载）
npm run dev
# 或
pnpm dev

# 生产模式构建
npm run build
# 或
pnpm build

# 预览生产构建
npm run preview
# 或
pnpm preview
```

### 3. 使用 Docker 部署

对于生产环境，我们推荐使用 Docker 进行部署：

```bash
# 构建 Docker 镜像
docker build -t zayum-admin-frontend .

# 运行容器
docker run -p 5173:80 zayum-admin-frontend

# 或使用 Docker Compose（推荐）
docker-compose up -d
```

## 运行模式说明

### 开发模式（Development）
- 启用热重载（Hot Module Replacement）
- 启用源代码映射（Source Maps）
- 启用开发工具
- 访问地址：http://localhost:5173

### 生产模式（Production）
- 代码压缩和优化
- 移除开发工具
- 启用缓存和性能优化
- 可通过 Nginx 等 Web 服务器部署

### 构建模式（Build）
- 仅构建静态文件，不启动服务器
- 输出到 `dist/` 目录
- 适合 CI/CD 流水线

## 环境配置

### 环境变量

前端支持以下环境变量：

```env
# API 基础地址
VITE_API_BASE_URL=http://localhost:8000

# 应用标题
VITE_APP_TITLE=Zayum Admin

# 启用/禁用功能
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=false

# 其他配置
VITE_DEFAULT_LANGUAGE=zh-CN
VITE_THEME_COLOR=#1890ff
```

### 配置文件

主要配置文件：
- `vite.config.ts` - Vite 构建配置
- `tailwind.config.ts` - Tailwind CSS 配置
- `tsconfig.json` - TypeScript 配置

## 常见问题

### 1. 端口被占用

如果默认端口 5173 被占用，Vite 会自动尝试其他端口。您也可以手动指定端口：

```bash
# 在 package.json 中修改 scripts
"dev": "vite --port 3000"
```

### 2. 依赖安装失败

如果依赖安装失败，可以尝试：

```bash
# 清除缓存
npm cache clean --force
# 或
pnpm store prune

# 重新安装
rm -rf node_modules package-lock.json
npm install
```

### 3. 构建失败

如果构建失败，可以检查：

1. TypeScript 类型错误：运行 `npm run type-check`
2. 内存不足：增加 Node.js 内存限制 `NODE_OPTIONS=--max-old-space-size=4096`
3. 网络问题：检查网络连接，或使用国内镜像源

## 性能优化

### 构建优化

1. **代码分割**：自动按路由分割代码
2. **Tree Shaking**：自动移除未使用的代码
3. **图片优化**：自动压缩图片资源
4. **Gzip 压缩**：启用 Gzip 压缩

### 运行时优化

1. **懒加载**：路由和组件懒加载
2. **缓存策略**：合理的 HTTP 缓存头
3. **CDN 加速**：静态资源使用 CDN

## 监控和维护

### 日志查看

```bash
# 查看实时日志
tail -f logs/frontend.log

# 查看错误日志
grep -i error logs/frontend.log
```

### 性能监控

1. **浏览器 DevTools**：使用 Performance 和 Lighthouse 工具
2. **Web Vitals**：监控核心 Web 指标
3. **错误监控**：集成 Sentry 等错误监控服务

## 更新和升级

### 更新依赖

```bash
# 更新所有依赖
npm update
# 或
pnpm update

# 更新特定依赖
npm update package-name
```

### 项目升级

1. 备份当前项目
2. 拉取最新代码
3. 更新依赖
4. 测试功能
5. 部署更新

---

**注意**：生产环境部署前，请务必进行充分的测试，确保系统稳定运行。
