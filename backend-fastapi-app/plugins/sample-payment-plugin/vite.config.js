import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'sample-payment-plugin',
      filename: 'remoteEntry.js',
      // 导出模块
      exposes: {
        './PaymentRecords': './frontend/components/PaymentRecords.vue',
        './PaymentSettings': './frontend/components/PaymentSettings.vue',
      },
      // 共享依赖
      shared: ['vue']
    })
  ],
  build: {
    target: 'esnext',
    minify: 'terser',
    cssCodeSplit: false,
    outDir: 'dist',
  }
})