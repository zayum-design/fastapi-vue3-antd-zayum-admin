import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

// 自定义插件来注入全局变量
function injectMetadata(env: Record<string, string>) {
  return {
    name: 'inject-metadata',
    transformIndexHtml(html: string) {
      return html.replace(
        '<head>',
        `<head><script>
          window.__ZAYUM_ADMIN_METADATA__ = {
            authorEmail: 'yixiniis@foxmail.com',
            authorName: 'Zayum',
            authorUrl: 'http://zayum.com',
            buildTime: new Date().toISOString(),
            dependencies: {},
            description: 'A python admin pannel',
            devDependencies: {},
            homepage: 'http://zayum.com',
            license: 'MIT',
            repositoryUrl: 'https://github.com/zayum-design/fastapi-vue3-antd-zayum-admin',
            version: '1.0.2'
          };
          window._ZAYUM_ADMIN_PRO_APP_CONF_ = {
            VITE_GLOB_API_URL: '${env.VITE_GLOB_API_URL}',
            VITE_GLOB_URL: '${env.VITE_GLOB_URL}'
          };
        </script>`
      )
    }
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [
      vue(),
      tailwindcss(),
      injectMetadata(env), // 添加自定义插件并传入env
    ],
  envPrefix: 'VITE_',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
    server: {
      proxy: {
        '/api': {
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          target: 'http://localhost:5320/api',
          ws: true,
        },
      },
    },
  };
})
