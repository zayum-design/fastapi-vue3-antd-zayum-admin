<script setup lang="ts">
import type {
  CaptchaVerifyPassingData,
  SliderCaptchaProps,
  SliderRotateVerifyPassingData,
} from '../types';

import { reactive, unref, useTemplateRef, watch, watchEffect } from 'vue';

import { $t } from '@/locales';

import { cn } from '@/_core/shared/utils';

import { useTimeoutFn } from '@vueuse/core';

import SliderCaptchaAction from './slider-captcha-action.vue';
import SliderCaptchaBar from './slider-captcha-bar.vue';
import SliderCaptchaContent from './slider-captcha-content.vue';

// 定义组件的 props，包含样式、文本等
const props = withDefaults(defineProps<SliderCaptchaProps>(), {
  actionStyle: () => ({}),
  barStyle: () => ({}),
  contentStyle: () => ({}),
  isSlot: false,
  successText: '',
  text: '',
  wrapperStyle: () => ({}),
});

// 定义事件的 emit 类型
const emit = defineEmits<{
  end: [MouseEvent | TouchEvent];
  move: [SliderRotateVerifyPassingData];
  start: [MouseEvent | TouchEvent];
  success: [CaptchaVerifyPassingData];
}>();

// 定义 v-model 双向绑定的状态
const modelValue = defineModel<boolean>({ default: false });

// 定义组件内部的状态
const state = reactive({
  endTime: 0,
  isMoving: false,
  isPassing: false,
  moveDistance: 0,
  startTime: 0,
  toLeft: false,
});

// 暴露 resume 方法给外部调用
defineExpose({
  resume,
});

// 使用 template ref 引用 DOM 元素
const wrapperRef = useTemplateRef<HTMLDivElement>('wrapperRef');
const barRef = useTemplateRef<typeof SliderCaptchaBar>('barRef');
const contentRef = useTemplateRef<typeof SliderCaptchaContent>('contentRef');
const actionRef = useTemplateRef<typeof SliderCaptchaAction>('actionRef');

// 监听 state.isPassing 的变化，当成功时触发 success 事件
watch(
  () => state.isPassing,
  (isPassing) => {
    if (isPassing) {
      const { endTime, startTime } = state;
      const time = (endTime - startTime) / 1000; // 计算验证时间
      emit('success', { isPassing, time: time.toFixed(1) });
      modelValue.value = isPassing; // 更新 v-model 值
    }
  },
);

// 监听 modelValue 的变化，更新 isPassing 状态
watchEffect(() => {
  state.isPassing = !!modelValue.value;
});

// 获取事件的 pageX 值
function getEventPageX(e: MouseEvent | TouchEvent): number {
  if ('pageX' in e) {
    return e.pageX;
  } else if ('touches' in e && e.touches[0]) {
    return e.touches[0].pageX;
  }
  return 0;
}

// 处理拖动开始事件
function handleDragStart(e: MouseEvent | TouchEvent) {
  if (state.isPassing) {
    return;
  }
  if (!actionRef.value) return;
  emit('start', e); // 触发 start 事件

  // 计算拖动的起始位置
  state.moveDistance =
    getEventPageX(e) -
    Number.parseInt(
      actionRef.value.getStyle().left.replace('px', '') || '0',
      10,
    );
  state.startTime = Date.now(); // 记录开始时间
  state.isMoving = true; // 设置为正在拖动
}

// 获取偏移量
function getOffset(actionEl: HTMLDivElement) {
  const wrapperWidth = wrapperRef.value?.offsetWidth ?? 220;
  const actionWidth = actionEl?.offsetWidth ?? 40;
  const offset = wrapperWidth - actionWidth - 6;
  return { actionWidth, offset, wrapperWidth };
}

