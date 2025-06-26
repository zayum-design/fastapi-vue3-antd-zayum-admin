<script setup lang="ts">
import type { CSSProperties } from 'vue';
import { computed, ref, useTemplateRef } from 'vue';
import { Check, ChevronsRight } from '@/_core/ui/icons/icons';
import { Slot } from '@/_core/ui/common-ui/shadcn-ui';

// 定义组件的 props
const props = defineProps<{
  actionStyle: CSSProperties; // 传入的自定义样式
  isPassing: boolean; // 是否验证通过
  toLeft: boolean; // 是否向左滑动
}>();

// 通过 useTemplateRef 获取 DOM 引用
const actionRef = useTemplateRef<HTMLDivElement>('actionRef');

// 记录滑块的 left 值
const left = ref('0');

// 计算属性：动态合并样式
const style = computed(() => {
  const { actionStyle } = props;
  return {
    ...actionStyle,
    left: left.value, // 设置滑块的 left 值
  };
});

// 计算属性：判断是否正在拖拽
const isDragging = computed(() => {
  const currentLeft = Number.parseInt(left.value as string);
  return currentLeft > 10 && !props.isPassing; // 当 left 大于 10 且未通过验证时，认为正在拖拽
});

// 向外暴露方法，便于父组件调用
defineExpose({
  getEl: () => {
    return actionRef.value; // 获取组件的 DOM 元素
  },
  getStyle: () => {
    return actionRef?.value?.style; // 获取组件的样式
  },
  setLeft: (val: string) => {
    left.value = val; // 设置滑块的 left 值
  },
});
</script>

<template>
  <div
    ref="actionRef"
    :class="{
      'transition-width !left-0 duration-300': toLeft, // 当 toLeft 为 true 时，应用动画效果
      'rounded-md': isDragging, // 拖拽时应用圆角样式
    }"
    :style="style"
    class="bg-background dark:bg-accent absolute left-0 top-0 flex h-full cursor-move items-center justify-center px-3.5 shadow-md"
    name="captcha-action"
  >
    <!-- 插槽：可传入自定义 icon，默认显示箭头或勾号 -->
    <Slot :is-passing="isPassing" class="text-foreground/60 size-4">
      <slot name="icon">
        <ChevronsRight v-if="!isPassing" />
        <Check v-else />
      </slot>
    </Slot>
  </div>
</template>
