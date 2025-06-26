declare module '*.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// 添加 radix-vue 的模块声明
declare module 'radix-vue' {
  export * from 'radix-vue';
}