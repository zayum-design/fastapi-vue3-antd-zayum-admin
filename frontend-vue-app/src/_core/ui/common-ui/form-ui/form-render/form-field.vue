<script setup lang="ts">
/* =========================
   导入相关依赖及类型定义
========================= */
// 引入 zod 的类型，用于校验规则定义
import type { ZodType } from 'zod';

// 导入自定义表单相关的类型定义
import type { FormSchema, MaybeComponentProps } from '../types';

// 导入 Vue 中常用的 API，如计算属性、下一刻执行、模板引用和侦听器
import { computed, nextTick, useTemplateRef, watch } from 'vue';

// 导入 shadcn-ui 中常用的表单组件
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormMessage,
  ZayumRenderContent,
} from '@/_core/ui/common-ui/shadcn-ui';

// 导入工具函数，包括类名合并、判断是否为函数、对象、字符串等
import { cn, isFunction, isObject, isString } from '@/_core/shared/utils';
// 将 vee-validate 与 zod 结合，转换为带类型的校验规则
import { toTypedSchema } from '@vee-validate/zod';

// 从 vee-validate 中引入获取字段错误信息和表单所有值的 Hook
import { useFieldError, useFormValues } from 'vee-validate';

// 导入表单上下文以及依赖注入相关的方法
import { injectRenderFormProps, useFormContext } from './context';
// 引入依赖处理的 Hook
import useDependencies from './dependencies';
// 导入自定义表单标签组件
import FormLabel from './form-label.vue';
// 导入辅助函数，用于判断传入对象是否类似事件对象（例如 antd 组件的事件对象）
import { isEventObjectLike } from './helper';

/* =========================
   定义组件 Props 类型
========================= */
// 定义 Props 接口，继承自 FormSchema，表示表单组件的属性
interface Props extends FormSchema {}

// 使用 defineProps 定义组件接收的属性，同时要求传入 commonComponentProps 属性
const {
  colon,
  commonComponentProps,
  component,
  componentProps,
  dependencies,
  description,
  disabled,
  disabledOnChangeListener,
  disabledOnInputListener,
  emptyStateValue,
  fieldName,
  formFieldProps,
  label,
  labelClass,
  labelWidth,
  modelPropName,
  renderComponentContent,
  rules,
} = defineProps<
  Props & {
    commonComponentProps: MaybeComponentProps;
  }
>();

/* =========================
   获取表单上下文及相关引用
========================= */
// 从表单上下文中获取组件事件绑定映射、组件映射以及布局方向（垂直/水平）
const { componentBindEventMap, componentMap, isVertical } = useFormContext();
// 通过依赖注入获取表单渲染的属性（例如 form API、紧凑模式设置等）
const formRenderProps = injectRenderFormProps();
// 获取整个表单的值
const values = useFormValues();
// 获取当前字段的错误信息
const errors = useFieldError(fieldName);
// 创建模板引用，用于引用实际渲染的输入组件
const fieldComponentRef = useTemplateRef<HTMLInputElement>('fieldComponentRef');
// 获取表单的 API，通常包含一些操作方法
const formApi = formRenderProps.form;
// 判断是否处于紧凑模式（compact）
const compact = formRenderProps.compact;
// 计算当前字段是否无效（即存在错误信息）
const isInValid = computed(() => errors.value?.length > 0);

/* =========================
   计算实际使用的表单组件
========================= */
// 根据传入的 component 属性判断使用哪个组件：如果是字符串，则从组件映射中查找；否则直接使用传入组件
const FieldComponent = computed(() => {
  const finalComponent = isString(component)
    ? componentMap.value[component]
    : component;
  if (!finalComponent) {
    // 组件未注册，打印警告信息
    console.warn(`Component ${component} is not registered`);
  }
  return finalComponent;
});

/* =========================
   动态依赖配置处理
========================= */
// 使用自定义 Hook 根据 dependencies 返回动态组件属性、动态校验规则、禁用状态、必填状态和显示状态
const {
  dynamicComponentProps,
  dynamicRules,
  isDisabled,
  isIf,
  isRequired,
  isShow,
} = useDependencies(() => dependencies);

