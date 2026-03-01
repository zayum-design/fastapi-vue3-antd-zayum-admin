// 插件前端入口文件
export const routes = [
  {
    path: '/',
    name: 'DemoPluginHome',
    component: () => import('./components/DemoPage.vue'),
    meta: {
      title: '示例插件',
      icon: 'el-icon-s-promotion'
    }
  },
  {
    path: '/demo',
    name: 'DemoPage',
    component: () => import('./components/DemoPage.vue'),
    meta: {
      title: '示例插件演示',
      icon: 'el-icon-s-promotion'
    }
  }
]

// 插件组件
export const components = {
  'DemoWidget': () => import('./components/DemoPage.vue')
}

// 插件配置
export const pluginConfig = {
  name: 'demo-plugin',
  displayName: '示例插件',
  version: '1.0.0'
}
