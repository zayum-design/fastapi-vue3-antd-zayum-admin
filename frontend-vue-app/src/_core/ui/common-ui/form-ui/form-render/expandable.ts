import type { FormRenderProps } from '../types';
import { computed, nextTick, onMounted, ref, useTemplateRef, watch } from 'vue';
import { breakpointsTailwind, useBreakpoints } from '@vueuse/core';

/**
 * 处理表单项的动态行数计算
 * @param props 表单渲染属性
 * @returns 计算结果
 */
export function useExpandable(props: FormRenderProps) {
  // 获取表单容器的 DOM 引用
  const wrapperRef = useTemplateRef<HTMLElement>('wrapperRef');
  
  // 记录每一行的表单项数量
  const rowMapping = ref<Record<number, number>>({});
  
  // 标记是否已经计算过
  const isCalculated = ref(false);

  // 监听 TailwindCSS 的断点
  const breakpoints = useBreakpoints(breakpointsTailwind);

  // 计算可以显示的表单项数量
  const keepFormItemIndex = computed(() => {
    const rows = props.collapsedRows ?? 1; // 获取折叠后保留的行数
    const mapping = rowMapping.value;
    let maxItem = 0;

    for (let index = 1; index <= rows; index++) {
      maxItem += mapping?.[index] ?? 0;
    }
    
    return maxItem - 1 || 1; // 保证至少留一个表单项
  });

  // 监听表单折叠按钮、屏幕断点变化、表单项数量变化，重新计算行数
  watch(
    [
      () => props.showCollapseButton,
      () => breakpoints.active().value,
      () => props.schema?.length,
    ],
    async ([val]) => {
      if (val) {
        await nextTick();
        rowMapping.value = {};
        isCalculated.value = false;
        await calculateRowMapping();
      }
    },
  );

  /**
   * 计算表单项的行数映射
   */
  async function calculateRowMapping() {
    if (!props.showCollapseButton) {
      return;
    }

    await nextTick();
    if (!wrapperRef.value) {
      return;
    }

    const formItems = [...wrapperRef.value.children];
    const container = wrapperRef.value;
    const containerStyles = window.getComputedStyle(container);

    // 获取 grid 布局的行高信息
    const rowHeights = containerStyles
      .getPropertyValue('grid-template-rows')
      .split(' ');

    // 获取容器的位置信息
    const containerRect = container.getBoundingClientRect();

    formItems.forEach((el) => {
      const itemRect = el.getBoundingClientRect();

      // 计算该表单项所在的行
      const itemTop = itemRect.top - containerRect.top;
      let rowStart = 0;
      let cumulativeHeight = 0;

      for (const [i, rowHeight] of rowHeights.entries()) {
        cumulativeHeight += Number.parseFloat(rowHeight);
        if (itemTop < cumulativeHeight) {
          rowStart = i + 1;
          break;
        }
      }

      // 只计算在可见行范围内的表单项
      if (rowStart > (props?.collapsedRows ?? 1)) {
        return;
      }

      // 记录当前行的表单项数量
      rowMapping.value[rowStart] = (rowMapping.value[rowStart] ?? 0) + 1;
      isCalculated.value = true;
    });
  }

  // 组件挂载时计算行数
  onMounted(() => {
    calculateRowMapping();
  });

  return { isCalculated, keepFormItemIndex, wrapperRef };
}
