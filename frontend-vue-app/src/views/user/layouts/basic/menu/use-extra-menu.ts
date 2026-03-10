import type { ComputedRef } from 'vue';

import type { MenuRecordRaw } from '@/_core/types';

import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import { layoutConfig } from '../../layout-config';
import { useUserAccessStore } from '@/stores/user/access';
import { findRootMenuByPath } from '@/_core/utils';

import { useNavigation } from './use-navigation';

function useExtraMenu(useRootMenus?: ComputedRef<MenuRecordRaw[]>) {
  const accessStore = useUserAccessStore();
  const { navigation } = useNavigation();

  // 从 user access store 获取菜单数据
  const storeMenus = computed<MenuRecordRaw[]>(() => accessStore.accessMenus || []);

  const menus = computed(() => useRootMenus?.value ?? storeMenus.value);

  /** 记录当前顶级菜单下哪个子菜单最后激活 */
  const defaultSubMap = new Map<string, string>();
  const extraRootMenus = ref<MenuRecordRaw[]>([]);
  const route = useRoute();
  const extraMenus = ref<MenuRecordRaw[]>([]);
  const sidebarExtraVisible = ref<boolean>(false);
  const extraActiveMenu = ref('');
  const parentLevel = computed(() =>
    layoutConfig.app.layout === 'header-mixed-nav' ? 1 : 0,
  );

  /**
   * 选择混合菜单事件
   * @param menu
   */
  const handleMixedMenuSelect = async (menu: MenuRecordRaw) => {
    extraMenus.value = menu?.children ?? [];
    extraActiveMenu.value = menu.parents?.[parentLevel.value] ?? menu.path;
    const hasChildren = extraMenus.value.length > 0;

    sidebarExtraVisible.value = hasChildren;
    if (!hasChildren) {
      await navigation(menu.path);
    } else if (layoutConfig.sidebar.autoActivateChild) {
      await navigation(
        defaultSubMap.has(menu.path)
          ? (defaultSubMap.get(menu.path) as string)
          : menu.path,
      );
    }
  };

  /**
   * 选择默认菜单事件
   * @param menu
   * @param rootMenu
   */
  const handleDefaultSelect = async (
    menu: MenuRecordRaw,
    rootMenu?: MenuRecordRaw,
  ) => {
    extraMenus.value = rootMenu?.children ?? extraRootMenus.value ?? [];
    extraActiveMenu.value = menu.parents?.[parentLevel.value] ?? menu.path;

    if (layoutConfig.sidebar.expandOnHover) {
      sidebarExtraVisible.value = extraMenus.value.length > 0;
    }
  };

  /**
   * 侧边菜单鼠标移出事件
   */
  const handleSideMouseLeave = () => {
    if (layoutConfig.sidebar.expandOnHover) {
      return;
    }

    const { findMenu, rootMenu, rootMenuPath } = findRootMenuByPath(
      menus.value,
      route.path,
    );
    extraActiveMenu.value = rootMenuPath ?? findMenu?.path ?? '';
    extraMenus.value = rootMenu?.children ?? [];
  };

  const handleMenuMouseEnter = (menu: MenuRecordRaw) => {
    if (!layoutConfig.sidebar.expandOnHover) {
      const { findMenu } = findRootMenuByPath(menus.value, menu.path);
      extraMenus.value = findMenu?.children ?? [];
      extraActiveMenu.value = menu.parents?.[parentLevel.value] ?? menu.path;
      sidebarExtraVisible.value = extraMenus.value.length > 0;
    }
  };

  function calcExtraMenus(path: string) {
    const currentPath = (route.meta?.activePath as string) || path;
    
    // 先找到当前菜单项（支持扁平菜单结构）
    const currentMenu = menus.value.find((item) => item.path === currentPath);
    if (currentMenu) {
      extraActiveMenu.value = currentMenu.path ?? '';
      extraMenus.value = currentMenu.children ?? [];
      extraRootMenus.value = currentMenu.children ?? menus.value;
      if (layoutConfig.sidebar.expandOnHover) {
        sidebarExtraVisible.value = extraMenus.value.length > 0;
      }
      return;
    }
    
    // 原有逻辑（用于支持层级菜单）
    const { findMenu, rootMenu, rootMenuPath } = findRootMenuByPath(
      menus.value,
      currentPath,
      parentLevel.value,
    );
    extraRootMenus.value = rootMenu?.children ?? [];
    if (rootMenuPath) defaultSubMap.set(rootMenuPath, currentPath);
    extraActiveMenu.value = rootMenuPath ?? findMenu?.path ?? '';
    extraMenus.value = rootMenu?.children ?? [];
    if (layoutConfig.sidebar.expandOnHover) {
      sidebarExtraVisible.value = extraMenus.value.length > 0;
    }
  }

  watch(
    () => [route.path, layoutConfig.app.layout],
    ([path]) => {
      calcExtraMenus(path as string || '');
    },
    { immediate: true },
  );

  return {
    extraActiveMenu,
    extraMenus,
    handleDefaultSelect,
    handleMenuMouseEnter,
    handleMixedMenuSelect,
    handleSideMouseLeave,
    sidebarExtraVisible,
  };
}

export { useExtraMenu };
