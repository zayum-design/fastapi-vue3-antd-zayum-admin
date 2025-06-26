<script setup lang="ts">
// 引入 PointSelectionCaptchaCardProps 类型定义
import type { PointSelectionCaptchaCardProps } from '../types';

// 从 vue 中引入 computed，用于计算属性
import { computed } from 'vue';

// 引入国际化函数 $t，用于多语言支持
import { $t } from '@/locales';

// 引入 shadcn-ui 中的各个卡片组件
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/_core/ui/common-ui/shadcn-ui';

// 定义组件的 props，并设置默认值
const props = withDefaults(defineProps<PointSelectionCaptchaCardProps>(), {
  height: '220px',
  paddingX: '12px',
  paddingY: '16px',
  title: '',
  width: '300px',
});

// 定义组件的自定义事件，这里定义了 click 事件
const emit = defineEmits<{
  click: [MouseEvent];
}>();

// 辅助函数：解析数值或字符串形式的数值，返回数值型
const parseValue = (value: number | string) => {
  if (typeof value === 'number') {
    return value;
  }
  const parsed = Number.parseFloat(value);
  return Number.isNaN(parsed) ? 0 : parsed;
};

// 计算根容器的样式，根据传入的 padding 和宽度计算
const rootStyles = computed(() => ({
  padding: `${parseValue(props.paddingY)}px ${parseValue(props.paddingX)}px`,
  width: `${parseValue(props.width) + parseValue(props.paddingX) * 2}px`,
}));

// 计算验证码图片的样式，设置高度和宽度
const captchaStyles = computed(() => {
  return {
    height: `${parseValue(props.height)}px`,
    width: `${parseValue(props.width)}px`,
  };
});

// 点击事件处理函数，触发自定义的 click 事件
function handleClick(e: MouseEvent) {
  emit('click', e);
}
</script>

<template>
  <!-- 根容器 Card 组件，绑定计算后的样式和 ARIA 属性 -->
  <Card :style="rootStyles" aria-labelledby="captcha-title" role="region">
    <!-- 卡片头部 -->
    <CardHeader class="p-0">
      <CardTitle id="captcha-title" class="flex items-center justify-between">
        <!-- 判断是否提供 title 插槽 -->
        <template v-if="$slots.title">
          <!-- 如果提供 title 插槽，则使用插槽内容；否则使用国际化默认文本 -->
          <slot name="title">{{ $t('ui.captcha.title') }}</slot>
        </template>
        <template v-else>
          <span>{{ title }}</span>
        </template>
        <!-- 右侧额外内容插槽 -->
        <div class="flex items-center justify-end">
          <slot name="extra"></slot>
        </div>
      </CardTitle>
    </CardHeader>
    <!-- 卡片内容部分 -->
    <CardContent class="relative mt-2 flex w-full overflow-hidden rounded p-0">
      <!-- 验证码图片 -->
      <img
        v-show="captchaImage"  <!-- 显示验证码图片的条件 -->
        :alt="$t('ui.captcha.alt')"  <!-- 图片的替代文本，支持国际化 -->
        :src="captchaImage"  <!-- 图片来源 -->
        :style="captchaStyles"  <!-- 应用计算后的图片样式 -->
        class="relative z-10"
        @click="handleClick"  <!-- 点击图片时触发 handleClick 方法 -->
      />
      <!-- 插槽区域，允许用户添加覆盖在验证码图片上的内容 -->
      <div class="absolute inset-0">
        <slot></slot>
      </div>
    </CardContent>
    <!-- 卡片页脚 -->
    <CardFooter class="mt-2 flex justify-between p-0">
      <slot name="footer"></slot>
    </CardFooter>
  </Card>
</template>
