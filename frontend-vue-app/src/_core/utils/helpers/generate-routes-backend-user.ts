// 引入 vue-router 的类型定义
import type { RouteRecordRaw } from 'vue-router';

// 引入自定义的类型定义
import type {
  ComponentRecordType,
  GenerateMenuAndRoutesOptions,
  RouteRecordStringComponent,
} from '@/_core/typings';

// 引入工具函数 mapTree
import { mapTree } from '@/_core/shared/utils';

import { USER_ROUTE_PREFIX } from '@/constants';

/**
 * 动态生成路由 - 后端方式（用户端专用）
 * 
 * 该函数用于通过后端返回的菜单数据生成前端应用的路由配置（用户端）
 */
async function generateRoutesByBackendUser(
  options: GenerateMenuAndRoutesOptions,
): Promise<RouteRecordRaw[]> {
  const { fetchMenuListAsync, layoutMap = {}, pageMap = {} } = options;

  try {
    const menuRoutes = await fetchMenuListAsync?.();
    if (!menuRoutes) {
      return [];
    }

    const normalizePageMap: ComponentRecordType = {};

    for (const [key, value] of Object.entries(pageMap)) {
      normalizePageMap[normalizeViewPath(key)] = value;
    }
    
    // 调试输出可用的组件
    console.log('[User Routes] Raw pageMap keys (first 10):', 
      Object.keys(pageMap).slice(0, 10)
    );
    console.log('[User Routes] Normalized pageMap keys (first 10):', 
      Object.keys(normalizePageMap).slice(0, 10)
    );

    const routes = convertRoutes(menuRoutes, layoutMap, normalizePageMap);

    return routes;
  } catch (error) {
    console.error(error);
    return [];
  }
}

/**
 * 转换路由数据（用户端专用）
 *
 * 主要逻辑：
 * 1. 遍历所有路由节点。
 * 2. 检查路由节点是否包含有效的 name 属性
 * 3. 根据节点中的 component 属性判断布局组件和页面组件
 * 4. 为路由路径添加 USER_ROUTE_PREFIX 前缀（如果缺失）
 */
function convertRoutes(
  routes: RouteRecordStringComponent[],
  layoutMap: ComponentRecordType,
  pageMap: ComponentRecordType,
): RouteRecordRaw[] {
  return mapTree(routes, (node) => {
    const route = node as unknown as RouteRecordRaw;
    const { component, name, path } = node;

    if (!name) {
      console.error('route name is required', route);
    }

    // 处理路由路径：后端已返回 /user/xxx 格式，直接使用
    if (path) {
      route.path = path.startsWith('/') ? path : `/${path}`;
    }

    // 处理布局组件和页面组件
    if (component && layoutMap[component]) {
      route.component = layoutMap[component];
    } else if (component) {
      const normalizePath = normalizeViewPath(component);
      const componentKey = normalizePath.endsWith('.vue')
        ? normalizePath
        : `${normalizePath}.vue`;
      
      // 调试输出
      console.log('[User Routes] Looking for component:', {
        original: component,
        normalized: normalizePath,
        key: componentKey,
        availableKeys: Object.keys(pageMap).slice(0, 10),
        found: !!pageMap[componentKey],
      });
      
      route.component = pageMap[componentKey];
      
      if (!route.component) {
        console.error(`[User Routes] Component not found: ${componentKey}`);
      }
    }

    return route;
  });
}

/**
 * 规范化视图组件的路径
 */
function normalizeViewPath(path: string): string {
  const normalizedPath = path.replace(/^(\.\/|\.\.\/)+/, '');

  const viewPath = normalizedPath.startsWith('/')
    ? normalizedPath
    : `/${normalizedPath}`;

  return viewPath.replace(/^\/views/, '');
}

export { generateRoutesByBackendUser };
