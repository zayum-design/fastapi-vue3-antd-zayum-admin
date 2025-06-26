// 导入类型定义：ExtendedModalApi、ModalApiOptions、ModalProps，这些类型用于描述 Modal API 的扩展、配置选项和组件属性
import type { ExtendedModalApi, ModalApiOptions, ModalProps } from './modal';

// 从 Vue 框架中导入常用 API，包括组件定义、虚拟 DOM 创建、依赖注入、响应式数据、下一个渲染周期等
import {
  defineComponent,
  h,
  inject,
  nextTick,
  provide,
  reactive,
  ref,
} from 'vue';

// 导入全局状态管理的钩子，用于在 Modal 内部获取和操作共享状态
import { useStore } from '@/_core/shared/store';

// 导入 ModalApi 类，该类封装了 Modal 的各种行为和逻辑
import { ModalApi } from './modal-api';

// 导入实际用于渲染 Modal 的 Vue 组件
import ZayumModal from './modal.vue';

// 定义用于 provide/inject 的唯一标识符，确保组件间通信时注入的数据的唯一性
const USER_MODAL_INJECT_KEY = Symbol('ZAYUM_MODAL_INJECT');

// 定义默认的 Modal 属性，使用 Partial 表示这些属性为可选项，初始为空对象
const DEFAULT_MODAL_PROPS: Partial<ModalProps> = {};

// 导出一个设置默认 Modal 属性的方法，通过合并传入的 props 更新默认值
export function setDefaultModalProps(props: Partial<ModalProps>) {
  Object.assign(DEFAULT_MODAL_PROPS, props);
}

