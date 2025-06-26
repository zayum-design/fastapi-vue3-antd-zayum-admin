// 引入 MenuRecordRaw 类型，用于定义菜单记录的数据结构
import type { MenuRecordRaw } from '@/_core/typings';

/**
 * 通过递归遍历菜单列表，查找匹配指定路径的菜单项
 * @param list - 菜单记录数组，可能包含嵌套的子菜单
 * @param path - 需要查找的菜单路径
 * @returns 返回匹配路径的菜单记录，如果未找到则返回 null
 */
function findMenuByPath(
  list: MenuRecordRaw[],
  path?: string,
): MenuRecordRaw | null {
  // 遍历当前菜单列表中的每个菜单项
  for (const menu of list) {
    // 如果当前菜单的路径与目标路径相同，则直接返回该菜单项
    if (menu.path === path) {
      return menu;
    }
    // 如果当前菜单有子菜单，则递归调用 findMenuByPath 查找子菜单中是否存在匹配的路径
    const findMenu = menu.children && findMenuByPath(menu.children, path);
    // 如果在子菜单中找到了匹配的菜单项，则返回该菜单项
    if (findMenu) {
      return findMenu;
    }
  }
  // 遍历完整个列表后未找到匹配的菜单，返回 null
  return null;
}

/**
 * 查找根菜单
 * 根据指定路径，先找到对应的菜单项，然后根据父级索引（level）返回对应的根菜单项
 *
 * @param menus - 包含所有菜单记录的数组
 * @param path - 需要查找的菜单路径
 * @param level - 用于确定父级索引的位置，默认为 0，即直接取第一个父级路径
 * @returns 返回一个对象，包含查找到的菜单项 (findMenu)、对应的根菜单项 (rootMenu) 以及根菜单的路径 (rootMenuPath)
 */
function findRootMenuByPath(menus: MenuRecordRaw[], path?: string, level = 0) {
  // 调用 findMenuByPath 函数，查找菜单列表中匹配指定路径的菜单项
  const findMenu = findMenuByPath(menus, path);
  // 从找到的菜单项中获取其父级路径数组，并取第 level 个元素作为根菜单路径
  const rootMenuPath = findMenu?.parents?.[level];
  // 根据根菜单路径，从顶级菜单列表中查找对应的根菜单项
  const rootMenu = rootMenuPath
    ? menus.find((item) => item.path === rootMenuPath)
    : undefined;
  // 返回一个对象，包含找到的菜单项、根菜单项以及根菜单的路径
  return {
    findMenu,
    rootMenu,
    rootMenuPath,
  };
}

// 导出这两个函数供其他模块使用
export { findMenuByPath, findRootMenuByPath };
