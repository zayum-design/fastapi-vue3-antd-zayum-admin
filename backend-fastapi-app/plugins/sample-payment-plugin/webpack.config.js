// webpack.config.js
const { ModuleFederationPlugin } = require('webpack').container;

module.exports = {
  output: {
    publicPath: 'http://localhost:8000/', // 必须与最终访问URL一致
  },
  plugins: [
    new ModuleFederationPlugin({
      name: 'remote_app', // 全局变量名 (window.remote_app)
      filename: 'remoteEntry.js',
      exposes: {
        './PaymentRecords': './src/frontend/components/PaymentRecords.vue',
        './PaymentSettings': './src/frontend/components/PaymentSettings.vue'
      },
      shared: {
        vue: { singleton: true } // 共享Vue避免重复加载
      }
    })
  ]
};