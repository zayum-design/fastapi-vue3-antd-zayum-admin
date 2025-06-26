/******/ var __webpack_modules__ = ({});
/******/ var __webpack_require__ = function(moduleId) {
/******/  // Webpack require 实现
/******/ };
/******/ 
/******/ var moduleMap = {
/******/   "./PaymentRecords": () => {
/******/     return Promise.all([__webpack_require__.e("src_frontend_components_PaymentRecords_vue"), __webpack_require__.e("webpack_sharing_consume_default_vue")]).then(() => () => __webpack_require__("./src/frontend/components/PaymentRecords.vue"));
/******/   },
/******/   "./PaymentSettings": () => {
/******/     return Promise.all([__webpack_require__.e("src_frontend_components_PaymentSettings_vue"), __webpack_require__.e("webpack_sharing_consume_default_vue")]).then(() => () => __webpack_require__("./src/frontend/components/PaymentSettings.vue"));
/******/   }
/******/ };
/******/ 
/******/ var remote_app = (() => {
/******/   var modules = {};
/******/   
/******/   // 模块联邦核心方法
/******/   return {
/******/     get: (module) => {
/******/       return (
/******/         moduleMap[module]() ||
/******/         Promise.resolve().then(() => {
/******/           throw new Error('Module "' + module + '" does not exist in container.');
/******/         })
/******/       );
/******/     },
/******/     init: (shareScope) => {
/******/       // 共享作用域初始化
/******/       return Promise.resolve();
/******/     }
/******/   };
/******/ })();
/******/ 
/******/ // 暴露全局变量
/******/ window.remote_app = remote_app;