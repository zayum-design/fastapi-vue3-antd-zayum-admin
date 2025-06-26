<script lang="ts" setup>
import type { ColPageProps } from './types';

import { computed, ref, useSlots } from 'vue';

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/_core/ui/common-ui/shadcn-ui';

import Page from '../page/page.vue';

// 定义组件名称和属性继承选项
defineOptions({
  name: 'ColPage',
  inheritAttrs: false,
});

// 定义组件的 props，并提供默认值
const props = withDefaults(defineProps<ColPageProps>(), {
  leftWidth: 30, // 左侧面板默认宽度（百分比）
  rightWidth: 70, // 右侧面板默认宽度（百分比）
  resizable: true, // 是否支持拖动调整大小
});

// 计算需要传递给 Page 组件的 props
const delegatedProps = computed(() => {
  const { leftWidth: _, ...delegated } = props;
  return delegated;
});

const slots = useSlots();

// 计算需要传递的插槽
const delegatedSlots = computed(() => {
  const resultSlots: string[] = [];
  for (const key of Object.keys(slots)) {
    if (!['default', 'left'].includes(key)) {
      resultSlots.push(key);
    }
  }
  return resultSlots;
});

// 获取左侧面板的引用
const leftPanelRef = ref<InstanceType<typeof ResizablePanel>>();

// 展开左侧面板
function expandLeft() {
  leftPanelRef.value?.expand();
}

// 收起左侧面板
function collapseLeft() {
  leftPanelRef.value?.collapse();
}

// 向外暴露方法
defineExpose({
  expandLeft,
  collapseLeft,
});
</script>

<template>
  <Page v-bind="delegatedProps">
    <!-- 继承默认的 slot -->
    <template
      v-for="slotName in delegatedSlots"
      :key="slotName"
      #[slotName]="slotProps"
    >
      <slot :name="slotName" v-bind="slotProps"></slot>
    </template>

    <!-- 可调整大小的面板组 -->
    <ResizablePanelGroup class="w-full" direction="horizontal">
      <!-- 左侧面板 -->
      <ResizablePanel
        ref="leftPanelRef"
        :collapsed-size="leftCollapsedWidth"
        :collapsible="leftCollapsible"
        :default-size="leftWidth"
        :max-size="leftMaxWidth"
        :min-size="leftMinWidth"
      >
        <template #default="slotProps">
          <slot
            name="left"
            v-bind="{
              ...slotProps,
              expand: expandLeft,
              collapse: collapseLeft,
            }"
          ></slot>
        </template>
      </ResizablePanel>
      
      <!-- 中间拖拽调整大小的分割线 -->
      <ResizableHandle
        v-if="resizable"
        :style="{ backgroundColor: splitLine ? undefined : 'transparent' }"
        :with-handle="splitHandle"
      />
      
      <!-- 右侧面板 -->
      <ResizablePanel
        :collapsed-size="rightCollapsedWidth"
        :collapsible="rightCollapsible"
        :default-size="rightWidth"
        :max-size="rightMaxWidth"
        :min-size="rightMinWidth"
      >
        <template #default>
          <slot></slot>
        </template>
      </ResizablePanel>
    </ResizablePanelGroup>
  </Page>
</template>
