<script lang="ts" setup>
// 导入 Vue 中的 RendererElement 类型，用于为元素添加类型约束
import type { RendererElement } from 'vue';

// 定义组件选项，设置组件名称为 'CollapseTransition'
defineOptions({
  name: 'CollapseTransition',
});

// 定义一个重置函数，用于在动画结束后将元素的样式还原到初始状态
const reset = (el: RendererElement) => {
  // 清空最大高度设置
  el.style.maxHeight = '';
  // 恢复 overflow 属性为进入动画前存储的原始值
  el.style.overflow = el.dataset.oldOverflow;
  // 恢复上内边距为进入动画前存储的原始值
  el.style.paddingTop = el.dataset.oldPaddingTop;
  // 恢复下内边距为进入动画前存储的原始值
  el.style.paddingBottom = el.dataset.oldPaddingBottom;
};

// 定义过渡动画各阶段的事件处理函数集合
const on = {
  // 当进入动画完成后调用
  afterEnter(el: RendererElement) {
    // 清除最大高度设置，确保元素完全展开
    el.style.maxHeight = '';
    // 恢复 overflow 属性为进入动画前存储的原始值
    el.style.overflow = el.dataset.oldOverflow;
  },

  // 当离开动画完成后调用
  afterLeave(el: RendererElement) {
    // 调用 reset 函数，重置元素的样式
    reset(el);
  },

  // 进入动画开始前调用（在元素显示之前）
  beforeEnter(el: RendererElement) {
    // 如果元素没有 dataset，则初始化为一个空对象
    if (!el.dataset) el.dataset = {};

    // 保存当前的上内边距到 dataset 中，后续用于恢复
    el.dataset.oldPaddingTop = el.style.paddingTop;
    // 保存当前的上外边距到 dataset 中
    el.dataset.oldMarginTop = el.style.marginTop;

    // 保存当前的下内边距到 dataset 中
    el.dataset.oldPaddingBottom = el.style.paddingBottom;
    // 保存当前的下外边距到 dataset 中
    el.dataset.oldMarginBottom = el.style.marginBottom;
    // 如果元素当前设置了高度，则将该高度保存到 dataset 中
    if (el.style.height) el.dataset.elExistsHeight = el.style.height;

    // 将最大高度设置为 0，使元素初始状态下不可见
    el.style.maxHeight = 0;
    // 将上内边距设为 0，以配合收缩动画效果
    el.style.paddingTop = 0;
    // 将上外边距设为 0
    el.style.marginTop = 0;
    // 将下内边距设为 0
    el.style.paddingBottom = 0;
    // 将下外边距设为 0
    el.style.marginBottom = 0;
  },

  // 离开动画开始前调用（在元素开始收缩之前）
  beforeLeave(el: RendererElement) {
    // 如果元素没有 dataset，则初始化为一个空对象
    if (!el.dataset) el.dataset = {};
    // 保存当前的上内边距到 dataset 中
    el.dataset.oldPaddingTop = el.style.paddingTop;
    // 保存当前的上外边距到 dataset 中
    el.dataset.oldMarginTop = el.style.marginTop;
    // 保存当前的下内边距到 dataset 中
    el.dataset.oldPaddingBottom = el.style.paddingBottom;
    // 保存当前的下外边距到 dataset 中
    el.dataset.oldMarginBottom = el.style.marginBottom;
    // 保存当前的 overflow 样式到 dataset 中
    el.dataset.oldOverflow = el.style.overflow;
    // 设置最大高度为元素当前的滚动高度，实现平滑收缩动画
    el.style.maxHeight = `${el.scrollHeight}px`;
    // 将 overflow 设置为 hidden，防止内容溢出
    el.style.overflow = 'hidden';
  },

  // 进入动画进行时调用，使用 requestAnimationFrame 确保动画样式在下一帧生效
  enter(el: RendererElement) {
    requestAnimationFrame(() => {
      // 保存当前的 overflow 样式到 dataset 中
      el.dataset.oldOverflow = el.style.overflow;
      // 如果之前保存了元素的高度，则恢复该高度
      if (el.dataset.elExistsHeight) {
        el.style.maxHeight = el.dataset.elExistsHeight;
      } else if (el.scrollHeight === 0) {
        // 如果元素没有内容高度，则直接设置最大高度为 0
        el.style.maxHeight = 0;
      } else {
        // 否则设置最大高度为元素当前的滚动高度
        el.style.maxHeight = `${el.scrollHeight}px`;
      }

      // 恢复上内边距为进入前存储的原始值
      el.style.paddingTop = el.dataset.oldPaddingTop;
      // 恢复下内边距为进入前存储的原始值
      el.style.paddingBottom = el.dataset.oldPaddingBottom;
      // 恢复上外边距为进入前存储的原始值
      el.style.marginTop = el.dataset.oldMarginTop;
      // 恢复下外边距为进入前存储的原始值
      el.style.marginBottom = el.dataset.oldMarginBottom;
      // 确保 overflow 仍然为 hidden，保持动画效果
      el.style.overflow = 'hidden';
    });
  },

  // 如果进入动画被取消，则调用 reset 函数重置样式
  enterCancelled(el: RendererElement) {
    reset(el);
  },

  // 离开动画进行时调用，用于控制元素的收缩效果
  leave(el: RendererElement) {
    // 如果元素具有滚动高度，则执行收缩操作
    if (el.scrollHeight !== 0) {
      // 将最大高度设置为 0，使元素完全收缩
      el.style.maxHeight = 0;
      // 将上内边距设为 0
      el.style.paddingTop = 0;
      // 将下内边距设为 0
      el.style.paddingBottom = 0;
      // 将上外边距设为 0
      el.style.marginTop = 0;
      // 将下外边距设为 0
      el.style.marginBottom = 0;
    }
  },

  // 如果离开动画被取消，则调用 reset 函数重置样式
  leaveCancelled(el: RendererElement) {
    reset(el);
  },
};
</script>

<template>
  <!-- 使用 transition 组件包裹内容，通过设置 name 属性控制 CSS 过渡类名，
       同时通过 v-on 指令将上面定义的事件处理函数绑定到 transition 组件上，
       实现折叠/展开的动画效果 -->
  <transition name="collapse-transition" v-on="on">
    <slot></slot>
  </transition>
</template>