/* =========================
   标签样式及校验规则计算
========================= */
// 计算标签样式：如果 labelClass 中包含特定宽度或者布局为垂直，则不设置宽度，否则根据 labelWidth 设置宽度
const labelStyle = computed(() => {
  return labelClass?.includes('w-') || isVertical.value
    ? {}
    : {
        width: `${labelWidth}px`,
      };
});

// 计算当前使用的校验规则：优先使用动态规则，否则使用 props 中的规则
const currentRules = computed(() => {
  return dynamicRules.value || rules;
});

// 计算当前组件的可见性：只有在 isIf 与 isShow 都为 true 时，组件才会显示
const visible = computed(() => {
  return isIf.value && isShow.value;
});

// 判断当前字段是否必填
const shouldRequired = computed(() => {
  // 若字段不可见，则不必填
  if (!visible.value) {
    return false;
  }

  // 如果没有设置规则，则直接依据 isRequired 判断
  if (!currentRules.value) {
    return isRequired.value;
  }

  // 如果外部标记为必填，则直接返回 true
  if (isRequired.value) {
    return true;
  }

  // 如果规则为字符串，则判断是否包含 'required' 或 'selectRequired'
  if (isString(currentRules.value)) {
    return ['required', 'selectRequired'].includes(currentRules.value);
  }

  // 通过规则的 isOptional 方法判断是否可选
  let isOptional = currentRules?.value?.isOptional?.();

  // 如果规则包含默认值，则需要特殊处理，默认值包装类型不一定必填
  const typeName = currentRules?.value?._def?.typeName;
  if (typeName === 'ZodDefault') {
    const innerType = currentRules?.value?._def.innerType;
    if (innerType) {
      isOptional = innerType.isOptional?.();
    }
  }

  return !isOptional;
});

// 计算最终传递给表单字段的校验规则
const fieldRules = computed(() => {
  // 如果字段不可见，则不需要校验规则
  if (!visible.value) {
    return null;
  }

  let rules = currentRules.value;
  // 如果没有规则，则根据是否必填返回 'required' 或 null
  if (!rules) {
    return isRequired.value ? 'required' : null;
  }

  // 如果规则为字符串，直接返回字符串规则
  if (isString(rules)) {
    return rules;
  }

  // 根据必填状态判断是否为可选
  const isOptional = !shouldRequired.value;
  if (!isOptional) {
    // 尝试解包规则，获取内部实际规则
    const unwrappedRules = (rules as any)?.unwrap?.();
    if (unwrappedRules) {
      rules = unwrappedRules;
    }
  }
  // 转换为带类型的 zod 校验规则
  return toTypedSchema(rules as ZodType);
});

/* =========================
   计算最终传递给组件的 Props
========================= */
// 根据传入的 componentProps（可能为函数）及动态组件属性，合并生成最终的组件属性
const computedProps = computed(() => {
  const finalComponentProps = isFunction(componentProps)
    ? componentProps(values.value, formApi!)
    : componentProps;

  return {
    ...commonComponentProps,
    ...finalComponentProps,
    ...dynamicComponentProps.value,
  };
});

/* =========================
   监听自动聚焦属性变化
========================= */
// 监控 computedProps 中的 autofocus 属性，一旦为 true，则在下一刻触发聚焦操作
watch(
  () => computedProps.value?.autofocus,
  (value) => {
    if (value === true) {
      nextTick(() => {
        autofocus();
      });
    }
  },
  { immediate: true },
);

/* =========================
   计算字段禁用状态
========================= */
// 结合依赖状态、传入的 disabled 属性以及 computedProps 的禁用状态，最终决定是否禁用
const shouldDisabled = computed(() => {
  return isDisabled.value || disabled || computedProps.value?.disabled;
});