// 处理拖动过程中事件
function handleDragMoving(e: MouseEvent | TouchEvent) {
  const { isMoving, moveDistance } = state;
  if (isMoving) {
    const actionEl = unref(actionRef);
    const barEl = unref(barRef);
    if (!actionEl || !barEl) return;
    const { actionWidth, offset, wrapperWidth } = getOffset(actionEl.getEl());
    const moveX = getEventPageX(e) - moveDistance;

    emit('move', {
      event: e,
      moveDistance,
      moveX,
    });
    if (moveX > 0 && moveX <= offset) {
      // 更新拖动元素的位置
      actionEl.setLeft(`${moveX}px`);
      barEl.setWidth(`${moveX + actionWidth / 2}px`);
    } else if (moveX > offset) {
      // 拖动超出范围，设置为最大值
      actionEl.setLeft(`${wrapperWidth - actionWidth}px`);
      barEl.setWidth(`${wrapperWidth - actionWidth / 2}px`);
      if (!props.isSlot) {
        checkPass(); // 检查是否验证通过
      }
    }
  }
}

// 处理拖动结束事件
function handleDragOver(e: MouseEvent | TouchEvent) {
  const { isMoving, isPassing, moveDistance } = state;
  if (isMoving && !isPassing) {
    emit('end', e); // 触发 end 事件
    const actionEl = actionRef.value;
    const barEl = unref(barRef);
    if (!actionEl || !barEl) return;
    const moveX = getEventPageX(e) - moveDistance;
    const { actionWidth, offset, wrapperWidth } = getOffset(actionEl.getEl());
    if (moveX < offset) {
      if (props.isSlot) {
        setTimeout(() => {
          if (modelValue.value) {
            const contentEl = unref(contentRef);
            if (contentEl) {
              contentEl.getEl().style.width = `${Number.parseInt(barEl.getEl().style.width)}px`;
            }
          } else {
            resume();
          }
        }, 0);
      } else {
        resume();
      }
    } else {
      actionEl.setLeft(`${wrapperWidth - actionWidth}px`);
      barEl.setWidth(`${wrapperWidth - actionWidth / 2}px`);
      checkPass(); // 检查是否验证通过
    }
    state.isMoving = false; // 设置拖动结束
  }
}

// 检查是否通过验证
function checkPass() {
  if (props.isSlot) {
    resume();
    return;
  }
  state.endTime = Date.now(); // 记录结束时间
  state.isPassing = true; // 设置为通过
  state.isMoving = false; // 设置为停止移动
}

// 恢复初始状态
function resume() {
  state.isMoving = false;
  state.isPassing = false;
  state.moveDistance = 0;
  state.toLeft = false;
  state.startTime = 0;
  state.endTime = 0;
  const actionEl = unref(actionRef);
  const barEl = unref(barRef);
  const contentEl = unref(contentRef);
  if (!actionEl || !barEl || !contentEl) return;

  contentEl.getEl().style.width = '100%'; // 重置宽度
  state.toLeft = true;
  useTimeoutFn(() => {
    state.toLeft = false;
    actionEl.setLeft('0'); // 重置位置
    barEl.setWidth('0'); // 重置进度条宽度
  }, 300);
}
</script>

<template>
  <div
    ref="wrapperRef"
    :class="
      cn(
        'border-border bg-background-deep relative flex h-10 w-full items-center overflow-hidden rounded-md border text-center',
        props.class,
      )
    "
    :style="wrapperStyle"
    @mouseleave="handleDragOver"
    @mousemove="handleDragMoving"
    @mouseup="handleDragOver"
    @touchend="handleDragOver"
    @touchmove="handleDragMoving"
  >
    <SliderCaptchaBar
      ref="barRef"
      :bar-style="barStyle"
      :to-left="state.toLeft"
      :is-passing="state.isPassing"
    />
    <SliderCaptchaContent
      ref="contentRef"
      :content-style="contentStyle"
      :is-passing="state.isPassing"
      :success-text="successText || $t('ui.captcha.sliderSuccessText')"
      :text="text || $t('ui.captcha.sliderDefaultText')"
    >
      <template v-if="$slots.text" #text>
        <slot :is-passing="state.isPassing" name="text"></slot>
      </template>
    </SliderCaptchaContent>

    <SliderCaptchaAction
      ref="actionRef"
      :action-style="actionStyle"
      :is-passing="state.isPassing"
      :to-left="state.toLeft"
      @mousedown="handleDragStart"
      @touchstart="handleDragStart"
    >
      <template v-if="$slots.actionIcon" #icon>
        <slot :is-passing="state.isPassing" name="actionIcon"></slot>
      </template>
    </SliderCaptchaAction>
  </div>
</template>
