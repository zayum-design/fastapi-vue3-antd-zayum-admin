<script setup lang="ts">
import type { CSSProperties } from 'vue';
import { computed, ref, watchEffect } from 'vue';
import { ZayumTooltip } from '@/_core/ui/common-ui/shadcn-ui';
import { useElementSize } from '@vueuse/core';

interface Props {
  /**
   * 是否启用点击文本展开全部
   * @default false
   */
  expand?: boolean;
  /**
   * 文本最大行数，默认1行
   * @default 1
   */
  line?: number;
  /**
   * 文本最大宽度，可以是数值（px）或百分比
   * @default '100%'
   */
  maxWidth?: number | string;
  /**
   * 提示框的位置
   * @default 'top'
   */
  placement?: 'bottom' | 'left' | 'right' | 'top';
  /**
   * 是否启用文本提示框
   * @default true
   */
  tooltip?: boolean;
  /**
   * 提示框的背景颜色，优先级高于 overlayStyle
   */
  tooltipBackgroundColor?: string;
  /**
   * 提示文本的字体颜色，优先级高于 overlayStyle
   */
  tooltipColor?: string;
  /**
   * 提示文本的字体大小，单位px，优先级高于 overlayStyle
   */
  tooltipFontSize?: number;
  /**
   * 提示框内容的最大宽度，单位px
   * 如果不设置，默认与展示文本宽度保持一致
   */
  tooltipMaxWidth?: number;
  /**
   * 提示框内容区域的样式
   * @default { textAlign: 'justify' }
   */
  tooltipOverlayStyle?: CSSProperties;
}

// 定义组件的 props，并设置默认值
const props = withDefaults(defineProps<Props>(), {
  expand: false,
  line: 1,
  maxWidth: '100%',
  placement: 'top',
  tooltip: true,
  tooltipBackgroundColor: '',
  tooltipColor: '',
  tooltipFontSize: 14,
  tooltipMaxWidth: undefined,
  tooltipOverlayStyle: () => ({ textAlign: 'justify' }),
});

// 定义事件，用于通知外部组件展开状态的变化
const emit = defineEmits<{ expandChange: [boolean] }>();

// 计算文本的最大宽度
const textMaxWidth = computed(() => {
  if (typeof props.maxWidth === 'number') {
    return `${props.maxWidth}px`;
  }
  return props.maxWidth;
});

const ellipsis = ref(); // 绑定文本元素的引用
const isExpand = ref(false); // 是否展开的状态
const defaultTooltipMaxWidth = ref(); // 提示框的最大宽度

// 获取元素的实际宽度
const { width: eleWidth } = useElementSize(ellipsis);

// 监听元素的宽度变化，并计算默认的提示框最大宽度
watchEffect(
  () => {
    if (props.tooltip && eleWidth.value) {
      defaultTooltipMaxWidth.value =
        props.tooltipMaxWidth ?? eleWidth.value + 24;
    }
  },
  { flush: 'post' }, // 在 DOM 更新后执行
);

/**
 * 切换展开状态
 */
function onExpand() {
  isExpand.value = !isExpand.value;
  emit('expandChange', isExpand.value);
}

/**
 * 处理点击展开逻辑
 * 只有在 props.expand 为 true 时才执行展开操作
 */
function handleExpand() {
  props.expand && onExpand();
}
</script>

<template>
  <div>
    <!-- 文字提示组件 -->
    <ZayumTooltip
      :content-style="{
        ...tooltipOverlayStyle,
        maxWidth: `${defaultTooltipMaxWidth}px`,
        fontSize: `${tooltipFontSize}px`,
        color: tooltipColor,
        backgroundColor: tooltipBackgroundColor,
      }"
      :disabled="!props.tooltip || isExpand" 
      :side="placement"
    >
      <!-- 自定义提示内容插槽 -->
      <slot name="tooltip">
        <slot></slot>
      </slot>

      <template #trigger>
        <div
          ref="ellipsis"
          :class="{
            '!cursor-pointer': expand, // 可点击时鼠标变为指针
            ['block truncate']: line === 1, // 单行文本溢出省略
            [$style.ellipsisMultiLine]: line > 1, // 多行文本省略
          }"
          :style="{
            '-webkit-line-clamp': isExpand ? '' : line, // 控制文本折叠的行数
            'max-width': textMaxWidth, // 设定文本的最大宽度
          }"
          class="cursor-text overflow-hidden"
          @click="handleExpand"
          v-bind="$attrs"
        >
          <slot></slot>
        </div>
      </template>
    </ZayumTooltip>
  </div>
</template>

<style module>
/* 多行文本省略样式 */
.ellipsisMultiLine {
  display: -webkit-box;
  -webkit-box-orient: vertical;
}
</style>
