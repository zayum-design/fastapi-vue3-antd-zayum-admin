import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'
import fs from 'fs'
import path from 'path'

// 读取版本号
function readVersion(): string {
  try {
    // 尝试从项目根目录的 VERSION 文件读取
    const versionPath = path.resolve(__dirname, '..', '..', 'VERSION')
    if (fs.existsSync(versionPath)) {
      const version = fs.readFileSync(versionPath, 'utf-8').trim()
      return version || 'unknown'
    }
    
    // 尝试从当前目录的 VERSION 文件读取
    const localVersionPath = path.resolve(__dirname, 'VERSION')
    if (fs.existsSync(localVersionPath)) {
      const version = fs.readFileSync(localVersionPath, 'utf-8').trim()
      return version || 'unknown'
    }
  } catch (error) {
    console.warn('Failed to read version file:', error)
  }
  return 'unknown'
}

const projectVersion = readVersion()

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
            version: '${projectVersion}'
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
