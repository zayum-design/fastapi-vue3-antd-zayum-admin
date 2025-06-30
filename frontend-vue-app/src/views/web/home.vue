<template>
  <div class="home-page">
    <!-- 顶部导航栏 -->
    <a-layout-header ref="header" class="fixed w-full top-0 z-50 bg-blue-900 transition-colors duration-300">
      <div class="container mx-auto px-4 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <img src="@/assets/logo-2.svg" alt="ZayumAdmin Logo" class="h-8">
          <h1 class="text-xl font-bold text-white">ZayumAdmin</h1>
        </div>
        <a-menu mode="horizontal" class="hidden md:flex border-none bg-transparent">
          <a-menu-item key="home" class="hover:text-white-200 bg-transparent">首页</a-menu-item>
          <a-menu-item key="features" class="hover:text-white-200 bg-transparent">功能</a-menu-item>
          <a-menu-item key="demo" class="hover:text-white-200 bg-transparent">
            <a href="http://demo.zayumadmin.com" target="_blank">Demo</a>
          </a-menu-item>
          <a-menu-item key="docs" class="hover:text-white-200 bg-transparent">
            <a href="http://doc.zayumadmin.com" target="_blank">文档</a>
          </a-menu-item>
          <a-menu-item key="github" class="hover:text-white-200 bg-transparent">
            <a href="https://github.com/easyiit-design/fastapi-vue3-antd-zayum-admin" target="_blank">GitHub</a>
          </a-menu-item>
        </a-menu>
        <a-space wrap>
          <a-button type="primary" @click="$router.push('/user/login')" class="h-10">登录</a-button>
          <a-button @click="$router.push('/register')" class="h-10 ml-4">免费试用</a-button>
        </a-space>
      </div>
    </a-layout-header>

    <!-- 主视觉区域 -->
    <a-layout-content class="bg-blue-900 py-30">
      <div class="container mx-auto px-4 text-center">
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">企业后台管理系统解决方案</h2>
        <p class="text-xl text-blue-100 max-w-2xl mx-auto mb-10">
          基于FastAPI和Vue3构建的企业后台管理系统，提供完整的权限管理和丰富的功能组件
        </p>
        <a-space wrap>
          <a-button type="primary" size="large" href="/register" class="bg-white text-blue-900 hover:bg-blue-100">立即开始</a-button>
          <a-button size="large" href="#features" class="text-white border-white hover:bg-blue-800">了解更多</a-button>
        </a-space>
      </div>
    </a-layout-content>

    <!-- 功能特性 -->
    <a-layout-content id="features" class="py-20 bg-white">
      <div class="container mx-auto px-4">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">功能特性</h2>
        <a-row :gutter="[16, 16]">
          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable>
              <div class="text-blue-600 mb-4">
                <UserOutlined class="text-4xl" />
              </div>
              <h3 class="text-xl font-semibold mb-2 text-gray-800">用户管理</h3>
              <p class="text-gray-600">完整的用户注册/登录流程，基于JWT的身份验证，细粒度的权限控制</p>
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable>
              <div class="text-blue-600 mb-4">
                <SettingOutlined class="text-4xl" />
              </div>
              <h3 class="text-xl font-semibold mb-2 text-gray-800">系统管理</h3>
              <p class="text-gray-600">菜单管理、权限管理、日志管理等后台管理核心功能</p>
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable>
              <div class="text-blue-600 mb-4">
                <FileOutlined class="text-4xl" />
              </div>
              <h3 class="text-xl font-semibold mb-2 text-gray-800">文件管理</h3>
              <p class="text-gray-600">支持文件上传、分类管理，提供丰富的API接口</p>
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable>
              <div class="text-blue-600 mb-4">
                <AppstoreOutlined class="text-4xl" />
              </div>
              <h3 class="text-xl font-semibold mb-2 text-gray-800">插件系统</h3>
              <p class="text-gray-600">支持插件开发和管理，轻松扩展系统功能</p>
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable>
              <div class="text-blue-600 mb-4">
                <GlobalOutlined class="text-4xl" />
              </div>
              <h3 class="text-xl font-semibold mb-2 text-gray-800">国际化支持</h3>
              <p class="text-gray-600">内置多语言支持，轻松实现国际化</p>
            </a-card>
          </a-col>
          <a-col :xs="24" :sm="12" :lg="8">
            <a-card hoverable>
              <div class="text-blue-600 mb-4">
                <DeploymentUnitOutlined class="text-4xl" />
              </div>
              <h3 class="text-xl font-semibold mb-2 text-gray-800">Supervisor管理</h3>
              <p class="text-gray-600">提供完整的进程管理方案，确保服务稳定运行</p>
            </a-card>
          </a-col>
        </a-row>
      </div>
    </a-layout-content>

    <!-- 技术栈 -->
    <a-layout-content class="py-20 bg-gray-50">
      <div class="container mx-auto px-4">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">技术栈</h2>
        <a-row :gutter="[16, 16]">
          <a-col :xs="12" :sm="8" :lg="4">
            <div class="flex flex-col items-center">
            <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI" class="h-12 mb-4">
            <span class="text-gray-700">FastAPI</span>
            </div>
          </a-col>
          <a-col :xs="12" :sm="8" :lg="4">
            <div class="flex flex-col items-center">
            <img src="https://vuejs.org/images/logo.png" alt="Vue.js" class="h-12 mb-4">
            <span class="text-gray-700">Vue 3</span>
            </div>
          </a-col>
          <a-col :xs="12" :sm="8" :lg="4">
            <div class="flex flex-col items-center">
            <img src="https://www.typescriptlang.org/icons/icon-512x512.png" alt="TypeScript" class="h-12 mb-4">
            <span class="text-gray-700">TypeScript</span>
            </div>
          </a-col>
          <a-col :xs="12" :sm="8" :lg="4">
            <div class="flex flex-col items-center">
            <img src="https://antdv.com/assets/logo.1ef800a8.svg" alt="Ant Design Vue" class="h-12 mb-4">
            <span class="text-gray-700">Ant Design Vue</span>
            </div>
          </a-col>
          <a-col :xs="12" :sm="8" :lg="4">
            <div class="flex flex-col items-center">
              <img src="https://tailwindcss.com/_next/static/media/tailwindcss-mark.d52e9897.svg" alt="Tailwind CSS" class="h-12 mb-4">
              <span class="text-gray-700">Tailwind CSS</span>
            </div>
          </a-col>
          <a-col :xs="12" :sm="8" :lg="4">
            <div class="flex flex-col items-center">
              <img src="https://vitejs.dev/logo.svg" alt="Vite" class="h-12 mb-4">
              <span class="text-gray-700">Vite</span>
            </div>
          </a-col>
        </a-row>
      </div>
    </a-layout-content>

    <!-- 快速开始 -->
    <a-layout-content class="py-20 bg-white">
      <div class="container mx-auto px-4 flex flex-col items-center">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-12">快速开始</h2>
        <a-card class="w-full max-w-3xl">
          <div class="mb-6">
            <h3 class="text-xl font-semibold mb-4 text-gray-800">后端安装</h3>
            <pre class="bg-gray-800 text-gray-100 p-4 rounded-md overflow-x-auto"><code>cd backend-fastapi-app
