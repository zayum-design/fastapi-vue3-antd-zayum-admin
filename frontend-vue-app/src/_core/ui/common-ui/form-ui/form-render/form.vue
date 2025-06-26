<script setup lang="ts">
// 引入所需的类型定义
import type { GenericObject } from 'vee-validate';
import type { ZodTypeAny } from 'zod';

import type {
  FormCommonConfig,
  FormRenderProps,
  FormSchema,
  FormShape,
} from '../types';

// 引入 Vue 的计算属性
import { computed } from 'vue';

// 引入 UI 组件和工具函数
import { Form } from '@/_core/ui/common-ui/shadcn-ui';
import { cn, isString, mergeWithArrayOverride } from '@/_core/shared/utils';

// 引入表单上下文提供者和展开功能钩子
import { provideFormRenderProps } from './context';
import { useExpandable } from './expandable';
import FormField from './form-field.vue';
import { getBaseRules, getDefaultValueInZodStack } from './helper';

// 定义 Props 类型，继承自 FormRenderProps
interface Props extends FormRenderProps {}

// 使用默认值定义组件的 props
const props = withDefaults(
  defineProps<Props & { globalCommonConfig?: FormCommonConfig }>(),
  {
    collapsedRows: 1,
    commonConfig: () => ({}),
    globalCommonConfig: () => ({}),
    showCollapseButton: false,
    wrapperClass: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3',
  },
);

// 定义组件发射的事件
const emits = defineEmits<{
  submit: [event: any];
}>();

// 提供表单渲染相关的 props
provideFormRenderProps(props);

// 使用展开功能钩子获取状态和引用
const { isCalculated, keepFormItemIndex, wrapperRef } = useExpandable(props);

// 计算表单形状
const shapes = computed(() => {
  const resultShapes: FormShape[] = [];
  props.schema?.forEach((schema) => {
    const { fieldName } = schema;
    const rules = schema.rules as ZodTypeAny;

    let typeName = '';
    if (rules && !isString(rules)) {
      typeName = rules._def.typeName;
    }

    const baseRules = getBaseRules(rules) as ZodTypeAny;

    resultShapes.push({
      default: getDefaultValueInZodStack(rules),
      fieldName,
      required: !['ZodNullable', 'ZodOptional'].includes(typeName),
      rules: baseRules,
    });
  });
  return resultShapes;
});

// 计算表单组件
const formComponent = computed(() => (props.form ? 'form' : Form));

// 计算表单组件的属性
const formComponentProps = computed(() => {
  return props.form
    ? {
        onSubmit: props.form.handleSubmit((val) => emits('submit', val)),
      }
    : {
        onSubmit: (val: GenericObject) => emits('submit', val),
      };
});

// 计算表单是否折叠
const formCollapsed = computed(() => {
  return props.collapsed && isCalculated.value;
});

// 计算表单模式
const computedSchema = computed(
  (): (Omit<FormSchema, 'formFieldProps'> & {
    commonComponentProps: Record<string, any>;
    formFieldProps: Record<string, any>;
  })[] => {
    const {
      colon = false,
      componentProps = {},
      controlClass = '',
      disabled,
      disabledOnChangeListener = true,
      disabledOnInputListener = true,
      emptyStateValue = undefined,
      formFieldProps = {},
      formItemClass = '',
      hideLabel = false,
      hideRequiredMark = false,
      labelClass = '',
      labelWidth = 100,
      modelPropName = '',
      wrapperClass = '',
    } = mergeWithArrayOverride(props.commonConfig, props.globalCommonConfig);
    return (props.schema || []).map((schema, index) => {
      const keepIndex = keepFormItemIndex.value;

      const hidden =
        props.showCollapseButton && !!formCollapsed.value && keepIndex
          ? keepIndex <= index
          : false;

      return {
        colon,
        disabled,
        disabledOnChangeListener,
        disabledOnInputListener,
        emptyStateValue,
        hideLabel,
        hideRequiredMark,
        labelWidth,
        modelPropName,
        wrapperClass,
        ...schema,
        commonComponentProps: componentProps,
        componentProps: schema.componentProps,
        controlClass: cn(controlClass, schema.controlClass),
        formFieldProps: {
          ...formFieldProps,
          ...schema.formFieldProps,
        },
        formItemClass: cn(
          'flex-shrink-0',
          { hidden },
          formItemClass,
          schema.formItemClass,
        ),
        labelClass: cn(labelClass, schema.labelClass),
      };
    });
  },
);
</script>

<template>
  <component :is="formComponent" v-bind="formComponentProps">
    <div ref="wrapperRef" :class="wrapperClass" class="grid">
      <template v-for="cSchema in computedSchema" :key="cSchema.fieldName">
        <FormField
          v-bind="cSchema"
          :class="cSchema.formItemClass"
          :rules="cSchema.rules"
        >
          <template #default="slotProps">
            <slot v-bind="slotProps" :name="cSchema.fieldName"> </slot>
          </template>
        </FormField>
      </template>
      <slot :shapes="shapes"></slot>
    </div>
  </component>
</template>
