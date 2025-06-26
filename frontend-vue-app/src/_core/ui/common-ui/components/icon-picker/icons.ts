import type { Recordable } from '@/_core/types';

/**
 * ICONS_MAP 用于存储已获取的图标数据，避免重复请求
 * 在不刷新页面的情况下，相同的图标集不会重复请求远程接口
 */
export const ICONS_MAP: Recordable<string[]> = {};

interface IconifyResponse {
  prefix: string; // 图标集的前缀（唯一标识）
  total: number; // 图标总数
  title: string; // 图标集的标题
  uncategorized?: string[]; // 未分类的图标列表
  categories?: Recordable<string[]>; // 按类别组织的图标列表
  aliases?: Recordable<string>; // 图标别名
}

/**
 * 记录当前正在请求的图标集，避免同一时间多个组件重复请求同一个图标集
 * 当多个图标选择器同时请求相同的图标集时，所有请求共享同一份结果
 */
const PENDING_REQUESTS: Recordable<Promise<string[]>> = {};

/**
 * 通过 Iconify API 获取指定图标集的所有图标
 * - 如果 ICONS_MAP 中已存在，则直接返回缓存数据
 * - 如果 PENDING_REQUESTS 中已有相同的请求，则等待该请求完成并返回结果
 * - 否则，发起新的请求获取图标数据，并缓存结果
 * 
 * @param prefix 图标集的名称（前缀）
 * @returns 该图标集下所有的图标名称列表
 */
export async function fetchIconsData(prefix: string): Promise<string[]> {
  // 如果图标集已缓存，则直接返回
  if (Reflect.has(ICONS_MAP, prefix) && ICONS_MAP[prefix]) {
    return ICONS_MAP[prefix];
  }

  // 如果该图标集请求已经在进行中，则等待该请求完成
  if (Reflect.has(PENDING_REQUESTS, prefix) && PENDING_REQUESTS[prefix]) {
    return PENDING_REQUESTS[prefix];
  }

  // 开始请求图标数据，并存入 PENDING_REQUESTS 防止重复请求
  PENDING_REQUESTS[prefix] = (async () => {
    try {
      // 设置请求超时时间 10 秒，避免请求卡死
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1000 * 10);

      // 发送请求获取图标数据
      const response: IconifyResponse = await fetch(
        `https://api.iconify.design/collection?prefix=${prefix}`,
        { signal: controller.signal },
      ).then((res) => res.json());

      // 请求完成，清除超时计时器
      clearTimeout(timeoutId);

      // 提取未分类的图标列表
      const list = response.uncategorized || [];

      // 如果有分类信息，遍历分类并添加图标
      if (response.categories) {
        for (const category in response.categories) {
          list.push(...(response.categories[category] || []));
        }
      }

      // 格式化图标名称（添加前缀），并缓存到 ICONS_MAP
      ICONS_MAP[prefix] = list.map((v) => `${prefix}:${v}`);
    } catch (error) {
      console.error(`获取图标集 ${prefix} 失败:`, error);
      return [] as string[]; // 请求失败时返回空数组
    }
    return ICONS_MAP[prefix]; // 返回获取到的图标列表
  })();

  return PENDING_REQUESTS[prefix]; // 返回该图标集的请求 Promise
}
