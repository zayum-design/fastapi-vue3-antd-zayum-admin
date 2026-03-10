import type { MenuRecordRaw } from '@/_core/types';

import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import { layoutConfig } from '../../layout-config';
import { useUserAccessStore } from '@/stores/user/access';
import { findRootMenuByPath } from '@/_core/utils';

import { useNavigation } from './use-navigation';

function useMixedMenu() {
  const { navigation } = useNavigation();
  const accessStore = useUserAccessStore();
  const route = useRoute();
  const splitSideMenus = ref<MenuRecordRaw[]>([]);
  const rootMenuPath = ref<string>('');
  const mixedRootMenuPath = ref<string>('');
  const mixExtraMenus = ref<MenuRecordRaw[]>([]);
  /** 记录当前顶级菜单下哪个子菜单最后激活 */
  const defaultSubMap = new Map<string, string>();

  const isMixedNav = computed(() => layoutConfig.app.layout === 'mixed-nav');
  const isHeaderMixedNav = computed(() => layoutConfig.app.layout === 'header-mixed-nav');

  const needSplit = computed(
    () =>
      (layoutConfig.navigation.split && isMixedNav.value) ||
      isHeaderMixedNav.value,
  );

  const sidebarVisible = computed(() => {
    const enableSidebar = layoutConfig.sidebar.enable;
    if (needSplit.value) {
      return enableSidebar && splitSideMenus.value.length > 0;
    }
    return enableSidebar;
  });

  // 从 user access store 获取菜单数据
  const menus = computed<MenuRecordRaw[]>(() => accessStore.accessMenus || []);

  /**
   * 头部菜单
   */
  const headerMenus = computed(() => {
    if (!needSplit.value) {
      return menus.value;
    }
    return menus.value.map((item) => {
      return {
        ...item,
        children: [],
      };
    });
  });

  /**
   * 侧边菜单
   */
  const sidebarMenus = computed(() => {
    return needSplit.value ? splitSideMenus.value : menus.value;
  });

  const mixHeaderMenus = computed(() => {
    return isHeaderMixedNav.value ? sidebarMenus.value : headerMenus.value;
  });

  /**
   * 侧边菜单激活路径
   */
  const sidebarActive = computed(() => {
    return (route?.meta?.activePath as string) ?? route.path;
  });

  /**
   * 头部菜单激活路径
   */
  const headerActive = computed(() => {
    if (!needSplit.value) {
      return route.path;
    }
    return rootMenuPath.value;
  });

  /**
   * 菜单点击事件处理
   * @param key 菜单路径
   * @param mode 菜单模式
   */
  const handleMenuSelect = (key: string, mode?: string) => {
    if (!needSplit.value || mode === 'vertical') {
      navigation(key);
      return;
    }

    const rootMenu = menus.value.find((item) => item.path === key);
    rootMenuPath.value = rootMenu?.path ?? '';
    splitSideMenus.value = rootMenu?.children ?? [];
    if (splitSideMenus.value.length === 0) {
      navigation(key);
    } else if (rootMenu && layoutConfig.sidebar.autoActivateChild) {
      navigation(
        defaultSubMap.has(rootMenu.path)
          ? (defaultSubMap.get(rootMenu.path) as string)
          : rootMenu.path,
      );
    }
  };

  /**
   * 侧边菜单展开事件
   * @param key 路由路径
   * @param parentsPath 父级路径
   */
  const handleMenuOpen = (key: string, parentsPath: string[]) => {
    if (parentsPath.length <= 1 && layoutConfig.sidebar.autoActivateChild) {
      navigation(
        defaultSubMap.has(key) ? (defaultSubMap.get(key) as string) : key,
      );
    }
  };

  /**
   * 计算侧边菜单
   * @param path 路由路径
   */
  function calcSideMenus(path: string = route.path) {
    console.log('[calcSideMenus] path:', path);
    console.log('[calcSideMenus] menus:', menus.value.map(m => m.path));
    
    // 先找到当前菜单项
    const currentMenu = menus.value.find((item) => item.path === path);
    console.log('[calcSideMenus] currentMenu:', currentMenu);
    
    // 对于扁平菜单结构（没有层级），直接使用当前菜单
    if (currentMenu) {
      console.log('[calcSideMenus] found currentMenu, setting splitSideMenus to menus.value');
      rootMenuPath.value = currentMenu.path ?? '';
      // 如果有子菜单，显示子菜单；否则显示所有同级菜单
      splitSideMenus.value = currentMenu.children ?? menus.value;
      mixedRootMenuPath.value = currentMenu.path ?? '';
      mixExtraMenus.value = currentMenu.children ?? [];
      console.log('[calcSideMenus] splitSideMenus:', splitSideMenus.value.map(m => m.path));
      return;
    }
    
    // 原有逻辑（用于支持层级菜单）
    console.log('[calcSideMenus] using fallback logic');
    let { rootMenu } = findRootMenuByPath(menus.value, path);
    if (!rootMenu) {
      rootMenu = menus.value.find((item) => item.path === path);
    }
    const result = findRootMenuByPath(rootMenu?.children ?? [], path, 1);
    mixedRootMenuPath.value = result.rootMenuPath ?? '';
    mixExtraMenus.value = result.rootMenu?.children ?? [];
    rootMenuPath.value = rootMenu?.path ?? '';
    splitSideMenus.value = rootMenu?.children ?? [];
    console.log('[calcSideMenus] fallback splitSideMenus:', splitSideMenus.value.map(m => m.path));
  }

  watch(
    () => [route.path, menus.value],
    ([path]) => {
      const currentPath = (route?.meta?.activePath as string) ?? path;
      calcSideMenus(currentPath as string);
      if (rootMenuPath.value)
        defaultSubMap.set(rootMenuPath.value, currentPath as string);
    },
    { immediate: true },
  );

  return {
    handleMenuSelect,
    handleMenuOpen,
    headerActive,
    headerMenus,
    sidebarActive,
    sidebarMenus,
    mixHeaderMenus,
    mixExtraMenus,
    sidebarVisible,
  };
}

export { useMixedMenu };
