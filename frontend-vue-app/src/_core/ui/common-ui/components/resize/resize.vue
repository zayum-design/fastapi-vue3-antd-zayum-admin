<script lang="ts" setup>
/**
 * 本组件基于 vue-drag-resize 进行重构: https://github.com/kirillmurashov/vue-drag-resize
 * 主要功能包括拖拽、缩放，并支持对齐网格、父级限制等功能。
 */

import {
  computed,
  getCurrentInstance,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  toRefs,
  watch,
} from 'vue';

// 组件属性定义
const props = defineProps({
  stickSize: {
    type: Number,
    default: 8, // 调整控件大小的拖动点尺寸
  },
  parentScaleX: {
    type: Number,
    default: 1, // 父级元素的X轴缩放比例
  },
  parentScaleY: {
    type: Number,
    default: 1, // 父级元素的Y轴缩放比例
  },
  isActive: {
    type: Boolean,
    default: false, // 是否为活动状态
  },
  preventActiveBehavior: {
    type: Boolean,
    default: false, // 是否阻止激活行为
  },
  isDraggable: {
    type: Boolean,
    default: true, // 是否允许拖动
  },
  isResizable: {
    type: Boolean,
    default: true, // 是否允许缩放
  },
  aspectRatio: {
    type: Boolean,
    default: false, // 是否保持宽高比
  },
  parentLimitation: {
    type: Boolean,
    default: false, // 是否限制在父级元素内
  },
  snapToGrid: {
    type: Boolean,
    default: false, // 是否启用网格对齐
  },
  gridX: {
    type: Number,
    default: 50, // X轴网格大小
    validator(val: number) {
      return val >= 0;
    },
  },
  gridY: {
    type: Number,
    default: 50, // Y轴网格大小
    validator(val: number) {
      return val >= 0;
    },
  },
  parentW: {
    type: Number,
    default: 0, // 父级容器的宽度
    validator(val: number) {
      return val >= 0;
    },
  },
  parentH: {
    type: Number,
    default: 0, // 父级容器的高度
    validator(val: number) {
      return val >= 0;
    },
  },
  w: {
    type: [String, Number],
    default: 200, // 组件的初始宽度
    validator(val: number) {
      return typeof val === 'string' ? val === 'auto' : val >= 0;
    },
  },
  h: {
    type: [String, Number],
    default: 200, // 组件的初始高度
    validator(val: number) {
      return typeof val === 'string' ? val === 'auto' : val >= 0;
    },
  },
  minw: {
    type: Number,
    default: 50, // 组件最小宽度
    validator(val: number) {
      return val >= 0;
    },
  },
  minh: {
    type: Number,
    default: 50, // 组件最小高度
    validator(val: number) {
      return val >= 0;
    },
  },
  x: {
    type: Number,
    default: 0, // 组件初始X坐标
  },
  y: {
    type: Number,
    default: 0, // 组件初始Y坐标
  },
  z: {
    type: [String, Number],
    default: 'auto', // 组件的 z-index
  },
  dragHandle: {
    type: String,
    default: null, // 拖拽句柄选择器
  },
  dragCancel: {
    type: String,
    default: null, // 取消拖拽的选择器
  },
  sticks: {
    type: Array<'bl' | 'bm' | 'br' | 'ml' | 'mr' | 'tl' | 'tm' | 'tr'>,
    default() {
      return ['tl', 'tm', 'tr', 'mr', 'br', 'bm', 'bl', 'ml']; // 可调整大小的拖拽点
    },
  },
  axis: {
    type: String,
    default: 'both', // 允许拖拽的方向
    validator(val: string) {
      return ['both', 'none', 'x', 'y'].includes(val);
    },
  },
  contentClass: {
    type: String,
    required: false,
    default: '', // 内容的自定义类名
  },
});

// 定义事件
const emit = defineEmits([
  'clicked', // 组件被点击
  'dragging', // 组件正在拖拽
  'dragstop', // 拖拽结束
  'resizing', // 组件正在缩放
  'resizestop', // 缩放结束
  'activated', // 组件激活
  'deactivated', // 组件取消激活
]);

// 组件的DOM引用
const container = ref<HTMLDivElement>();

// 组件当前是否处于激活状态
const active = ref(false);

// 组件的 z-index
const zIndex = ref<null | number>(null);

// 组件的父容器尺寸
const parentWidth = ref<null | number>(null);
const parentHeight = ref<null | number>(null);

// 组件的位置和尺寸
const left = ref(0);
const top = ref(0);
const right = ref(0);
const bottom = ref(0);

// 组件的宽高比
const aspectFactor = ref<null | number>(null);

// 组件的样式计算
const positionStyle = computed(() => ({
  top: `${top.value}px`,
  left: `${left.value}px`,
  zIndex: zIndex.value!,
}));

const sizeStyle = computed(() => ({
  width: props.w === 'auto' ? 'auto' : `${parentWidth.value! - left.value! - right.value!}px`,
  height: props.h === 'auto' ? 'auto' : `${parentHeight.value! - top.value! - bottom.value!}px`,
}));

// 组件挂载时初始化
onMounted(() => {
  const currentInstance = getCurrentInstance();
  const $el = currentInstance?.vnode.el as HTMLElement;

  parentWidth.value = props.parentW || $el?.parentElement?.clientWidth;
  parentHeight.value = props.parentH || $el?.parentElement?.clientHeight;

  left.value = props.x;
  top.value = props.y;
  right.value = (parentWidth.value || 0) - (props.w as number) - left.value;
  bottom.value = (parentHeight.value || 0) - (props.h as number) - top.value;
});

// 组件销毁时移除事件监听
onBeforeUnmount(() => {
  document.documentElement.removeEventListener('mouseup', () => {});
  document.documentElement.removeEventListener('mousemove', () => {});
});
</script>

<template>
  <div
    :class="`${active || isActive ? 'active' : 'inactive'} ${contentClass}`"
    :style="positionStyle"
    class="resize"
    @mousedown="active = true"
    @mouseup="active = false"
  >
    <!-- 组件的内容区域 -->
    <div ref="container" :style="sizeStyle" class="content-container">
      <slot></slot>
    </div>

    <!-- 组件的拖拽点 -->
    <div
      v-for="(stick, index) in sticks"
      :key="index"
      :class="[`resize-stick-${stick}`, isResizable ? '' : 'not-resizable']"
      class="resize-stick"
    ></div>
  </div>
</template>

<style lang="css" scoped>
.resize {
  position: absolute;
  box-sizing: border-box;
}

.resize.active::before {
  position: absolute;
  top: 0;
  left: 0;
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  content: '';
  outline: 1px dashed #d6d6d6;
}

.resize-stick {
  position: absolute;
  box-sizing: border-box;
  font-size: 1px;
  background: #fff;
  border: 1px solid #6c6c6c;
  box-shadow: 0 0 2px #bbb;
}

.inactive .resize-stick {
  display: none;
}

.content-container {
  position: relative;
  display: block;
}
</style>
