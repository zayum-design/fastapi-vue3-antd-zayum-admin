/**
 * @copy https://github.com/element-plus/element-plus/blob/dev/packages/hooks/use-draggable/index.ts
 * 调整部分细节
 *
 * 本模块实现了一个用于模态框拖拽的 hook，
 * 允许用户通过鼠标拖拽来移动目标元素的位置，
 * 并确保拖拽移动的范围限制在当前视口内。
 */

import type { ComputedRef, Ref } from 'vue';

// 导入 Vue 的生命周期钩子和响应式 API
import { onBeforeUnmount, onMounted, reactive, ref, watchEffect } from 'vue';

// 导入 VueUse 的辅助函数，用于解析 ref 或直接传入的 DOM 元素
import { unrefElement } from '@vueuse/core';

/**
 * useModalDraggable - 用于实现模态框拖拽功能的自定义 Hook
 *
 * @param targetRef 拖拽目标元素的 Ref 对象（被拖拽的元素）
 * @param dragRef 拖拽触发区域的 Ref 对象（用于监听鼠标按下事件的区域）
 * @param draggable 一个计算属性，指示是否允许拖拽操作
 *
 * 返回值包含：
 * - dragging: 表示当前是否处于拖拽状态的 Ref 对象
 * - resetPosition: 重置拖拽位置的函数，将元素恢复到初始位置
 * - transform: 响应式对象，存储当前拖拽的偏移量（水平 offsetX 和垂直 offsetY）
 */
export function useModalDraggable(
  targetRef: Ref<HTMLElement | undefined>,
  dragRef: Ref<HTMLElement | undefined>,
  draggable: ComputedRef<boolean>,
) {
  // 定义响应式对象 transform，用于存储拖拽过程中的偏移量
  const transform = reactive({
    offsetX: 0,
    offsetY: 0,
  });

  // dragging 表示当前是否正在拖拽，通过 ref 保存布尔值
  const dragging = ref(false);

  // onMousedown 事件处理函数：当鼠标在拖拽区域按下时触发，开始记录拖拽初始位置
  const onMousedown = (e: MouseEvent) => {
    // 记录鼠标按下时的 X 和 Y 坐标
    const downX = e.clientX;
    const downY = e.clientY;

    // 如果目标元素不存在，则不进行任何操作
    if (!targetRef.value) {
      return;
    }

    // 获取目标元素在视口中的位置信息和尺寸
    const targetRect = targetRef.value.getBoundingClientRect();

    // 从 transform 中获取当前偏移量
    const { offsetX, offsetY } = transform;
    // 获取目标元素的左上角坐标
    const targetLeft = targetRect.left;
    const targetTop = targetRect.top;
    // 获取目标元素的宽度和高度
    const targetWidth = targetRect.width;
    const targetHeight = targetRect.height;
    // 获取文档根元素，用于计算视口宽高
    const docElement = document.documentElement;
    const clientWidth = docElement.clientWidth;
    const clientHeight = docElement.clientHeight;

    // 计算拖拽过程中允许的最小和最大水平偏移量（确保元素不会拖出视口）
    const minLeft = -targetLeft + offsetX;
    const minTop = -targetTop + offsetY;
    const maxLeft = clientWidth - targetLeft - targetWidth + offsetX;
    const maxTop = clientHeight - targetTop - targetHeight + offsetY;

    // onMousemove 事件处理函数：当鼠标移动时，更新目标元素的位置
    const onMousemove = (e: MouseEvent) => {
      // 根据鼠标移动距离和初始偏移量计算新的位置
      let moveX = offsetX + e.clientX - downX;
      let moveY = offsetY + e.clientY - downY;

      // 将新的位置限定在允许的范围内，防止拖拽出界
      moveX = Math.min(Math.max(moveX, minLeft), maxLeft);
      moveY = Math.min(Math.max(moveY, minTop), maxTop);

      // 更新 transform 中的偏移量
      transform.offsetX = moveX;
      transform.offsetY = moveY;

      // 如果目标元素存在，则更新其 CSS transform 属性，实现视觉上的移动效果
      if (targetRef.value) {
        targetRef.value.style.transform = `translate(${moveX}px, ${moveY}px)`;
        // 标记当前处于拖拽状态
        dragging.value = true;
      }
    };

    // onMouseup 事件处理函数：当鼠标松开时，结束拖拽操作
    const onMouseup = () => {
      // 取消拖拽状态
      dragging.value = false;
      // 移除鼠标移动和鼠标松开事件监听，防止内存泄露
      document.removeEventListener('mousemove', onMousemove);
      document.removeEventListener('mouseup', onMouseup);
    };

    // 为 document 添加鼠标移动和鼠标松开事件监听，开始跟踪拖拽过程
    document.addEventListener('mousemove', onMousemove);
    document.addEventListener('mouseup', onMouseup);
  };

  // onDraggable 函数：为拖拽触发区域绑定 mousedown 事件，实现拖拽启动
  const onDraggable = () => {
    // 使用 unrefElement 解析 dragRef，获取实际的 DOM 元素
    const dragDom = unrefElement(dragRef);
    // 如果拖拽触发元素和目标元素都存在，则为拖拽触发元素添加 mousedown 事件监听
    if (dragDom && targetRef.value) {
      dragDom.addEventListener('mousedown', onMousedown);
    }
  };

  // offDraggable 函数：移除拖拽触发区域的 mousedown 事件监听，停止拖拽功能
  const offDraggable = () => {
    // 使用 unrefElement 解析 dragRef，获取实际的 DOM 元素
    const dragDom = unrefElement(dragRef);
    // 如果拖拽触发元素和目标元素都存在，则移除绑定的 mousedown 事件监听
    if (dragDom && targetRef.value) {
      dragDom.removeEventListener('mousedown', onMousedown);
    }
  };

  // resetPosition 函数：重置拖拽状态，将偏移量恢复到初始状态，并移除目标元素的 transform 样式
  const resetPosition = () => {
    transform.offsetX = 0;
    transform.offsetY = 0;

    // 解析目标元素，并将其 transform 样式重置为 'none'
    const target = unrefElement(targetRef);
    if (target) {
      target.style.transform = 'none';
    }
  };

  // 在组件挂载时，使用 watchEffect 监听 draggable 属性的变化，动态绑定或解绑拖拽事件
  onMounted(() => {
    watchEffect(() => {
      // 当 draggable 为 true 时，启用拖拽功能；否则，禁用拖拽功能
      if (draggable.value) {
        onDraggable();
      } else {
        offDraggable();
      }
    });
  });

  // 在组件卸载前，移除拖拽事件监听，确保资源被正确释放
  onBeforeUnmount(() => {
    offDraggable();
  });

  // 返回当前拖拽状态、重置位置函数以及当前的偏移量，供外部组件使用
  return {
    dragging,
    resetPosition,
    transform,
  };
}
