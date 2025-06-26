import type {
  FormItemDependencies,
  FormSchemaRuleType,
  MaybeComponentProps,
} from '../types';

import { computed, ref, watch } from 'vue';

import { isBoolean, isFunction } from '@/_core/shared/utils';

import { useFormValues } from 'vee-validate';

import { injectRenderFormProps } from './context';

/**
 * 处理表单项的依赖关系
 * @param getDependencies 获取依赖配置的函数
 * @returns 计算后的动态属性
 */
export default function useDependencies(
  getDependencies: () => FormItemDependencies | undefined,
) {
  // 获取表单值
  const values = useFormValues();

  // 获取表单渲染的上下文
  const formRenderProps = injectRenderFormProps();

  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const formApi = formRenderProps.form!;

  if (!values) {
    throw new Error('useDependencies 只能在 <ZayumForm> 组件内部使用');
  }

  // 是否渲染组件
  const isIf = ref(true);
  // 是否禁用组件
  const isDisabled = ref(false);
  // 是否显示组件
  const isShow = ref(true);
  // 是否必填
  const isRequired = ref(false);
  // 组件的动态属性
  const dynamicComponentProps = ref<MaybeComponentProps>({});
  // 组件的动态校验规则
  const dynamicRules = ref<FormSchemaRuleType>();

  // 计算触发字段的值
  const triggerFieldValues = computed(() => {
    const triggerFields = getDependencies()?.triggerFields ?? [];
    return triggerFields.map((dep) => values.value[dep]);
  });

  // 重置依赖状态
  const resetConditionState = () => {
    isDisabled.value = false;
    isIf.value = true;
    isShow.value = true;
    isRequired.value = false;
    dynamicRules.value = undefined;
    dynamicComponentProps.value = {};
  };

  // 监听触发字段的变化
  watch(
    [triggerFieldValues, getDependencies],
    async ([_values, dependencies]) => {
      if (!dependencies || !dependencies?.triggerFields?.length) {
        return;
      }
      resetConditionState();
      const {
        componentProps,
        disabled,
        if: whenIf,
        required,
        rules,
        show,
        trigger,
      } = dependencies;

      // 1. 先判断 if，如果为 false，则不渲染组件
      const formValues = values.value;

      if (isFunction(whenIf)) {
        isIf.value = !!(await whenIf(formValues, formApi));
        if (!isIf.value) return;
      } else if (isBoolean(whenIf)) {
        isIf.value = whenIf;
        if (!isIf.value) return;
      }

      // 2. 再判断 show，如果为 false，则隐藏组件
      if (isFunction(show)) {
        isShow.value = !!(await show(formValues, formApi));
        if (!isShow.value) return;
      } else if (isBoolean(show)) {
        isShow.value = show;
        if (!isShow.value) return;
      }

      // 3. 计算动态组件属性
      if (isFunction(componentProps)) {
        dynamicComponentProps.value = await componentProps(formValues, formApi);
      }

      // 4. 计算动态校验规则
      if (isFunction(rules)) {
        dynamicRules.value = await rules(formValues, formApi);
      }

      // 5. 计算是否禁用
      if (isFunction(disabled)) {
        isDisabled.value = !!(await disabled(formValues, formApi));
      } else if (isBoolean(disabled)) {
        isDisabled.value = disabled;
      }

      // 6. 计算是否必填
      if (isFunction(required)) {
        isRequired.value = !!(await required(formValues, formApi));
      }

      // 7. 触发其他逻辑
      if (isFunction(trigger)) {
        await trigger(formValues, formApi);
      }
    },
    { deep: true, immediate: true },
  );

  return {
    dynamicComponentProps,
    dynamicRules,
    isDisabled,
    isIf,
    isRequired,
    isShow,
  };
}
