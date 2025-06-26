/**
 * 此文件为 Zayum Drawer 组件及其相关逻辑的实现文件，
 * 主要通过 Vue 的组合式 API（如 defineComponent、provide/inject、reactive 等）构建 Drawer 组件，
 * 同时利用自定义的 DrawerApi 实现对 Drawer 行为的控制和状态管理。
 * 注意：请勿删除或修改任何代码，仅在代码中增加详细中文注释。
 */

import type {
  // 导入 Drawer 相关的类型定义，用于描述 Drawer API 的配置、属性和扩展 API 类型
  DrawerApiOptions,
  DrawerProps,
  ExtendedDrawerApi,
} from './drawer';

import {
  // 从 Vue 框架中导入所需的 API，分别用于组件定义、虚拟节点创建、依赖注入、下一次 DOM 更新、响应式数据等功能
  defineComponent,
  h,
  inject,
  nextTick,
  provide,
  reactive,
  ref,
} from 'vue';

import { useStore } from '@/_core/shared/store'; // 导入全局状态管理 store 的钩子函数

import { DrawerApi } from './drawer-api'; // 导入 Drawer API 的实现，用于创建和操作 Drawer 的实例
import ZayumDrawer from './drawer.vue'; // 导入 ZayumDrawer 组件的 Vue 单文件组件

// 定义一个 Symbol 作为 Drawer API 在 provide/inject 中的唯一标识符
const USER_DRAWER_INJECT_KEY = Symbol('ZAYUM_DRAWER_INJECT');

// 定义默认的 Drawer 属性对象，初始为空，类型为部分 DrawerProps
const DEFAULT_DRAWER_PROPS: Partial<DrawerProps> = {};

/**
 * 设置默认 Drawer 属性
 * @param props - 部分 DrawerProps 对象，用于更新默认属性配置
 */
export function setDefaultDrawerProps(props: Partial<DrawerProps>) {
  // 将传入的 props 对象合并到默认属性对象中
  Object.assign(DEFAULT_DRAWER_PROPS, props);
}

/**
 * 创建并返回一个 Zayum Drawer 组件及其对应的扩展 API
 * @param options - Drawer API 配置选项，默认为空对象
 * @returns 一个包含 Drawer 组件和扩展 API 的只读元组
 */
export function useZayumDrawer<
  TParentDrawerProps extends DrawerProps = DrawerProps,
