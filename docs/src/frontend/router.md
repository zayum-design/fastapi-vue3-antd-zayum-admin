# 路由和菜单

## 路由配置

### 路由结构

1. **核心路由 (coreRoutes)**
   - 基础布局路由
   - 登录/注册页
   - 错误页(403/404/500)

2. **静态路由 (staticRoutes)**
   - 固定显示在菜单中的路由
   - 如仪表盘、个人中心等

3. **动态路由 (dynamicRoutes)**
   - 根据用户权限动态生成
   - 从后端API获取

### 路由模块示例

```typescript
// src/router/routes/modules/user.ts
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/user',
    name: 'user',
    component: () => import('@/views/user/index.vue'),
    meta: {
      title: '用户管理',
      icon: 'user',
      roles: ['admin']
    }
  }
];

export default routes;
```

## 菜单配置

菜单通过路由的 `meta` 属性配置：

```typescript
meta: {
  title: '菜单标题',    // 菜单显示名称
  icon: 'icon-name',   // 菜单图标
  roles: ['admin'],    // 可访问角色
  hidden: false,       // 是否隐藏菜单
  keepAlive: true      // 是否缓存页面
}
```

## 权限控制

1. **路由守卫流程**
   ```mermaid
   graph TD
     A[路由跳转] --> B{是否已安装}
     B -->|是| C{权限校验}
     B -->|否| D[跳转安装页]
     C -->|有权限| E[进入页面]
     C -->|无权限| F[跳转403]
   ```

2. **权限校验逻辑**
   - 前端: 根据用户角色过滤路由
   - 后端: 返回用户可访问的路由列表

## 最佳实践

1. **路由懒加载**
   ```typescript
   component: () => import('@/views/user/index.vue')
   ```

2. **路由分组**
   - 按功能模块组织路由文件
   - 统一在 `src/router/routes/index.ts` 导出

3. **动态标题**
   ```typescript
   router.afterEach((to) => {
     document.title = to.meta.title + ' | Zayum Admin'
   })
