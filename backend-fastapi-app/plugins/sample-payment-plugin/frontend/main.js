// plugins/sample-payment-plugin/frontend/main.js
import PaymentRecords from './components/PaymentRecords.vue'
import PaymentSettings from './components/PaymentSettings.vue'

export default {
  // 插件安装方法
  install: (app) => {
    app.component('PaymentRecords', PaymentRecords)
    app.component('PaymentSettings', PaymentSettings)
  },
  
  // 导出组件，供远程加载器使用
  components: {
    PaymentRecords,
    PaymentSettings
  },
  
  // 导出路由配置
  routes: [
    {
      path: '/plugins/sample-payment-plugin/records',
      name: 'payment-records',
      component: 'PaymentRecords',
      meta: {
        title: '支付记录',
        icon: 'payment'
      }
    },
    {
      path: '/plugins/sample-payment-plugin/settings',
      name: 'payment-settings',
      component: 'PaymentSettings',
      meta: {
        title: '支付设置',
        icon: 'settings'
      }
    }
  ]
}
