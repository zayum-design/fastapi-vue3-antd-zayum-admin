import type { RouteRecordRaw } from 'vue-router';
// 引入vue-router中的RouteRecordRaw类型，用于描述单个路由记录的结构

import { filterTree, mapTree } from '@/_core/shared/utils';
// 引入工具函数filterTree和mapTree，这两个函数分别用于对树形数据结构进行递归过滤和递归映射处理

/**
 * 动态生成路由 - 前端方式
 * 此函数根据用户角色动态生成符合权限要求的路由表。
 * 
 * 参数说明：
 * @param routes - 初始的路由表，包含所有路由记录，可能存在嵌套路由结构
 * @param roles - 当前用户的角色数组，根据这些角色判断用户是否拥有访问特定路由的权限
 * @param forbiddenComponent - 可选参数，当用户无权限访问某些路由时，用此组件替换原组件，通常用于展示403页面
 * 
 * 返回值：
 * @returns Promise<RouteRecordRaw[]> - 返回经过权限过滤和组件替换处理后的路由表
 */
async function generateRoutesByFrontend(
  routes: RouteRecordRaw[],
  roles: string[],
  forbiddenComponent?: RouteRecordRaw['component'],
): Promise<RouteRecordRaw[]> {
  // 根据用户角色过滤路由表
  // 使用filterTree函数递归遍历整个路由树，针对每个路由调用hasAuthority函数判断是否具有访问权限
  const finalRoutes = filterTree(routes, (route) => {
    return hasAuthority(route, roles);
  });

  // 如果没有传入forbiddenComponent，则直接返回过滤后的路由表
  if (!forbiddenComponent) {
    return finalRoutes;
  }

  // 如果传入了forbiddenComponent，则需要处理那些设置了菜单中可见但访问受限的路由
  // 使用mapTree函数递归遍历过滤后的路由树，对每个节点判断是否设置了菜单中可见但禁止访问的标志
  // 如果满足条件，则将该路由的组件替换为forbiddenComponent（例如403页面组件）
  return mapTree(finalRoutes, (route) => {
    if (menuHasVisibleWithForbidden(route)) {
      route.component = forbiddenComponent;
    }
    return route;
  });
}

/**
 * 判断路由是否有权限访问
 * 此函数用于检测当前用户是否具备访问某个路由的权限。
 * 
 * 判断逻辑：
 * 1. 如果路由meta中没有配置authority字段，则默认允许访问；
 * 2. 如果配置了authority字段，则检查用户的角色数组中是否存在与之匹配的角色；
 * 3. 如果用户不具备直接访问权限，但该路由配置为“菜单中可见且禁止访问”（即设置了menuVisibleWithForbidden），则也允许显示该路由（实际访问时可能跳转到403页面）。
 * 
 * 参数说明：
 * @param route - 单个路由记录对象，包含路由的各种元数据
 * @param access - 用户角色数组，用于与路由所要求的权限进行匹配
 * 
 * 返回值：
 * @returns boolean - 返回true表示用户有访问权限或路由允许菜单中显示，返回false则表示用户无权访问该路由
 */
function hasAuthority(route: RouteRecordRaw, access: string[]) {
  // 从路由的meta字段中获取authority属性，
  // authority通常为字符串数组，定义了允许访问该路由的角色列表
  const authority = route.meta?.authority;
  
  // 如果未设置authority，表示该路由不需要特殊权限，故默认允许访问
  if (!authority) {
    return true;
  }
  
  // 检查用户角色数组中是否存在至少一个角色包含在authority中
  const canAccess = access.some((value) => authority.includes(value));

  // 返回结果：
  // 如果用户具有访问权限，则直接返回true；
  // 如果用户没有权限，但路由设置了“菜单中可见且禁止访问”的标志，也返回true（因为可能仅用于菜单显示，实际访问会重定向到403页面）
  return canAccess || (!canAccess && menuHasVisibleWithForbidden(route));
}

/**
 * 判断路由是否在菜单中显示，但实际访问时会被重定向到403页面
 * 此函数主要用于检测那些需要在侧边菜单中显示，但用户实际点击后由于权限不足而无法正常访问的路由。
 * 
 * 判断依据：
 * 1. 路由meta中必须存在authority字段，表明该路由是需要权限控制的；
 * 2. 同时meta中必须存在menuVisibleWithForbidden属性，并且其值为true，表示该路由允许在菜单中显示但访问受限。
 * 
 * 参数说明：
 * @param route - 单个路由记录对象
 * 
 * 返回值：
 * @returns boolean - 返回true表示该路由应在菜单中显示但实际访问时会重定向到403页面，返回false则表示正常显示或完全隐藏
 */
function menuHasVisibleWithForbidden(route: RouteRecordRaw) {
  // 利用Reflect.has检查route.meta对象中是否存在menuVisibleWithForbidden属性
  // 同时确保authority属性存在且menuVisibleWithForbidden的值为真
  return (
    !!route.meta?.authority &&
    Reflect.has(route.meta || {}, 'menuVisibleWithForbidden') &&
    !!route.meta?.menuVisibleWithForbidden
  );
}

// 导出生成路由和权限判断的函数，以便在其他模块中使用
export { generateRoutesByFrontend, hasAuthority };
