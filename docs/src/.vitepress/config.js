import { defineConfig } from 'vitepress'
import path from 'path'
import { prismjsPlugin } from '@vuepress/plugin-prismjs'

export default defineConfig({
  title: 'Zayum Admin 文档',
  description: 'FastAPI + Vue3 后台管理系统文档',
  themeConfig: {
    ignoreDeadLinks: true,
    nav: [
      { text: '首页', link: '/' },
      { text: 'GitHub', link: 'https://github.com/zayum-design/fastapi-vue3-antd-zayum-admin' }
    ],
    sidebar: [
      {
        text: '简介',
        items: [
          { text: '关于 Zayum Admin', link: '/intro/about' },
          { text: '为什么选择我们?', link: '/intro/why' }
        ]
      },
      {
        text: '快速开始',
        link: '/quick-start/'
      },
      {
        text: '通用文档',
        items: [
          { text: '项目架构', link: '/architecture' },
          { text: '代码规范', link: '/coding-style' },
          { text: '开发流程', link: '/development-process' }
        ]
      },
      {
        text: '前端文档',
        items: [
          { text: '基础概念', link: '/frontend/basic' },
          { text: '本地开发', link: '/frontend/development' },
          { text: '路由和菜单', link: '/frontend/router' },
          { text: '配置', link: '/frontend/config' },
          { text: '图标', link: '/frontend/icons' },
          { text: '样式', link: '/frontend/advanced-styles' },
          { text: '外部模块', link: '/frontend/modules' },
          { text: '构建与部署', link: '/frontend-deploy' }
        ]
      },
      {
        text: '后端文档',
        items: [
          { text: 'API文档', link: '/backend/api' },
          { text: '环境配置', link: '/backend/env' }
        ]
      }
    ]
  },
  markdown: {
    ignoreDeadLinks: true
  },
  vite: {
    plugins: [
      prismjsPlugin({
        languages: ['env'],
      }),
    ]
  }
})
