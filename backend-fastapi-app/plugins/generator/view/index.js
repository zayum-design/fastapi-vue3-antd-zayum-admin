// 插件前端入口文件
export const routes = [
  {
    path: '/',
    name: 'GeneratorHome',
    component: () => import('./components/generator.vue'),
    meta: {
      title: '插件生成器',
      icon: 'el-icon-s-promotion'
    }
  }
]

// 插件组件
export const components = {
  'GeneratorWidget': () => import('./components/generator.vue')
}

// 插件配置
export const pluginConfig = {
  name: 'generator',
  displayName: '插件生成器',
  version: '1.0.0'
}