/* =========================
   自定义内容渲染逻辑
========================= */
// 如果 renderComponentContent 为函数，则调用它并传入当前表单值和表单 API，返回自定义插槽内容
const customContentRender = computed(() => {
  if (!isFunction(renderComponentContent)) {
    return {};
  }
  return renderComponentContent(values.value, formApi!);
});

// 获取自定义渲染内容的键名集合，用于在模板中动态生成插槽
const renderContentKey = computed(() => {
  return Object.keys(customContentRender.value);
});

/* =========================
   计算传递给 FormField 的属性
========================= */
// 组合 label、校验规则及其它传递的表单字段属性，生成最终传递给 FormField 的 props
const fieldProps = computed(() => {
  const rules = fieldRules.value;
  return {
    keepValue: true, // 保持字段值（防止在某些操作中丢失）
    label,
    ...(rules ? { rules } : {}),
    ...(formFieldProps as Record<string, any>),
  };
});

/* =========================
   事件绑定及属性合并处理
========================= */
/**
 * 绑定字段组件的事件
 * @param slotProps 插槽传入的属性对象
 * @returns 返回包含事件绑定的对象
 */
function fieldBindEvent(slotProps: Record<string, any>) {
  // 从 slotProps 中获取组件的 modelValue 及更新事件处理器
  const modelValue = slotProps.componentField.modelValue;
  const handler = slotProps.componentField['onUpdate:modelValue'];

  // 根据传入的 modelPropName 或组件名称，从映射中获取对应的事件字段名称
  const bindEventField =
    modelPropName ||
    (isString(component) ? componentBindEventMap.value?.[component] : null);

  let value = modelValue;
  // 处理某些 antd 组件可能传递事件对象的情况，提取实际值
  if (modelValue && isObject(modelValue) && bindEventField) {
    value = isEventObjectLike(modelValue)
      ? modelValue?.target?.[bindEventField]
      : (modelValue?.[bindEventField] ?? modelValue);
  }

  if (bindEventField) {
    return {
      // 绑定更新事件，事件名称动态生成
      [`onUpdate:${bindEventField}`]: handler,
      // 绑定对应的值，如果未定义则使用 emptyStateValue
      [bindEventField]: value === undefined ? emptyStateValue : value,
      // 绑定 onChange 事件，根据 disabledOnChangeListener 判断是否禁用
      onChange: disabledOnChangeListener
        ? undefined
        : (e: Record<string, any>) => {
            const shouldUnwrap = isEventObjectLike(e);
            const onChange = slotProps?.componentField?.onChange;
            if (!shouldUnwrap) {
              return onChange?.(e);
            }
            return onChange?.(e?.target?.[bindEventField] ?? e);
          },
      // 如果禁用 onInput，则不绑定 onInput 事件
      ...(disabledOnInputListener ? { onInput: undefined } : {}),
    };
  }
  // 若没有需要绑定的字段，则只返回根据 disabledOnInputListener 与 disabledOnChangeListener 决定的空事件绑定
  return {
    ...(disabledOnInputListener ? { onInput: undefined } : {}),
    ...(disabledOnChangeListener ? { onChange: undefined } : {}),
  };
}

/**
 * 创建最终传递给表单组件的 Props，将 slotProps、计算属性及事件绑定合并
 * @param slotProps 插槽传入的属性对象
 * @returns 合并后的属性对象
 */
function createComponentProps(slotProps: Record<string, any>) {
  const bindEvents = fieldBindEvent(slotProps);

  const binds = {
    ...slotProps.componentField,
    ...computedProps.value,
    ...bindEvents,
    // 如果 computedProps 中包含 onChange/onInput，则确保其被传入
    ...(Reflect.has(computedProps.value, 'onChange')
      ? { onChange: computedProps.value.onChange }
      : {}),
    ...(Reflect.has(computedProps.value, 'onInput')
      ? { onInput: computedProps.value.onInput }
      : {}),
  };

  return binds;
}

/* =========================
   聚焦处理函数
========================= */
/**
 * 执行聚焦操作，聚焦到实际输入组件上（若尚未获得焦点）
 */
