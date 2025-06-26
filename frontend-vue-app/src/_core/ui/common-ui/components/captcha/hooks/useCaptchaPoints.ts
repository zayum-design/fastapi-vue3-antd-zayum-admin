// 导入 CaptchaPoint 类型
import type { CaptchaPoint } from '../types';

// 导入 Vue 的 reactive 函数，用于创建响应式对象
import { reactive } from 'vue';

// 定义一个名为 useCaptchaPoints 的函数
export function useCaptchaPoints() {
  // 创建一个响应式数组 points，用于存储 CaptchaPoint 类型的点
  const points = reactive<CaptchaPoint[]>([]);

  // 定义一个函数 addPoint，用于向 points 数组中添加一个点
  function addPoint(point: CaptchaPoint) {
    points.push(point);
  }

  // 定义一个函数 clearPoints，用于清空 points 数组中的所有点
  function clearPoints() {
    points.splice(0, points.length);
  }

  // 返回一个对象，包含 addPoint、clearPoints 函数和 points 数组
  return {
    addPoint,
    clearPoints,
    points,
  };
}