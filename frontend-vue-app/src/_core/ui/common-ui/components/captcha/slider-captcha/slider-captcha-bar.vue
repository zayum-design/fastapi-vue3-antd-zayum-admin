<script setup lang="ts">
import type { CSSProperties } from 'vue';

import { computed, ref, useTemplateRef } from 'vue';

// 定义组件的 props
const props = defineProps<{
  barStyle: CSSProperties; // 传入的自定义样式
  toLeft: boolean; // 是否向左收缩
  isPassing?: boolean; // 是否验证通过（显示打勾动画）
}>();

// 通过 useTemplateRef 获取 DOM 引用
const barRef = useTemplateRef<HTMLDivElement>('barRef');

// 记录滑块的宽度
const width = ref('0');

// 计算属性：判断是否到达最右侧并验证通过
const isFullWidth = computed(() => {
  const currentWidth = Number.parseInt(width.value);
  // 当验证通过且宽度接近容器宽度时添加w-full类
  return props.isPassing && currentWidth > 200;
});

// 计算属性：动态合并样式
const style = computed(() => {
  const { barStyle } = props;
  return {
    ...barStyle,
    width: width.value, // 设置滑块的宽度
  };
});

// 向外暴露方法，便于父组件调用
defineExpose({
  getEl: () => {
    return barRef.value; // 获取组件的 DOM 元素
  },
  setWidth: (val: string) => {
    width.value = val; // 设置滑块的宽度
  },
});
</script>

<template>
  <div
    ref="barRef"
    :class="{
      'transition-width !w-0 duration-300': toLeft,
      'w-full': isFullWidth,
    }"
    class="bg-success absolute h-full"
  ></div>
</template>
