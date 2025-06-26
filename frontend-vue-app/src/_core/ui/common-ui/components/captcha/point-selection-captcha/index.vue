<script setup lang="ts">
// 引入类型定义
import type { CaptchaPoint, PointSelectionCaptchaProps } from '../types';

// 引入图标和国际化工具
import { RotateCw } from '@/_core/ui/icons/icons';
import { $t } from '@/locales';

// 引入UI组件
import { ZayumButton, ZayumIconButton } from '@/_core/ui/common-ui/shadcn-ui';

// 引入自定义Hook
import { useCaptchaPoints } from '../hooks/useCaptchaPoints';
import CaptchaCard from './point-selection-captcha-card.vue';

// 定义组件属性，并设置默认值
const props = withDefaults(defineProps<PointSelectionCaptchaProps>(), {
  height: '220px',
  hintImage: '',
  hintText: '',
  paddingX: '12px',
  paddingY: '16px',
  showConfirm: false,
  title: '',
  width: '300px',
});

// 定义组件事件
const emit = defineEmits<{
  click: [CaptchaPoint];
  confirm: [Array<CaptchaPoint>, clear: () => void];
  refresh: [];
}>();

// 使用自定义Hook管理验证码点的状态
const { addPoint, clearPoints, points } = useCaptchaPoints();

// 如果没有提示图片或提示文本，则发出警告
if (!props.hintImage && !props.hintText) {
  console.warn('At least one of hint image or hint text must be provided');
}

// 定义点的偏移量
const POINT_OFFSET = 11;

// 获取元素在页面中的位置
function getElementPosition(element: HTMLElement) {
  const rect = element.getBoundingClientRect();
  return {
    x: rect.left + window.scrollX,
    y: rect.top + window.scrollY,
  };
}

// 处理点击事件
function handleClick(e: MouseEvent) {
  try {
    const dom = e.currentTarget as HTMLElement;
    if (!dom) throw new Error('Element not found');

    // 获取元素的位置
    const { x: domX, y: domY } = getElementPosition(dom);

    // 获取鼠标点击的位置
    const mouseX = e.clientX + window.scrollX;
    const mouseY = e.clientY + window.scrollY;

    // 校验鼠标坐标是否为数字
    if (typeof mouseX !== 'number' || typeof mouseY !== 'number') {
      throw new TypeError('Mouse coordinates not found');
    }

    // 计算点击位置相对于元素的位置
    const xPos = mouseX - domX;
    const yPos = mouseY - domY;

    const rect = dom.getBoundingClientRect();

    // 校验点击位置是否在元素范围内
    if (xPos < 0 || yPos < 0 || xPos > rect.width || yPos > rect.height) {
      console.warn('Click position is out of the valid range');
      return;
    }

    // 取整点击位置
    const x = Math.ceil(xPos);
    const y = Math.ceil(yPos);

    // 创建点对象
    const point = {
      i: points.length,
      t: Date.now(),
      x,
      y,
    };

    // 添加点到状态中
    addPoint(point);

    // 触发点击事件
    emit('click', point);
    e.stopPropagation();
    e.preventDefault();
  } catch (error) {
    console.error('Error in handleClick:', error);
  }
}

// 清空所有点
function clear() {
  try {
    clearPoints();
  } catch (error) {
    console.error('Error in clear:', error);
  }
}

// 处理刷新事件
function handleRefresh() {
  try {
    clear();
    emit('refresh');
  } catch (error) {
    console.error('Error in handleRefresh:', error);
  }
}

// 处理确认事件
function handleConfirm() {
  if (!props.showConfirm) return;
  try {
    emit('confirm', points, clear);
  } catch (error) {
    console.error('Error in handleConfirm:', error);
  }
}
</script>

<template>
  <!-- 验证码卡片组件 -->
  <CaptchaCard
    :captcha-image="captchaImage"
    :height="height"
    :padding-x="paddingX"
    :padding-y="paddingY"
    :title="title"
    :width="width"
    @click="handleClick"
  >
    <!-- 标题插槽 -->
    <template #title>
      <slot name="title">{{ $t('ui.captcha.title') }}</slot>
    </template>

    <!-- 额外内容插槽 -->
    <template #extra>
      <!-- 刷新按钮 -->
      <ZayumIconButton
        :aria-label="$t('ui.captcha.refreshAriaLabel')"
        class="ml-1"
        @click="handleRefresh"
      >
        <RotateCw class="size-5" />
      </ZayumIconButton>
      <!-- 确认按钮 -->
      <ZayumButton
        v-if="showConfirm"
        :aria-label="$t('ui.captcha.confirmAriaLabel')"
        class="ml-2"
        size="sm"
        @click="handleConfirm"
      >
        {{ $t('ui.captcha.confirm') }}
      </ZayumButton>
    </template>

    <!-- 显示点击的点 -->
    <div
      v-for="(point, index) in points"
      :key="index"
      :aria-label="$t('ui.captcha.pointAriaLabel') + (index + 1)"
      :style="{
        top: `${point.y - POINT_OFFSET}px`,
        left: `${point.x - POINT_OFFSET}px`,
      }"
      class="bg-primary text-primary-50 border-primary-50 absolute z-20 flex h-5 w-5 cursor-default items-center justify-center rounded-full border-2"
      role="button"
      tabindex="0"
    >
      {{ index + 1 }}
    </div>

    <!-- 底部插槽 -->
    <template #footer>
      <!-- 提示图片 -->
      <img
        v-if="hintImage"
        :alt="$t('ui.captcha.alt')"
        :src="hintImage"
        class="border-border h-10 w-full rounded border"
      />
      <!-- 提示文本 -->
      <div
        v-else-if="hintText"
        class="border-border flex-center h-10 w-full rounded border"
      >
        {{ `${$t('ui.captcha.clickInOrder')}` + `【${hintText}】` }}
      </div>
    </template>
  </CaptchaCard>
</template>