# 配置系统

## 环境变量配置

项目使用Vite环境变量进行基础配置：

```env
# 前端配置 (frontend-vue-app/.env)
VITE_API_BASE_URL=/api
VITE_APP_VERSION=1.0.0
VITE_APP_TITLE=Zayum Admin
VITE_APP_NAMESPACE=zayum-admin
VITE_ROUTER_HISTORY=hash
```

## 请求配置

### 基础请求配置

```typescript
// src/utils/request.ts
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
})
```

### 请求拦截器

```typescript
request.interceptors.request.use((config) => {
  // 添加认证token
  const token = localStorage.getItem("token")
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

## 表格配置 (VxeTable)

### 基础配置

```typescript
// src/plugins/vxe-table/init.ts
VxeUI.setConfig({
  table: {
    size: 'medium',
    stripe: true,
    border: true
  }
})
```

### 表单配置

```typescript
// src/_core/ui/common-ui/form-ui/config.ts
const formConfig = {
  baseModelPropName: 'value',  // 默认v-model属性名
  modelPropNameMap: {         // 组件特定v-model属性名
    Input: 'value',
    Select: 'value',
    Checkbox: 'checked'
  }
}
```

## 偏好设置

### 默认偏好配置

```typescript
// src/_core/preferences/config.ts
const defaultPreferences = {
  app: {
    theme: 'light',
    locale: 'zh-CN'
  },
  settingShow: true
}
```

### 存储配置

```typescript
// 使用localStorage存储偏好设置
localStorage.setItem(
  `${import.meta.env.VITE_APP_NAMESPACE}-preferences`,
  JSON.stringify(preferences)
)
```

## 最佳实践

1. **环境变量使用**
   ```typescript
   // 生产环境判断
   if (import.meta.env.PROD) {
     // 生产环境逻辑
   }
   ```

2. **配置分层**
   - 基础配置: 环境变量
   - 运行时配置: 偏好设置
   - 组件配置: 各组件配置文件

3. **配置热更新**
   ```typescript
   // 监听配置变化
   watch(preferences, (newVal) => {
     updateCSSVariables(newVal.app.theme)
   })