function autofocus() {
  if (
    fieldComponentRef.value &&
    isFunction(fieldComponentRef.value.focus) &&
    // 检查当前是否已有其他元素获得焦点，避免重复聚焦
    document.activeElement !== fieldComponentRef.value
  ) {
    fieldComponentRef.value?.focus?.();
  }
}
</script>

<template>
  <!-- 使用 FormField 包装整个表单字段，当 isIf 为 true 时才进行渲染 -->
  <FormField
    v-if="isIf"
    v-bind="fieldProps"
    v-slot="slotProps"
    :name="fieldName"
  >
    <!-- FormItem 用于整体的表单项布局，根据 isShow 控制显示 -->
    <FormItem
      v-show="isShow"
      :class="{
        'form-valid-error': isInValid,          // 当存在错误时，添加错误样式
        'flex-col': isVertical,                 // 垂直布局
        'flex-row items-center': !isVertical,    // 水平布局
        'pb-6': !compact,                       // 非紧凑模式时底部内边距较大
        'pb-2': compact,                        // 紧凑模式时底部内边距较小
      }"
      class="flex"
      v-bind="$attrs"
    >
      <!-- FormLabel 渲染表单标签，当 hideLabel 为 false 时显示 -->
      <FormLabel
        v-if="!hideLabel"
        :class="
          cn(
            'flex leading-6',
            {
              'mr-2 flex-shrink-0 justify-end': !isVertical, // 水平布局时标签右侧对齐
              'mb-1 flex-row': isVertical,                    // 垂直布局时标签下方有间距
            },
            labelClass,
          )
        "
        :help="help"  <!-- 帮助提示信息 -->
        :required="shouldRequired && !hideRequiredMark" <!-- 根据必填状态决定是否显示必填标记 -->
        :style="labelStyle"  <!-- 应用计算后的标签样式 -->
      >
        <template v-if="label">
          <span>{{ label }}</span>
          <!-- 如果 colon 为 true，则在标签后添加冒号 -->
          <span v-if="colon" class="ml-[2px]">:</span>
        </template>
      </FormLabel>
      <!-- 输入组件及其他内容的容器 -->
      <div :class="cn('relative flex w-full items-center', wrapperClass)">
        <!-- FormControl 包裹实际输入组件 -->
        <FormControl :class="cn(controlClass)">
          <!-- 使用插槽传递所有字段和计算后的组件属性 -->
          <slot
            v-bind="{
              ...slotProps,
              ...createComponentProps(slotProps),
              disabled: shouldDisabled,
              isInValid,
            }"
          >
            <!-- 根据 FieldComponent 渲染实际输入组件 -->
            <component
              :is="FieldComponent"
              ref="fieldComponentRef"
              :class="{
                // 当字段无效时，添加边框和阴影样式
                'border-destructive focus:border-destructive hover:border-destructive/80 focus:shadow-[0_0_0_2px_rgba(255,38,5,0.06)]': isInValid,
              }"
              v-bind="createComponentProps(slotProps)"
              :disabled="shouldDisabled"
            >
              <!-- 遍历自定义渲染内容的键名，根据键名动态生成具名插槽 -->
              <template
                v-for="name in renderContentKey"
                :key="name"
                #[name]="renderSlotProps"
              >
                <ZayumRenderContent
                  :content="customContentRender[name]"
                  v-bind="{ ...renderSlotProps, $formContext: slotProps }"
                />
              </template>
              <!-- 备用插槽，可用于扩展额外内容 -->
              <!-- <slot></slot> -->
            </component>
          </slot>
        </FormControl>
        <!-- 自定义后缀渲染区域 -->
        <div v-if="suffix" class="ml-1">
          <ZayumRenderContent :content="suffix" />
        </div>

        <!-- 显示描述信息 -->
        <FormDescription v-if="description">
          <ZayumRenderContent :content="description" />
        </FormDescription>

        <!-- 使用过渡动画显示错误信息 -->
        <Transition name="slide-up">
          <FormMessage class="absolute -bottom-[22px]" />
        </Transition>
      </div>
    </FormItem>
  </FormField>
</template>
