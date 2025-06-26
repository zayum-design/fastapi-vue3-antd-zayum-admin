<script setup lang="ts">
import type { StyleValue } from 'vue';

import type { PageProps } from './types';

import { computed, nextTick, onMounted, ref, useTemplateRef } from 'vue';

import { CSS_VARIABLE_LAYOUT_CONTENT_HEIGHT } from '@/_core/shared/constants';
import { cn } from '@/_core/shared/utils';

defineOptions({
  name: 'Page',
});

// 定义组件接收的属性，并设置默认值
const { autoContentHeight = false } = defineProps<PageProps>();

// 记录页头高度
const headerHeight = ref(0);
// 记录页脚高度
const footerHeight = ref(0);
// 是否自动计算内容高度
const shouldAutoHeight = ref(false);

// 页头的 DOM 引用
const headerRef = useTemplateRef<HTMLDivElement>('headerRef');
// 页脚的 DOM 引用
const footerRef = useTemplateRef<HTMLDivElement>('footerRef');

// 计算内容区域的样式
const contentStyle = computed<StyleValue>(() => {
  if (autoContentHeight) {
    return {
      // 计算内容区域高度：布局内容总高度 - 页头高度
      height: `calc(var(${CSS_VARIABLE_LAYOUT_CONTENT_HEIGHT}) - ${headerHeight.value}px)`,
      // 根据 shouldAutoHeight 决定是否允许滚动
      overflowY: shouldAutoHeight.value ? 'auto' : 'unset',
    };
  }
  return {};
});

// 计算内容区域的实际高度
async function calcContentHeight() {
  if (!autoContentHeight) {
    return;
  }
  await nextTick();
  // 获取页头和页脚的实际高度
  headerHeight.value = headerRef.value?.offsetHeight || 0;
  footerHeight.value = footerRef.value?.offsetHeight || 0;
  // 设定延迟后启用自动滚动
  setTimeout(() => {
    shouldAutoHeight.value = true;
  }, 30);
}

// 组件挂载时计算内容区域高度
onMounted(() => {
  calcContentHeight();
});
</script>

<template>
  <div class="relative">
    <!-- 页头部分 -->
    <div
      v-if="
        description ||
        $slots.description ||
        title ||
        $slots.title ||
        $slots.extra
      "
      ref="headerRef"
      :class="
        cn(
          'bg-card border-border relative flex items-end border-b px-6 py-4',
          headerClass,
        )
      "
    >
      <div class="flex-auto">
        <!-- 标题插槽 -->
        <slot name="title">
          <div v-if="title" class="mb-2 flex text-lg font-semibold">
            {{ title }}
          </div>
        </slot>

        <!-- 描述插槽 -->
        <slot name="description">
          <p v-if="description" class="text-muted-foreground">
            {{ description }}
          </p>
        </slot>
      </div>

      <!-- 额外内容插槽 -->
      <div v-if="$slots.extra">
        <slot name="extra"></slot>
      </div>
    </div>

    <!-- 内容区域 -->
    <div :class="cn('h-full p-4', contentClass)" :style="contentStyle">
      <slot></slot>
    </div>

    <!-- 页脚部分 -->
    <div
      v-if="$slots.footer"
      ref="footerRef"
      :class="
        cn(
          'bg-card align-center absolute bottom-0 left-0 right-0 flex px-6 py-4',
          footerClass,
        )
      "
    >
      <slot name="footer"></slot>
    </div>
  </div>
</template>
