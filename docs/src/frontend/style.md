# 样式系统

## Tailwind CSS 配置

### 基础配置
```typescript
// tailwind.config.ts
export default {
  darkMode: 'selector',
  content: [
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: 'hsl(var(--primary))',
        secondary: 'hsl(var(--secondary))',
        destructive: 'hsl(var(--destructive))'
      }
    }
  }
}
```

### 插件
- `@tailwindcss/typography`: 排版插件
- `@iconify/tailwind`: 图标选择器
- `tailwindcss-animate`: 动画支持

## 颜色系统

### 主色配置
```css
:root {
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
}
```

### 颜色使用规范
```vue
<template>
  <!-- 主色 -->
  <div class="bg-primary text-primary-foreground"></div>
  
  <!-- 错误色 -->
  <div class="bg-destructive text-destructive-foreground"></div>
</template>
```

## 动画效果

### 内置动画
```javascript
// tailwind.config.ts
extend: {
  animation: {
    'accordion-down': 'accordion-down 0.2s ease-out',
    'float': 'float 5s linear infinite'
  },
  keyframes: {
    float: {
      '0%, 100%': { transform: 'translateY(0)' },
      '50%': { transform: 'translateY(-20px)' }
    }
  }
}
```

### 动画使用
```html
<div class="animate-float"></div>
```

## 组件样式重置

### Ant Design Vue 重置
```css
/* 按钮图标间距 */
.ant-btn > svg + span {
  margin-inline-start: 6px;
}

/* 表单错误状态 */
.form-valid-error .ant-input {
  border-color: hsl(var(--destructive));
}
```

## 最佳实践

1. **优先使用Tailwind工具类**
   ```html
   <!-- 推荐 -->
   <div class="p-4 bg-primary rounded-lg"></div>
   
   <!-- 不推荐 -->
   <div style="padding: 1rem; background: var(--primary); border-radius: 0.5rem;"></div>
   ```

2. **自定义组件样式**
   ```vue
   <script setup>
   import { computed } from 'vue'
   
   const props = defineProps({
     variant: {
       type: String,
       default: 'primary'
     }
   })
   
   const variantClasses = computed(() => {
     return {
       primary: 'bg-primary text-white',
       secondary: 'bg-secondary text-gray-800'
     }[props.variant]
   })
   </script>
   
   <template>
     <button :class="['px-4 py-2 rounded', variantClasses]">
       <slot />
     </button>
   </template>
   ```

3. **响应式设计**
   ```html
   <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
     <!-- 内容 -->
   </div>
