# 图标系统

## 图标来源

1. **Ant Design Vue 图标**
   ```vue
   <template>
     <FileAddOutlined />
     <DeleteOutlined />
   </template>
   <script setup>
   import { FileAddOutlined, DeleteOutlined } from "@ant-design/icons-vue"
   </script>
   ```

2. **Lucide 图标**
   ```vue
   <template>
     <icon-lucide-area-chart />
   </template>
   ```

3. **自定义 SVG 图标**
   ```vue
   <template>
     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
       <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
       <polyline points="13 2 13 9 20 9"/>
     </svg>
   </template>
   ```

## 图标组件

使用 `ZayumIcon` 组件统一渲染图标：

```vue
<template>
  <ZayumIcon :icon="SvgBellIcon" class="size-8" />
</template>
<script setup>
import { SvgBellIcon } from '@/_core/ui/icons'
</script>
```

## 路由菜单图标配置

在路由meta中配置菜单图标：

```typescript
const routes = [
  {
    path: '/dashboard',
    meta: {
      title: '仪表盘',
      icon: 'lucide:layout-dashboard' // 图标名称或组件
    }
  }
]
```

## 图标使用规范

1. **尺寸规范**
   - 小图标: 16x16 (class="size-4")
   - 中图标: 24x24 (class="size-6")
   - 大图标: 32x32 (class="size-8")

2. **颜色规范**
   ```vue
   <!-- 使用主题色 -->
   <ZayumIcon icon="user" class="text-primary" />
   
   <!-- 使用辅助色 --> 
   <ZayumIcon icon="warning" class="text-warning" />
   ```

3. **动画效果**
   ```css
   .icon-hover {
     transition: transform 0.3s ease;
     &:hover {
       transform: scale(1.2);
     }
   }
   ```

## 自定义图标

1. **添加SVG图标**
   - 将SVG文件放入 `@/_core/ui/icons` 目录
   - 导出为Vue组件

2. **使用图标字体**
   ```css
   @font-face {
     font-family: 'iconfont';
     src: url('@/assets/fonts/iconfont.woff2') format('woff2');
   }
   
   .icon {
     font-family: 'iconfont';
   }
