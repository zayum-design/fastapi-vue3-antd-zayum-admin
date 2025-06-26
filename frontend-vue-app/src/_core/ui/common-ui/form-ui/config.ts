// 引入Vue中的Component类型
import type { Component } from 'vue';

// 引入表单相关的类型定义
import type {
  BaseFormComponentType,
  FormCommonConfig,
  ZayumFormAdapterOptions,
} from './types';

// 引入Vue的h函数，用于创建VNode
import { h } from 'vue';

// 引入自定义UI组件
import {
  ZayumButton,
  ZayumCheckbox,
  Input as ZayumInput,
  ZayumInputPassword,
  ZayumPinInput,
  ZayumSelect,
} from '@/_core/ui/common-ui/shadcn-ui';

// 引入全局共享状态
import { globalShareState } from '@/_core/shared/global-state';

// 引入vee-validate的defineRule函数，用于定义验证规则
import { defineRule } from 'vee-validate';

// 默认的模型属性名称
const DEFAULT_MODEL_PROP_NAME = 'modelValue';

// 默认表单的通用配置
export const DEFAULT_FORM_COMMON_CONFIG: FormCommonConfig = {};

// 组件映射表，将基础表单组件类型映射到具体的Vue组件
export const COMPONENT_MAP: Record<BaseFormComponentType, Component> = {
  DefaultButton: h(ZayumButton, { size: 'sm', variant: 'outline' }),
  PrimaryButton: h(ZayumButton, { size: 'sm', variant: 'default' }),
  ZayumCheckbox,
  ZayumInput,
  ZayumInputPassword,
  ZayumPinInput,
  ZayumSelect,
};

// 组件绑定事件的映射表
export const COMPONENT_BIND_EVENT_MAP: Partial<
  Record<BaseFormComponentType, string>
> = {
  ZayumCheckbox: 'checked',
};

// 设置Zayum表单的函数
export function setupZayumForm<
  T extends BaseFormComponentType = BaseFormComponentType,
>(options: ZayumFormAdapterOptions<T>) {
  // 从参数中解构配置项和定义规则
  const { config, defineRules } = options;

  // 从配置中解构相关属性，默认值处理
  const {
    disabledOnChangeListener = true,
    disabledOnInputListener = true,
    emptyStateValue = undefined,
  } = (config || {}) as FormCommonConfig;

  // 将配置项赋值到默认配置
  Object.assign(DEFAULT_FORM_COMMON_CONFIG, {
    disabledOnChangeListener,
    disabledOnInputListener,
    emptyStateValue,
  });

  // 如果有定义验证规则，则进行定义
  if (defineRules) {
    for (const key of Object.keys(defineRules)) {
      defineRule(key, defineRules[key as never]);
    }
  }

  // 处理模型属性名称的默认值和映射
  const baseModelPropName =
    config?.baseModelPropName ?? DEFAULT_MODEL_PROP_NAME;
  const modelPropNameMap = config?.modelPropNameMap as
    | Record<BaseFormComponentType, string>
    | undefined;

  // 获取全局共享的组件
  const components = globalShareState.getComponents();

  // 遍历并更新组件映射表
  for (const component of Object.keys(components)) {
    const key = component as BaseFormComponentType;
    COMPONENT_MAP[key] = components[component as never];

    // 如果基本模型属性名不是默认值，则更新绑定事件映射表
    if (baseModelPropName !== DEFAULT_MODEL_PROP_NAME) {
      COMPONENT_BIND_EVENT_MAP[key] = baseModelPropName;
    }

    // 覆盖特殊组件的modelPropName
    if (modelPropNameMap && modelPropNameMap[key]) {
      COMPONENT_BIND_EVENT_MAP[key] = modelPropNameMap[key];
    }
  }
}
