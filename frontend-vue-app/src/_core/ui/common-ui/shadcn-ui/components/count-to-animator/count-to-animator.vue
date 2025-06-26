<script lang="ts" setup>
/* 
  以下代码为 CountToAnimator 组件的逻辑部分，
  使用了 Vue 3 的 Composition API 和 TypeScript，
  仅在原有代码上增加详细中文注释，未对代码进行任何删除或修改。
*/

// 导入 Vue 中的响应式 API 和生命周期函数
import { computed, onMounted, ref, unref, watch, watchEffect } from 'vue';

// 导入工具函数 isNumber，用于判断传入的值是否为数字
import { isNumber } from '@/_core/shared/utils';

// 导入 @vueuse/core 中的动画过渡工具，包括内置的过渡预设和 useTransition 函数
import { TransitionPresets, useTransition } from '@vueuse/core';

// 定义组件的 Props 接口，声明组件可以接收的属性以及它们的类型
interface Props {
  autoplay?: boolean; // 是否在组件加载时自动播放动画
  color?: string; // 显示数字的颜色
  decimal?: string; // 用作小数点的字符
  decimals?: number; // 显示数字时保留的小数位数
  duration?: number; // 动画持续时间（单位：毫秒）
  endVal?: number; // 数字动画的结束值
  prefix?: string; // 数字前缀
  separator?: string; // 千位分隔符
  startVal?: number; // 数字动画的起始值
  suffix?: string; // 数字后缀
  transition?: keyof typeof TransitionPresets; // 选择的动画过渡预设名称
  useEasing?: boolean; // 是否启用缓动（easing）效果
}

// 设置组件名称为 'CountToAnimator'
defineOptions({ name: 'CountToAnimator' });

// 定义并初始化组件的 Props，同时设置默认值
const props = withDefaults(defineProps<Props>(), {
  autoplay: true,
  color: '',
  decimal: '.',
  decimals: 0,
  duration: 1500,
  endVal: 2021,
  prefix: '',
  separator: ',',
  startVal: 0,
  suffix: '',
  transition: 'linear',
  useEasing: true,
});

// 定义组件可以触发的自定义事件，这里包括动画开始和动画结束事件
const emit = defineEmits(['onStarted', 'onFinished']);

// 创建响应式变量 source，用于存储当前动画的数字值，初始值为 props.startVal
const source = ref(props.startVal);

// 创建响应式变量 disabled，用来控制动画是否被禁用，初始值为 false（即动画默认启用）
const disabled = ref(false);

// 初始化 outputValue，通过 useTransition 实现数字从 startVal 到 endVal 的动画过渡效果
let outputValue = useTransition(source);

// 定义计算属性 value，通过 formatNumber 函数格式化 outputValue 的值，确保数字显示格式符合要求
const value = computed(() => formatNumber(unref(outputValue)));

// 使用 watchEffect 监听响应式依赖变化，每次依赖变化时将 source 重置为初始值 props.startVal
watchEffect(() => {
  source.value = props.startVal;
});

// 监听 props.startVal 和 props.endVal 的变化，若自动播放开启，则重新启动动画
watch([() => props.startVal, () => props.endVal], () => {
  if (props.autoplay) {
    start();
  }
});

// 在组件挂载完成时，若自动播放属性为 true，则立即启动动画
onMounted(() => {
  props.autoplay && start();
});

// 定义 start 函数：先调用 run 函数初始化动画设置，然后将 source 的值更新为动画结束值，从而触发动画
function start() {
  run();
  source.value = props.endVal;
}

// 定义 reset 函数：将 source 的值重置为起始值 props.startVal，并重新执行动画
function reset() {
  source.value = props.startVal;
  run();
}

// 定义 run 函数：设置动画的过渡效果，包括动画持续时间、是否禁用动画、动画开始和结束时触发的事件，以及是否使用缓动效果
function run() {
  outputValue = useTransition(source, {
    disabled, // 动画是否被禁用
    duration: props.duration, // 动画持续时间
    onFinished: () => emit('onFinished'), // 动画完成后触发 onFinished 事件
    onStarted: () => emit('onStarted'), // 动画开始时触发 onStarted 事件
    // 如果启用缓动效果，则根据传入的 transition 属性选取对应的过渡预设，否则不设置
    ...(props.useEasing
      ? { transition: TransitionPresets[props.transition] }
      : {}),
  });
}

// 定义 formatNumber 函数：用于格式化数字，添加前缀、后缀、指定小数位数及千位分隔符
function formatNumber(num: number | string) {
  // 如果 num 既不是有效数字也不等于 0，则返回空字符串
  if (!num && num !== 0) {
    return '';
  }
  // 从 props 中解构出用于格式化的相关参数
  const { decimal, decimals, prefix, separator, suffix } = props;
  // 将数字转换为固定小数位数的字符串
  num = Number(num).toFixed(decimals);
  num += ''; // 强制转换为字符串

  // 将数字字符串分割为整数部分和小数部分
  const x = num.split('.');
  let x1 = x[0]; // 整数部分
  // 如果存在小数部分，则添加自定义小数点及小数部分；否则为空字符串
  const x2 = x.length > 1 ? decimal + x[1] : '';

  // 定义正则表达式，用于匹配整数部分中需要添加千位分隔符的位置
  const rgx = /(\d+)(\d{3})/;
  // 如果定义了分隔符，并且该分隔符不是数字，同时整数部分存在，则循环添加分隔符
  if (separator && !isNumber(separator) && x1) {
    while (rgx.test(x1)) {
      x1 = x1.replace(rgx, `$1${separator}$2`);
    }
  }
  // 返回最终格式化后的字符串，格式为：前缀 + 格式化整数部分 + 小数部分 + 后缀
  return prefix + x1 + x2 + suffix;
}

// 通过 defineExpose 导出 reset 函数，允许外部组件调用该方法重置动画
defineExpose({ reset });
</script>

<template>
  <!-- 使用 span 标签显示格式化后的数字，动态绑定样式中的颜色属性 -->
  <span :style="{ color }">
    {{ value }}
  </span>
</template>
