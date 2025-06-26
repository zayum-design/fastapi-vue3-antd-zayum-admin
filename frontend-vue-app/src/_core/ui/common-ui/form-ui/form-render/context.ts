import type { FormRenderProps } from '../types';
import { computed } from 'vue';
import { createContext } from '@/_core/ui/common-ui/shadcn-ui';

// 创建表单渲染属性的上下文
export const [injectRenderFormProps, provideFormRenderProps] =
  createContext<FormRenderProps>('FormRenderProps');

/**
 * 使用表单上下文
 * 该函数用于获取表单渲染相关的配置，如组件映射、事件绑定映射等
 * @returns 表单上下文相关的计算属性
 */
export const useFormContext = () => {
  // 获取注入的表单渲染属性
  const formRenderProps = injectRenderFormProps();

  // 是否为垂直布局
  const isVertical = computed(() => formRenderProps.layout === 'vertical');

  // 组件映射
  const componentMap = computed(() => formRenderProps.componentMap);

  // 组件事件绑定映射
  const componentBindEventMap = computed(
    () => formRenderProps.componentBindEventMap,
  );

  return {
    componentBindEventMap,
    componentMap,
    isVertical,
  };
};
