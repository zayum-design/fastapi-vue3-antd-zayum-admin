<script setup lang="ts">
import { computed, toRaw, unref, watch } from 'vue';

import { useSimpleLocale } from '@/_core/composables';
import { ZayumExpandableArrow } from '@/_core/ui/common-ui/shadcn-ui';
import { cn, isFunction, triggerWindowResize } from '@/_core/shared/utils';

import { COMPONENT_MAP } from '../config';
import { injectFormProps } from '../use-form-context';

const { $t } = useSimpleLocale();

// 获取表单的属性和表单实例
const [rootProps, form] = injectFormProps();

// 定义一个折叠状态的模型
const collapsed = defineModel({ default: false });

// 计算重置按钮的配置
const resetButtonOptions = computed(() => {
  return {
    content: `${$t.value('reset')}`, // 按钮文本
    show: true, // 按钮是否显示
    ...unref(rootProps).resetButtonOptions, // 继承外部传入的配置
  };
});

// 计算提交按钮的配置
const submitButtonOptions = computed(() => {
  return {
    content: `${$t.value('submit')}`, // 按钮文本
    show: true, // 按钮是否显示
    ...unref(rootProps).submitButtonOptions, // 继承外部传入的配置
  };
});

// const isQueryForm = computed(() => {
//   return !!unref(rootProps).showCollapseButton;
// });

// 计算查询表单的样式
const queryFormStyle = computed(() => {
  if (!unref(rootProps).actionWrapperClass) {
    return {
      'grid-column': `-2 / -1`, // 设置列位置
      marginLeft: 'auto', // 设置自动左边距
    };
  }

  return {};
});

// 提交事件处理
async function handleSubmit(e: Event) {
  e?.preventDefault(); // 阻止默认事件
  e?.stopPropagation(); // 阻止事件冒泡
  const { valid } = await form.validate(); // 校验表单
  if (!valid) {
    return; // 如果表单无效，直接返回
  }

  const values = toRaw(await unref(rootProps).formApi?.getValues()); // 获取表单值
  await unref(rootProps).handleSubmit?.(values); // 调用外部传入的提交处理函数
}

// 重置事件处理
async function handleReset(e: Event) {
  e?.preventDefault(); // 阻止默认事件
  e?.stopPropagation(); // 阻止事件冒泡
  const props = unref(rootProps);

  const values = toRaw(props.formApi?.getValues()); // 获取表单值

  if (isFunction(props.handleReset)) {
    await props.handleReset?.(values); // 调用外部传入的重置处理函数
  } else {
    form.resetForm(); // 重置表单
  }
}

// 监听折叠状态变化，触发窗口大小调整
watch(
  () => collapsed.value,
  () => {
    const props = unref(rootProps);
    if (props.collapseTriggerResize) {
      triggerWindowResize(); // 触发窗口大小调整
    }
  },
);

// 暴露重置和提交处理函数
defineExpose({
  handleReset,
  handleSubmit,
});
</script>
<template>
  <div
    :class="
      cn(
        'col-span-full w-full text-right',
        rootProps.compact ? 'pb-2' : 'pb-6',
        rootProps.actionWrapperClass,
      )
    "
    :style="queryFormStyle"
  >
    <template v-if="rootProps.actionButtonsReverse">
      <!-- 提交按钮前 -->
      <slot name="submit-before"></slot>

      <component
        :is="COMPONENT_MAP.PrimaryButton"
        v-if="submitButtonOptions.show"
        class="ml-3"
        type="button"
        @click="handleSubmit"
        v-bind="submitButtonOptions"
      >
        {{ submitButtonOptions.content }}
      </component>
    </template>

    <!-- 重置按钮前 -->
    <slot name="reset-before"></slot>

    <component
      :is="COMPONENT_MAP.DefaultButton"
      v-if="resetButtonOptions.show"
      class="ml-3"
      type="button"
      @click="handleReset"
      v-bind="resetButtonOptions"
    >
      {{ resetButtonOptions.content }}
    </component>

    <template v-if="!rootProps.actionButtonsReverse">
      <!-- 提交按钮前 -->
      <slot name="submit-before"></slot>

      <component
        :is="COMPONENT_MAP.PrimaryButton"
        v-if="submitButtonOptions.show"
        class="ml-3"
        type="button"
        @click="handleSubmit"
        v-bind="submitButtonOptions"
      >
        {{ submitButtonOptions.content }}
      </component>
    </template>

    <!-- 展开按钮前 -->
    <slot name="expand-before"></slot>

    <ZayumExpandableArrow
      v-if="rootProps.showCollapseButton"
      v-model:model-value="collapsed"
      class="ml-2"
    >
      <span>{{ collapsed ? $t('expand') : $t('collapse') }}</span>
    </ZayumExpandableArrow>

    <!-- 展开按钮后 -->
    <slot name="expand-after"></slot>
  </div>
</template>
