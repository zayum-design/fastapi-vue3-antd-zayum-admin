<script setup lang="ts">
import type { CSSProperties } from 'vue';

import { computed, useTemplateRef } from 'vue';

import { ZayumSpineText } from '@/_core/ui/common-ui/shadcn-ui';

// 定义组件的 props
const props = defineProps<{
  contentStyle: CSSProperties; // 传入的自定义样式
  isPassing: boolean; // 是否验证通过
  successText: string; // 成功时显示的文本
  text: string; // 默认文本
}>();

// 通过 useTemplateRef 获取 DOM 引用
const contentRef = useTemplateRef<HTMLDivElement>('contentRef');

// 计算属性：动态合并样式
const style = computed(() => {
  const { contentStyle } = props;
  return {
    ...contentStyle,
  };
});

// 向外暴露方法，便于父组件调用
defineExpose({
  getEl: () => {
    return contentRef.value; // 获取组件的 DOM 元素
  },
});
</script>

<template>
  <div
    ref="contentRef"
    :class="{
      [$style.success]: isPassing, // 成功时应用特殊样式
    }"
    :style="style"
    class="absolute top-0 flex size-full select-none items-center justify-center text-xs"
  >
    <!-- 插槽：可传入自定义文本，默认显示 successText 或 text -->
    <slot name="text">
      <ZayumSpineText class="flex h-full items-center">
        {{ isPassing ? successText : text }}
      </ZayumSpineText>
    </slot>
  </div>
</template>

<style module>
.success {
  -webkit-text-fill-color: hsl(0deg 0% 98%); /* 成功状态时的文本填充颜色 */
}
</style>