>(options: DrawerApiOptions = {}) {
  // 如果传入了 connectedComponent，则表示 Drawer 为外部调用，与内部组件进行连接，
  // 外部的 Drawer 通过 provide/inject 机制传递 API
  const { connectedComponent } = options;
  if (connectedComponent) {
    // 创建一个响应式对象用于存储扩展 API
    const extendedApi = reactive({});
    // 用于控制 Drawer 是否处于可渲染状态，初始为 true
    const isDrawerReady = ref(true);
    // 定义一个父级 Drawer 组件，该组件主要用于传递扩展 API 给子组件
    const Drawer = defineComponent(
      (props: TParentDrawerProps, { attrs, slots }) => {
        // 使用 provide 将扩展 API 的方法和配置信息传递给后代组件
        provide(USER_DRAWER_INJECT_KEY, {
          /**
           * 用于扩展 API：设置扩展 API 的原型为传入的 api 对象，
           * 保证响应性和原型函数不丢失
           */
          extendApi(api: ExtendedDrawerApi) {
            // 不能直接给 reactive 对象赋值，否则会丢失响应式；也不能用 Object.assign 会丢失原型函数
            Object.setPrototypeOf(extendedApi, api);
          },
          options, // 将当前 options 传递下去
          /**
           * 重新创建 Drawer 的方法，
           * 当调用此方法时，会将 isDrawerReady 设为 false，等待下一次 DOM 更新后恢复为 true
           */
          async reCreateDrawer() {
            isDrawerReady.value = false;
            await nextTick();
            isDrawerReady.value = true;
          },
        });
        // 检查 props、attrs 与 slots 中的属性是否与 store 状态中的属性重复，避免复杂度提升
        checkProps(extendedApi as ExtendedDrawerApi, {
          ...props,
          ...attrs,
          ...slots,
        });
        // 返回一个渲染函数，根据 isDrawerReady 状态渲染 connectedComponent 或占位 div
        return () =>
          h(
            isDrawerReady.value ? connectedComponent : 'div',
            { ...props, ...attrs },
            slots,
          );
      },
      {
        inheritAttrs: false, // 禁止自动继承外部传入的 attributes
        name: 'ZayumParentDrawer', // 组件名称，便于调试和错误提示
      },
    );
    // 返回包含 Drawer 组件和扩展 API 的元组，类型为只读元组
    return [Drawer, extendedApi as ExtendedDrawerApi] as const;
  }

  // 如果没有 connectedComponent，则通过 inject 获取上层组件传递的相关数据，默认为空对象
  const injectData = inject<any>(USER_DRAWER_INJECT_KEY, {});

  // 合并默认属性、注入数据中的 options 以及传入的 options，生成最终的 Drawer API 配置项
  const mergedOptions = {
    ...DEFAULT_DRAWER_PROPS,
    ...injectData.options,
    ...options,
  } as DrawerApiOptions;

  // 重写 mergedOptions 的 onOpenChange 回调，确保同时调用传入 options 和注入 options 中的回调
  mergedOptions.onOpenChange = (isOpen: boolean) => {
    options.onOpenChange?.(isOpen);
    injectData.options?.onOpenChange?.(isOpen);
  };

  // 处理 Drawer 关闭后的回调逻辑
  const onClosed = mergedOptions.onClosed;
  mergedOptions.onClosed = () => {
    // 调用原有的 onClosed 回调
    onClosed?.();
    // 如果配置了 destroyOnClose，则在 Drawer 关闭后调用 reCreateDrawer 重新创建 Drawer
    if (mergedOptions.destroyOnClose) {
      injectData.reCreateDrawer?.();
    }
  };
  // 使用合并后的配置项创建 DrawerApi 实例，用于管理 Drawer 的行为和状态
  const api = new DrawerApi(mergedOptions);

  // 将 DrawerApi 实例断言为 ExtendedDrawerApi 类型
  const extendedApi: ExtendedDrawerApi = api as never;

  // 为扩展 API 增加 useStore 方法，方便在组件中使用全局状态管理
  extendedApi.useStore = (selector) => {
    return useStore(api.store, selector);
  };

  // 定义最终的 Drawer 组件，该组件包装了 ZayumDrawer 组件，并将扩展 API 作为 props 传递进去
  const Drawer = defineComponent(
    (props: DrawerProps, { attrs, slots }) => {
      return () =>
        h(ZayumDrawer, { ...props, ...attrs, drawerApi: extendedApi }, slots);
    },
    {
      inheritAttrs: false, // 禁止自动继承外部传入的 attributes
      name: 'ZayumDrawer', // 组件名称，便于调试和错误提示
    },
  );
  // 如果注入数据中存在 extendApi 方法，则调用该方法，将扩展 API 传递出去
  injectData.extendApi?.(extendedApi);
  // 返回包含 Drawer 组件和扩展 API 的元组，类型为只读元组
  return [Drawer, extendedApi] as const;
}

/**
 * 检查传入的属性是否与 Drawer 的 store 状态中的属性重名，
 * 如果存在重名且不属于特殊属性（如 'class'），则在控制台发出警告，
 * 以防止在 connectedComponent 存在时设置不必要的 props 或 slots 增加复杂度。
 *
 * @param api - 扩展 Drawer API，用于访问 store 状态
 * @param attrs - 需要检查的属性集合，可能来自 props、attrs 或 slots
 */
async function checkProps(api: ExtendedDrawerApi, attrs: Record<string, any>) {
  // 如果 attrs 为空，则无需进行检查
  if (!attrs || Object.keys(attrs).length === 0) {
    return;
  }
  // 等待下一次 DOM 更新，确保状态已经更新
  await nextTick();

  const state = api?.store?.state;

  // 如果 store 状态不存在，则退出检查
  if (!state) {
    return;
  }

  // 将 store 状态的所有属性名存入 Set 集合中，便于快速查找
  const stateKeys = new Set(Object.keys(state));

  // 遍历 attrs 中的所有属性
  for (const attr of Object.keys(attrs)) {
    // 如果属性名存在于 store 状态中，并且该属性不为 'class'
    if (stateKeys.has(attr) && !['class'].includes(attr)) {
      // 发出警告提示：当 connectedComponent 存在时，不应直接设置 Drawer 的 props 或 slots，
      // 否则可能会导致组件内部逻辑复杂度增加。
      console.warn(
        `[Zayum Drawer]: When 'connectedComponent' exists, do not set props or slots '${attr}', which will increase complexity. If you need to modify the props of Drawer, please use useZayumDrawer or api.`,
      );
    }
  }
}
