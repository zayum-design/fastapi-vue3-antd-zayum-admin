// 引入 vue-router 的类型定义
import type { RouteRecordRaw } from 'vue-router';

// 引入自定义的类型定义，包括组件记录类型、生成菜单和路由的配置选项、字符串形式的路由组件
import type {
  ComponentRecordType,
  GenerateMenuAndRoutesOptions,
  RouteRecordStringComponent,
} from '@/_core/typings';

// 引入工具函数 mapTree，用于对树形结构数据进行遍历和映射转换
import { mapTree } from '@/_core/shared/utils';

/**
 * 动态生成路由 - 后端方式
 * 
 * 该函数用于通过后端返回的菜单数据生成前端应用的路由配置。
 * 主要流程包括：
 * 1. 异步获取菜单数据。
 * 2. 规范化页面组件映射，将页面路径转换成标准格式。
 * 3. 转换菜单数据为 Vue 路由对象，处理布局组件和页面组件的对应关系。
 *
 * @param options - 包含以下属性：
 *    fetchMenuListAsync: 异步获取菜单列表的方法
 *    layoutMap: 布局组件映射对象（key 为组件标识，value 为对应的布局组件）
 *    pageMap: 页面组件映射对象（key 为组件路径，value 为对应的页面组件）
 * @returns Promise，解析为 RouteRecordRaw 数组，代表应用的路由配置
 */
async function generateRoutesByBackend(
  options: GenerateMenuAndRoutesOptions,
): Promise<RouteRecordRaw[]> {
  // 从 options 中解构获取异步获取菜单数据的函数及组件映射，若未传入则默认设置为空对象
  const { fetchMenuListAsync, layoutMap = {}, pageMap = {} } = options;

  try {
    // 调用 fetchMenuListAsync 获取后端返回的菜单路由数据（注意：若 fetchMenuListAsync 为 null或未定义，则不执行调用）
    const menuRoutes = await fetchMenuListAsync?.();
    // 如果没有获取到菜单数据，则返回空数组
    if (!menuRoutes) {
      return [];
    }

    // 创建一个新的对象，用于存储规范化后的页面组件映射
    // 规范化的目的是将页面路径转换为标准格式，便于后续查找对应的组件
    const normalizePageMap: ComponentRecordType = {};

    // 遍历原始的 pageMap，将每个 key（组件路径）经过 normalizeViewPath 规范化后存入 normalizePageMap 中
    for (const [key, value] of Object.entries(pageMap)) {
      normalizePageMap[normalizeViewPath(key)] = value;
    }

    // 使用转换函数 convertRoutes 将后端返回的菜单数据转换为 Vue 路由配置对象数组
    // 此函数会处理布局组件和普通页面组件的对应关系
    const routes = convertRoutes(menuRoutes, layoutMap, normalizePageMap);

    // 返回生成的路由配置数组
    return routes;
  } catch (error) {
    // 捕获并输出错误信息，确保错误可被调试和跟踪
    console.error(error);
    // 发生错误时返回空数组，避免程序中断
    return [];
  }
}

/**
 * 转换路由数据，将后端返回的菜单路由数据转换为符合 Vue 路由配置要求的对象数组
 *
 * 主要逻辑：
 * 1. 遍历所有路由节点。
 * 2. 检查路由节点是否包含有效的 name 属性，若缺失则打印错误信息。
 * 3. 根据节点中的 component 属性判断：
 *    - 若 component 在 layoutMap 中存在，则替换为对应的布局组件；
 *    - 否则，视为普通页面组件，根据规范化的路径从 pageMap 中查找对应组件。
 *
 * @param routes - 后端返回的字符串形式的路由组件数组
 * @param layoutMap - 布局组件映射对象，用于将路由中的 component 转换为实际布局组件
 * @param pageMap - 经过规范化的页面组件映射对象
 * @returns 转换后的 RouteRecordRaw 数组，符合 Vue 路由配置要求
 */
function convertRoutes(
  routes: RouteRecordStringComponent[],
  layoutMap: ComponentRecordType,
  pageMap: ComponentRecordType,
): RouteRecordRaw[] {
  // 使用 mapTree 遍历树形结构数据，对每个节点执行转换操作
  return mapTree(routes, (node) => {
    // 将当前节点强制转换为 RouteRecordRaw 类型，以便后续赋值操作
    const route = node as unknown as RouteRecordRaw;
    // 从节点中解构出 component 和 name 属性
    const { component, name } = node;

    // 如果路由节点缺少必需的 name 属性，打印错误信息，提示开发者该路由配置存在问题
    if (!name) {
      console.error('route name is required', route);
    }

    // 如果节点的 component 属性存在，并且在布局组件映射 layoutMap 中存在对应的组件
    if (component && layoutMap[component]) {
      // 将路由组件替换为 layoutMap 中对应的布局组件
      route.component = layoutMap[component];
    // 如果节点的 component 属性存在但不在 layoutMap 中
    } else if (component) {
      // 使用 normalizeViewPath 对组件路径进行规范化
      const normalizePath = normalizeViewPath(component);
      // 从 pageMap 中查找对应的页面组件，确保路径以 .vue 结尾
      route.component =
        pageMap[
          normalizePath.endsWith('.vue')
            ? normalizePath
            : `${normalizePath}.vue`
        ];
    }

    // 返回转换后的路由对象
    return route;
  });
}

/**
 * 规范化视图组件的路径
 *
 * 该函数主要完成以下工作：
 * 1. 移除路径中的相对路径前缀，如 "./" 或 "../"。
 * 2. 确保返回的路径以 '/' 开头。
 * 3. 针对项目中使用的目录结构，移除路径开头的 '/views' 部分。
 *
 * @param path - 原始的组件路径
 * @returns 规范化后的组件路径，符合项目约定的格式
 */
function normalizeViewPath(path: string): string {
  // 使用正则表达式移除路径中的相对路径前缀（例如 './' 或 '../'）
  const normalizedPath = path.replace(/^(\.\/|\.\.\/)+/, '');

  // 如果规范化后的路径不以 '/' 开头，则自动补充
  const viewPath = normalizedPath.startsWith('/')
    ? normalizedPath
    : `/${normalizedPath}`;

  // 根据项目的目录结构，移除路径中开头的 '/views' 部分，降低耦合性
  return viewPath.replace(/^\/views/, '');
}

// 导出 generateRoutesByBackend 函数，以便其他模块可以调用
export { generateRoutesByBackend };
