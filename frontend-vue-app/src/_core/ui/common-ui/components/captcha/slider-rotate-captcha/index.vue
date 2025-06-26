<script setup lang="ts">
import type {
  CaptchaVerifyPassingData,
  SliderCaptchaActionType,
  SliderRotateCaptchaProps,
  SliderRotateVerifyPassingData,
} from '../types';

import { computed, reactive, unref, useTemplateRef, watch } from 'vue';
import { $t } from '@/locales';
import { useTimeoutFn } from '@vueuse/core';
import SliderCaptcha from '../slider-captcha/index.vue';

// 定义组件的 props，并设置默认值
const props = withDefaults(defineProps<SliderRotateCaptchaProps>(), {
  defaultTip: '', // 默认提示文本
  diffDegree: 20, // 容错角度
  imageSize: 260, // 图片尺寸
  maxDegree: 300, // 最大旋转角度
  minDegree: 120, // 最小旋转角度
  src: '', // 图片地址
});

// 定义事件
const emit = defineEmits<{
  success: [CaptchaVerifyPassingData]; // 成功事件，传递验证数据
}>();

const slideBarRef = useTemplateRef<SliderCaptchaActionType>('slideBarRef');

// 定义组件的状态
const state = reactive({
  currentRotate: 0, // 当前旋转角度
  dragging: false, // 是否正在拖动
  endTime: 0, // 结束时间
  imgStyle: {}, // 图片样式
  isPassing: false, // 是否通过验证
  randomRotate: 0, // 目标旋转角度
  showTip: false, // 是否显示提示
  startTime: 0, // 开始时间
  toOrigin: false // 是否返回原点
});

const modalValue = defineModel<boolean>({ default: false });

// 监听 isPassing 状态变化
watch(
  () => state.isPassing,
  (isPassing) => {
    if (isPassing) {
      const { endTime, startTime } = state;
      const time = (endTime - startTime) / 1000;
      emit('success', { isPassing, time: time.toFixed(1) });
    }
    modalValue.value = isPassing;
  },
);

// 计算图片容器样式
const getImgWrapStyleRef = computed(() => {
  const { imageSize, imageWrapperStyle } = props;
  return {
    height: `${imageSize}px`,
    width: `${imageSize}px`,
    ...imageWrapperStyle,
  };
});

// 计算旋转系数
const getFactorRef = computed(() => {
  const { maxDegree, minDegree } = props;
  if (minDegree > maxDegree) {
    console.warn('minDegree should not be greater than maxDegree');
  }
  return minDegree === maxDegree ? Math.floor(1 + Math.random() * 1) / 10 + 1 : 1;
});

// 开始拖动时记录时间
function handleStart() {
  state.startTime = Date.now();
}

// 处理滑动条移动
function handleDragBarMove(data: SliderRotateVerifyPassingData) {
  state.dragging = true;
  const { imageSize, maxDegree } = props;
  const { moveX } = data;
  const denominator = imageSize!;
  if (denominator === 0) return;
  
  const currentRotate = Math.ceil((moveX / denominator) * 1.5 * maxDegree! * unref(getFactorRef));
  state.currentRotate = currentRotate;
  setImgRotate(state.randomRotate - currentRotate);
}

// 图片加载完成后生成随机旋转角度
function handleImgOnLoad() {
  const { maxDegree, minDegree } = props;
  const ranRotate = Math.floor(minDegree! + Math.random() * (maxDegree! - minDegree!));
  state.randomRotate = ranRotate;
  setImgRotate(ranRotate);
}

// 拖动结束时检查验证是否成功
function handleDragEnd() {
  const { currentRotate, randomRotate } = state;
  const { diffDegree } = props;
  
  if (Math.abs(randomRotate - currentRotate) >= (diffDegree || 20)) {
    setImgRotate(randomRotate);
    state.toOrigin = true;
    useTimeoutFn(() => {
      state.toOrigin = false;
      state.showTip = true;
    }, 300);
  } else {
    checkPass();
  }
  state.showTip = true;
  state.dragging = false;
}

// 设置图片旋转角度
function setImgRotate(deg: number) {
  state.imgStyle = { transform: `rotateZ(${deg}deg)` };
}

// 验证成功时更新状态
function checkPass() {
  state.isPassing = true;
  state.endTime = Date.now();
}

// 重置验证码
function resume() {
  state.showTip = false;
  const basicEl = unref(slideBarRef);
  if (!basicEl) return;
  state.isPassing = false;
  basicEl.resume();
  handleImgOnLoad();
}

const imgCls = computed(() => (state.toOrigin ? ['transition-transform duration-300'] : []));

const verifyTip = computed(() => {
  return state.isPassing
    ? $t('ui.captcha.sliderRotateSuccessTip', [((state.endTime - state.startTime) / 1000).toFixed(1)])
    : $t('ui.captcha.sliderRotateFailTip');
});

// 向外暴露方法
defineExpose({ resume });
</script>

<template>
  <div class="relative flex flex-col items-center">
    <div :style="getImgWrapStyleRef" class="border-border relative cursor-pointer overflow-hidden rounded-full border shadow-md">
      <img :class="imgCls" :src="src" :style="state.imgStyle" alt="verify" class="w-full rounded-full" @click="resume" @load="handleImgOnLoad" />
      <div class="absolute bottom-3 left-0 z-10 block h-7 w-full text-center text-xs leading-[30px] text-white">
        <div v-if="state.showTip" :class="{ 'bg-success/80': state.isPassing, 'bg-destructive/80': !state.isPassing }">
          {{ verifyTip }}
        </div>
        <div v-if="!state.dragging" class="bg-black/30">
          {{ defaultTip || $t('ui.captcha.sliderRotateDefaultTip') }}
        </div>
      </div>
    </div>

    <SliderCaptcha ref="slideBarRef" v-model="modalValue" class="mt-5" is-slot @end="handleDragEnd" @move="handleDragBarMove" @start="handleStart">
      <template v-for="(_, key) in $slots" :key="key" #[key]="slotProps">
        <slot :name="key" v-bind="slotProps"></slot>
      </template>
    </SliderCaptcha>
  </div>
</template>