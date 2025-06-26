// 导入 SubMenuProvider 类型，用于对子菜单数据进行类型检查，确保数据符合预期结构
import type { SubMenuProvider } from '../types';

// 从 Vue 框架中导入 computed 和 getCurrentInstance 函数
// computed 用于创建响应式计算属性；getCurrentInstance 用于获取当前组件实例
import { computed, getCurrentInstance } from 'vue';

// 从 utils 工具模块中导入 findComponentUpward 函数，用于在组件树中向上查找指定名称的父组件
import { findComponentUpward } from '../utils';

/**
 * useMenu 函数封装了获取菜单相关信息的逻辑
 * 包括当前组件的父级菜单链路（路径）和最近的父级菜单组件
 */
function useMenu() {
  // 获取当前组件实例，如果获取不到则抛出错误，确保后续操作有组件实例上下文
  const instance = getCurrentInstance();
  if (!instance) {
    throw new Error('instance is required');
  }

  /**
   * @zh_CN 获取所有父级菜单链路
   * parentPaths 是一个计算属性，用于从当前组件向上追溯所有父组件的 path 属性，并以数组形式返回
   */
  const parentPaths = computed(() => {
    // 从当前实例的 parent 属性开始，向上查找
    let parent = instance.parent;
    // 初始化路径数组，将当前组件的 path 添加为初始值
    const paths: string[] = [instance.props.path as string];
    // 循环查找父组件，直到找到类型名称为 'Menu' 的组件为止
    while (parent?.type.name !== 'Menu') {
      // 如果当前父组件存在 path 属性，则将其插入到 paths 数组开头，保持从上到下的顺序
      if (parent?.props.path) {
        paths.unshift(parent.props.path as string);
      }
      // 继续向上查找父组件，如果不存在则赋值为 null 终止循环
      parent = parent?.parent ?? null;
    }

    // 返回包含所有父级菜单路径的数组
    return paths;
  });

  /**
   * parentMenu 是一个计算属性，用于获取当前组件向上查找到的最近的菜单或子菜单组件
   * 利用 findComponentUpward 函数向上查找名称为 'Menu' 或 'SubMenu' 的组件
   */
  const parentMenu = computed(() => {
    return findComponentUpward(instance, ['Menu', 'SubMenu']);
  });

  // 返回包含父级菜单组件和父级路径信息的对象，供外部使用
  return {
    parentMenu,
    parentPaths,
  };
}

/**
 * useMenuStyle 函数用于生成子菜单的样式对象
 * 根据传入的子菜单数据（menu）计算出菜单的层级样式
 *
 * @param menu - 可选参数，类型为 SubMenuProvider，用于提供子菜单的相关数据
 */
function useMenuStyle(menu?: SubMenuProvider) {
  // 创建一个计算属性 subMenuStyle，该属性返回一个包含 CSS 自定义属性的对象
  // '--menu-level' 用于表示菜单的层级，通过 menu 对象中的 level 属性计算得出
  const subMenuStyle = computed(() => {
    return {
      '--menu-level': menu ? (menu?.level ?? 0 + 1) : 0,
    };
  });
  // 返回生成的样式对象
  return subMenuStyle;
}

// 导出 useMenu 和 useMenuStyle 函数，供其他模块或组件使用
export { useMenu, useMenuStyle };
