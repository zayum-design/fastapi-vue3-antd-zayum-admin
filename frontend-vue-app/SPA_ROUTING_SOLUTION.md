# SPA 路由刷新问题解决方案

## 问题描述

当 `frontend-vue-app/dist` 中生成的静态文件运行在服务器上时，路由刷新后页面会显示 404 错误。

## 问题原因

1. **路由模式问题**：项目使用的是 Vue Router 的 HTML5 History 模式 (`createWebHistory`)
2. **服务器配置**：虽然 nginx 配置中已经有了 SPA 支持，但缺少必要的环境变量配置
3. **环境变量缺失**：缺少 `VITE_ROUTER_HISTORY` 环境变量配置

## 解决方案

### 1. 环境变量配置

已更新以下环境配置文件，添加了 `VITE_ROUTER_HISTORY` 配置：

- `.env.production` - 生产环境配置
- `.env.development` - 开发环境配置

```bash
# 路由历史模式
# hash: 使用 hash 模式，兼容性好，不需要服务器配置
# history: 使用 HTML5 history 模式，需要服务器配置支持
VITE_ROUTER_HISTORY=history
```

### 2. 服务器配置验证

当前的 nginx 配置已经正确配置了 SPA 支持：

```nginx
# 处理 SPA 路由
location / {
    try_files $uri $uri/ /index.html;
}
```

这个配置确保了所有路由请求都会回退到 `index.html`，由前端路由处理。

### 3. 可选方案：使用 Hash 模式

如果仍然遇到问题，可以将 `VITE_ROUTER_HISTORY` 设置为 `hash`：

```bash
VITE_ROUTER_HISTORY=hash
```

Hash 模式的优点：
- 不需要服务器配置
- 兼容性更好
- URL 格式：`http://example.com/#/path`

## 部署步骤

1. **重新构建前端应用**：
   ```bash
   cd frontend-vue-app
   npm run build
   ```

2. **部署到服务器**：
   - 将 `dist` 目录内容上传到服务器
   - 确保 nginx 配置正确
   - 重启 nginx 服务

3. **验证部署**：
   - 访问应用根路径
   - 导航到子路由
   - 刷新页面，应该能正常显示

## 故障排除

如果仍然遇到问题：

1. **检查 nginx 配置**：确保 `try_files` 指令正确配置
2. **检查环境变量**：确保 `VITE_ROUTER_HISTORY` 正确设置
3. **检查构建过程**：确保构建时使用了正确的环境配置
4. **查看浏览器控制台**：检查是否有 JavaScript 错误

## 技术说明

- **HTML5 History 模式**：需要服务器支持，URL 格式更友好
- **Hash 模式**：不需要服务器支持，兼容性更好
- **SPA 路由原理**：所有路由都由前端 JavaScript 处理，服务器只提供 `index.html`

## 相关文件

- `src/router/index.ts` - 路由配置
- `vite.config.ts` - 构建配置
- `nginx.conf` - 服务器配置
- `.env.*` - 环境变量配置