// 定义并导出 useZayumModal 函数，创建和返回一个 Modal 组件及其扩展 API
// TParentModalProps 泛型用于定义传入的父级 Modal 属性类型，默认为 ModalProps 类型
export function useZayumModal<TParentModalProps extends ModalProps = ModalProps>(
  options: ModalApiOptions = {},
) {
  // 如果传入的 options 中包含 connectedComponent，说明当前 Modal 为外部调用
  // 外部 Modal 需要通过 provide/inject 与内部组件连接，并传递 API
  const { connectedComponent } = options;
  if (connectedComponent) {
    // 创建一个响应式对象用于存储扩展的 API，后续会通过 extendApi 方法注入实际的 API 方法
    const extendedApi = reactive({});
    // 定义一个响应式标志，用于控制 Modal 是否准备好渲染
    const isModalReady = ref(true);
    // 定义一个 Vue 组件，该组件作为外部 Modal 的包装组件
    const Modal = defineComponent(
      // 组件的 setup 函数，接收 props、attrs 和 slots
      (props: TParentModalProps, { attrs, slots }) => {
        // 通过 provide 将 Modal 相关的 API 和选项传递给子组件
        provide(USER_MODAL_INJECT_KEY, {
          // extendApi 方法用于将传入的 api 扩展到 extendedApi 上
          // 注意：不能直接赋值或使用 Object.assign，否则可能会丢失响应式能力或原型方法
          extendApi(api: ExtendedModalApi) {
            Object.setPrototypeOf(extendedApi, api);
          },
          // 将当前的 options 传递下去
          options,
          // reCreateModal 方法用于重新创建 Modal，主要用于在销毁后重新渲染 Modal
          async reCreateModal() {
            // 首先将 isModalReady 设为 false，触发卸载
            isModalReady.value = false;
            // 等待下一个 DOM 更新周期
            await nextTick();
            // 再将 isModalReady 设为 true，重新渲染 Modal
            isModalReady.value = true;
          },
        });
        // 调用 checkProps 辅助函数，检查传入的 props、attrs 和 slots 是否存在与 Modal 内部状态冲突的属性
        checkProps(extendedApi as ExtendedModalApi, {
          ...props,
          ...attrs,
          ...slots,
        });
        // 返回渲染函数，根据 isModalReady 决定渲染 connectedComponent 还是一个空 div 占位符
        return () =>
          h(
            isModalReady.value ? connectedComponent : 'div',
            {
              ...props,
              ...attrs,
            },
            slots,
          );
      },
      {
        // 设置 inheritAttrs 为 false，防止非 prop 的属性自动应用到组件根元素上
        inheritAttrs: false,
        // 为组件指定名称，便于调试和开发工具识别
        name: 'ZayumParentModal',
      },
    );
    // 返回包含 Modal 组件和扩展 API 的元组，使用 const 断言确保类型不变
    return [Modal, extendedApi as ExtendedModalApi] as const;
  }

  // 如果没有传入 connectedComponent，则通过 inject 获取上层组件传递过来的 Modal 数据
  const injectData = inject<any>(USER_MODAL_INJECT_KEY, {});

  // 合并默认的 Modal 属性、注入数据中的 options 和函数传入的 options，生成最终的配置对象
  const mergedOptions = {
    ...DEFAULT_MODAL_PROPS,
    ...injectData.options,
    ...options,
  } as ModalApiOptions;

  // 重写 mergedOptions 的 onOpenChange 回调，确保在 Modal 打开状态改变时，
  // 同时调用传入 options 和注入 options 中定义的 onOpenChange 方法
  mergedOptions.onOpenChange = (isOpen: boolean) => {
    options.onOpenChange?.(isOpen);
    injectData.options?.onOpenChange?.(isOpen);
  };

  // 保存原始的 onClosed 回调函数
  const onClosed = mergedOptions.onClosed;

  // 重写 mergedOptions 的 onClosed 回调，
  // 当 Modal 关闭时先调用原始 onClosed 回调，再根据 destroyOnClose 标志判断是否重置 Modal
  mergedOptions.onClosed = () => {
    onClosed?.();
    if (mergedOptions.destroyOnClose) {
      // 如果 destroyOnClose 为 true，则调用注入数据中的 reCreateModal 方法，重新创建 Modal
      injectData.reCreateModal?.();
    }
  };

  // 创建 ModalApi 实例，用 mergedOptions 作为配置，管理 Modal 的行为和状态
  const api = new ModalApi(mergedOptions);

  // 将创建的 api 实例赋值给 extendedApi，并强制类型转换为 ExtendedModalApi
  const extendedApi: ExtendedModalApi = api as never;

  // 为 extendedApi 添加 useStore 方法，允许组件通过 selector 筛选和使用共享状态
  extendedApi.useStore = (selector) => {
    return useStore(api.store, selector);
  };

  // 定义一个 Vue 组件 Modal，用于渲染 ZayumModal 组件
  // 该组件在渲染时会将 extendedApi 传递给 ZayumModal，以便内部组件使用 Modal API
  const Modal = defineComponent(
    (props: ModalProps, { attrs, slots }) => {
      return () =>
        h(
          ZayumModal,
          {
            ...props,
            ...attrs,
            modalApi: extendedApi,
          },
          slots,
        );
    },
    {
      // 同样设置 inheritAttrs 为 false，避免自动绑定非 prop 属性
      inheritAttrs: false,
      // 指定组件名称，便于开发和调试
      name: 'ZayumModal',
    },
  );
  // 如果注入数据中包含 extendApi 方法，则调用该方法将 extendedApi 传递出去
  injectData.extendApi?.(extendedApi);
  // 返回包含 Modal 组件和扩展 API 的元组
  return [Modal, extendedApi] as const;
}

// 定义一个辅助函数 checkProps，用于检查传入的属性与 Modal 内部状态是否有冲突
// 主要用于在 connectedComponent 存在时，提醒开发者不要在 props、attrs 或 slots 中传入可能引起复杂性的属性
async function checkProps(api: ExtendedModalApi, attrs: Record<string, any>) {
  // 如果 attrs 为空或没有任何属性，则无需检查，直接返回
  if (!attrs || Object.keys(attrs).length === 0) {
    return;
  }
  // 等待下一个渲染周期，确保所有响应式数据已经更新
  await nextTick();

  // 获取 ModalApi 中存储的状态对象，如果不存在则返回
  const state = api?.store?.state;
  if (!state) {
    return;
  }

  // 将状态对象的所有键存入一个 Set 中，便于后续快速查找
  const stateKeys = new Set(Object.keys(state));

  // 遍历传入的属性对象的所有键
  for (const attr of Object.keys(attrs)) {
    // 如果当前属性键存在于 Modal 的状态中，并且该键不为 'class'
    if (stateKeys.has(attr) && !['class'].includes(attr)) {
      // 提示开发者在 connectedComponent 存在时，不要直接传入 Modal 的 props 或 slots，
      // 以避免造成不必要的复杂性；建议通过 useZayumModal 或 api 修改 Modal 的属性
      console.warn(
        `[Zayum Modal]: When 'connectedComponent' exists, do not set props or slots '${attr}', which will increase complexity. If you need to modify the props of Modal, please use useZayumModal or api.`,
      );
    }
  }
}
