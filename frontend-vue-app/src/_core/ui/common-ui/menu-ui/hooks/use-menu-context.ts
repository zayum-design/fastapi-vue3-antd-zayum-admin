// 导入 MenuProvider 和 SubMenuProvider 类型，用于类型检查和代码提示，确保传入的数据符合预期结构
import type { MenuProvider, SubMenuProvider } from '../types';

// 从 Vue 框架中导入 getCurrentInstance、inject、provide 三个函数
// getCurrentInstance 用于获取当前组件实例；inject 和 provide 用于实现依赖注入
import { getCurrentInstance, inject, provide } from 'vue';

// 从 utils 工具文件中导入 findComponentUpward 函数，用于在组件树中向上查找指定名称的父组件
import { findComponentUpward } from '../utils';

// 创建一个唯一的 Symbol 作为菜单上下文的 key，确保在依赖注入过程中不会与其他 key 冲突
const menuContextKey = Symbol('menuContext');

/**
 * @zh_CN Provide menu context
 * 创建并提供菜单上下文数据
 *
 * @param injectMenuData - 类型为 MenuProvider 的菜单数据，该数据将被注入到 Vue 的依赖注入系统中
 */
function createMenuContext(injectMenuData: MenuProvider) {
  // 使用 Vue 的 provide 函数，将 injectMenuData 数据注入到当前组件上下文中
  // 该数据可以在子组件中通过 inject(menuContextKey) 进行访问
  provide(menuContextKey, injectMenuData);
}

/**
 * @zh_CN Provide menu context
 * 创建并提供子菜单上下文数据
 *
 * @param injectSubMenuData - 类型为 SubMenuProvider 的子菜单数据，将在当前组件中通过依赖注入提供给后代组件使用
 */
function createSubMenuContext(injectSubMenuData: SubMenuProvider) {
  // 获取当前组件实例，用于生成唯一的 key
  const instance = getCurrentInstance();

  // 使用当前组件的 uid 生成唯一的 key，将子菜单数据注入到依赖注入系统中
  // 这样可以确保同一父组件下不同子组件之间的数据不会发生冲突
  provide(`subMenu:${instance?.uid}`, injectSubMenuData);
}

/**
 * @zh_CN Inject menu context
 * 注入并获取菜单上下文数据
 *
 * @returns 返回提供的 MenuProvider 数据，供当前组件使用
 */
function useMenuContext() {
  // 获取当前组件实例，用于确保在组件上下文中进行依赖注入
  const instance = getCurrentInstance();
  // 如果当前组件实例不存在，则抛出错误，避免后续代码出现无法预料的问题
  if (!instance) {
    throw new Error('instance is required');
  }
  // 使用 inject 函数通过之前提供的 menuContextKey 获取菜单上下文数据
  const rootMenu = inject(menuContextKey) as MenuProvider;
  // 返回获取到的菜单数据
  return rootMenu;
}

/**
 * @zh_CN Inject menu context
 * 注入并获取子菜单上下文数据
 *
 * @returns 返回提供的 SubMenuProvider 数据，供当前组件使用
 */
function useSubMenuContext() {
  // 获取当前组件实例，确保在组件上下文中进行依赖注入
  const instance = getCurrentInstance();
  // 如果当前组件实例不存在，则抛出错误，提示必须在组件实例中使用此函数
  if (!instance) {
    throw new Error('instance is required');
  }
  // 利用 findComponentUpward 函数从当前组件向上查找最近的名称为 'Menu' 或 'SubMenu' 的父组件
  // 这一步确保子菜单上下文的数据来源于正确的父组件
  const parentMenu = findComponentUpward(instance, ['Menu', 'SubMenu']);
  // 通过父组件的 uid 构造唯一的 key，注入子菜单上下文数据
  const subMenu = inject(`subMenu:${parentMenu?.uid}`) as SubMenuProvider;
  // 返回获取到的子菜单数据
  return subMenu;
}

// 导出所有创建和注入菜单上下文的函数，供其他模块或组件使用
export {
  createMenuContext,
  createSubMenuContext,
  useMenuContext,
  useSubMenuContext,
};