pip install -r requirements.txt
python -m app.initialize_db
uvicorn app.main:app --reload</code></pre>
          </div>
          <div>
            <h3 class="text-xl font-semibold mb-4 text-gray-800">前端安装</h3>
            <pre class="bg-gray-800 text-gray-100 p-4 rounded-md overflow-x-auto"><code>cd frontend-vue-app
npm install
npm run dev</code></pre>
          </div>
        </a-card>
      </div>
    </a-layout-content>

    <!-- 页脚 -->
    <a-layout-footer class="bg-gray-800 text-white py-12">
      <div class="container mx-auto px-4">
        <a-row :gutter="[16, 16]">
          <a-col :xs="24" :md="8">
            <h3 class="text-xl font-semibold mb-4">ZayumAdmin</h3>
            <p class="text-gray-400">标准企业后台管理系统解决方案</p>
          </a-col>
          <a-col :xs="24" :md="8">
            <h3 class="text-xl font-semibold mb-4">链接</h3>
            <ul class="space-y-2">
              <li><a href="http://demo.zayumadmin.com" target="_blank" class="text-gray-400 hover:text-white">Demo演示</a></li>
              <li><a href="http://doc.zayumadmin.com" target="_blank" class="text-gray-400 hover:text-white">文档</a></li>
              <li><a href="https://github.com/easyiit-design/fastapi-vue3-antd-zayum-admin" target="_blank" class="text-gray-400 hover:text-white">GitHub</a></li>
            </ul>
          </a-col>
          <a-col :xs="24" :md="8">
            <h3 class="text-xl font-semibold mb-4">许可证</h3>
            <p class="text-gray-400">MIT License</p>
          </a-col>
        </a-row>
        <div class="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
          <p>© 2025 ZayumAdmin. All rights reserved.</p>
        </div>
      </div>
    </a-layout-footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'
import {
  UserOutlined,
  SettingOutlined,
  FileOutlined,
  AppstoreOutlined,
  GlobalOutlined,
  DeploymentUnitOutlined
} from '@ant-design/icons-vue'

export default defineComponent({
  name: 'HomePage',
  components: {
    UserOutlined,
    SettingOutlined,
    FileOutlined,
    AppstoreOutlined,
    GlobalOutlined,
    DeploymentUnitOutlined
  },
  setup() {
    const header = ref<HTMLElement | null>(null)

    const handleScroll = () => {
      if (header.value) {
        if (window.scrollY > 50) {
          header.value.classList.add('bg-blue-800', 'shadow-sm')
          header.value.classList.remove('bg-blue-900')
        } else {
          header.value.classList.add('bg-blue-900')
          header.value.classList.remove('bg-blue-800', 'shadow-sm')
        }
      }
    }

    onMounted(() => {
      window.addEventListener('scroll', handleScroll)
    })

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
    })

    return {
      header
    }
  }
})
</script>

<style scoped>
.home-page {
  @apply min-h-screen flex flex-col;
}

/* 覆盖Ant Design Vue菜单样式 */
:deep(.ant-menu) {
  background: transparent !important;
}
:deep(.ant-menu-horizontal) {
  border-bottom: none !important;
}
:deep(.ant-menu-item),
:deep(.ant-menu-item:hover),
:deep(.ant-menu-item-selected),
:deep(.ant-menu-item-active) {
  color: white !important;
}
:deep(.ant-menu-item:hover) {
  color: #bfdbfe !important; /* 浅蓝色hover效果 */
}
</style>
