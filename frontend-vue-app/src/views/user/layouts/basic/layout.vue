<script lang="ts" setup>
import type { SetupContext } from 'vue';

import type { MenuRecordRaw } from '@/_core/types';

import { computed, useSlots, watch } from 'vue';

import { useRefresh } from '@/_core/hooks';
import { $t, i18n } from '@/locales';
import { layoutConfig } from '../layout-config';
import { useLockStore } from '@/stores';
import { cloneDeep, mapTree } from '@/utils';

import { ZayumLayout } from '@/_core/ui/common-ui/layout-ui';
import { ZayumBackTop, ZayumLogo } from '@/_core/ui/common-ui/shadcn-ui';

import { Breadcrumb, CheckUpdates, Preferences } from '@/layouts/widgets';

import { LayoutContent, LayoutContentSpinner } from './content';
import { Copyright } from './copyright';
import { LayoutFooter } from './footer';
import { LayoutHeader } from './header';
import {
  LayoutExtraMenu,
  LayoutMenu,
  LayoutMixedMenu,
  useExtraMenu,
  useMixedMenu,
} from './menu';
import { LayoutTabbar } from './tabbar';

defineOptions({ name: 'BasicLayout' });

const emit = defineEmits<{ clearPreferencesAndLogout: [] }>();

const isMobile = computed(() => {
  return window.innerWidth < 768 || layoutConfig.app.isMobile;
});

const isDark = computed(() => {
  return layoutConfig.theme.darkMode;
});

const theme = computed(() => {
  return isDark.value ? 'dark' : 'light';
});

const layout = computed(() => 
  isMobile.value ? 'sidebar-nav' : layoutConfig.app.layout
);

const isHeaderNav = computed(() => 
  layout.value === 'header-nav'
);

const isMixedNav = computed(() => 
  layout.value === 'mixed-nav'
);

const isSideMixedNav = computed(() => 
  layout.value === 'sidebar-mixed-nav'
);

const isHeaderMixedNav = computed(() => 
  layout.value === 'header-mixed-nav'
);

const isHeaderSidebarNav = computed(() => 
  layout.value === 'header-sidebar-nav'
);

const sidebarCollapsed = computed(() => 
  layoutConfig.sidebar.collapsed
);

const preferencesButtonPosition = computed(() => {
  const { enablePreferences, preferencesButtonPosition } = layoutConfig.app;

  if (!enablePreferences) {
    return {
      fixed: false,
      header: false,
    };
  }

  const { header, sidebar } = layoutConfig;
  const headerHidden = header.hidden;
  const sidebarHidden = sidebar.hidden;

  const contentIsMaximize = headerHidden && sidebarHidden;

  const isHeaderPosition = preferencesButtonPosition === 'header';

  if (preferencesButtonPosition !== 'auto') {
    return {
      fixed: preferencesButtonPosition === 'fixed',
      header: isHeaderPosition,
    };
  }

  const fixed =
    contentIsMaximize ||
    layout.value === 'full-content' ||
    isMobile.value ||
    !layoutConfig.header.enable;

  return {
    fixed,
    header: !fixed,
  };
});
const lockStore = useLockStore();
const { refresh } = useRefresh();

const sidebarTheme = computed(() => {
  const dark = isDark.value || layoutConfig.theme.semiDarkSidebar;
  return dark ? 'dark' : 'light';
});

const headerTheme = computed(() => {
  const dark = isDark.value || layoutConfig.theme.semiDarkHeader;
  return dark ? 'dark' : 'light';
});

const logoClass = computed(() => {
  const { collapsedShowTitle } = layoutConfig.sidebar;
  const classes: string[] = [];

  if (collapsedShowTitle && sidebarCollapsed.value && !isMixedNav.value) {
    classes.push('mx-auto');
  }

  if (isSideMixedNav.value) {
    classes.push('flex-center');
  }

  return classes.join(' ');
});

const isMenuRounded = computed(() => {
  return layoutConfig.navigation.styleType === 'rounded';
});

const logoCollapsed = computed(() => {
  if (isMobile.value && sidebarCollapsed.value) {
    return true;
  }
  if (isHeaderNav.value || isMixedNav.value || isHeaderSidebarNav.value) {
    return false;
  }
  return (
    sidebarCollapsed.value || isSideMixedNav.value || isHeaderMixedNav.value
  );
});

const showHeaderNav = computed(() => {
  return (
    !isMobile.value &&
    (isHeaderNav.value || isMixedNav.value || isHeaderMixedNav.value)
  );
});

const {
  handleMenuSelect,
  handleMenuOpen,
  headerActive,
  headerMenus,
  sidebarActive,
  sidebarMenus,
  mixHeaderMenus,
  sidebarVisible,
} = useMixedMenu();

// 侧边多列菜单
const {
  extraActiveMenu,
  extraMenus,
  handleDefaultSelect,
  handleMenuMouseEnter,
  handleMixedMenuSelect,
  handleSideMouseLeave,
  sidebarExtraVisible,
} = useExtraMenu(mixHeaderMenus);

/**
 * 包装菜单，翻译菜单名称
 * @param menus 原始菜单数据
 * @param deep 是否深度包装。对于双列布局，只需要包装第一层，因为更深层的数据会在扩展菜单中重新包装
 */
function wrapperMenus(menus: MenuRecordRaw[], deep: boolean = true) {
  return deep
    ? mapTree(menus, (item) => {
        return { ...cloneDeep(item), name: $t(item.name) };
      })
    : menus.map((item) => {
        return { ...cloneDeep(item), name: $t(item.name) };
      });
}

function toggleSidebar() {
  // 直接修改 layoutConfig 中的 sidebar.hidden
  layoutConfig.sidebar.hidden = !layoutConfig.sidebar.hidden;
}

function clearPreferencesAndLogout() {
  emit('clearPreferencesAndLogout');
}

watch(
  layout,
  async (val) => {
    if (val === 'sidebar-mixed-nav' && layoutConfig.sidebar.hidden) {
      layoutConfig.sidebar.hidden = false;
    }
  },
);

// 语言更新后，刷新页面
// i18n.global.locale会在preference.app.locale变更之后才会更新，因此watchpreference.app.locale是不合适的，刷新页面时可能语言配置尚未完全加载完成
watch(i18n.global.locale, refresh, { flush: 'post' });

const slots: SetupContext['slots'] = useSlots();
const headerSlots = computed(() => {
  return Object.keys(slots).filter((key) => key.startsWith('header-'));
});
</script>

<template>
  <ZayumLayout
    v-model:sidebar-extra-visible="sidebarExtraVisible"
    :content-compact="layoutConfig.contentCompact as any"
    :footer-enable="layoutConfig.footer.enable"
    :footer-fixed="layoutConfig.footer.fixed"
    :header-hidden="layoutConfig.header.hidden"
    :header-mode="layoutConfig.header.mode as any"
    :header-theme="headerTheme"
    :header-toggle-sidebar-button="layoutConfig.widget.sidebarToggle"
    :header-visible="layoutConfig.header.enable"
    :is-mobile="isMobile"
    :layout="layout"
    :sidebar-collapse="layoutConfig.sidebar.collapsed"
    :sidebar-collapse-show-title="layoutConfig.sidebar.collapsedShowTitle"
    :sidebar-enable="sidebarVisible"
    :sidebar-expand-on-hover="layoutConfig.sidebar.expandOnHover"
    :sidebar-extra-collapse="layoutConfig.sidebar.extraCollapse"
    :sidebar-hidden="layoutConfig.sidebar.hidden"
    :sidebar-theme="sidebarTheme"
    :sidebar-width="layoutConfig.sidebar.width"
    :tabbar-enable="layoutConfig.tabbar.enable"
    :tabbar-height="layoutConfig.tabbar.height"
    @side-mouse-leave="handleSideMouseLeave"
    @toggle-sidebar="toggleSidebar"
    @update:sidebar-collapse="
      (value: boolean | undefined) => layoutConfig.sidebar.collapsed = value ?? false
    "
    @update:sidebar-enable="
      (value: boolean | undefined) => layoutConfig.sidebar.enable = value ?? false
    "
    @update:sidebar-expand-on-hover="
      (value: boolean | undefined) => layoutConfig.sidebar.expandOnHover = value ?? false
    "
    @update:sidebar-extra-collapse="
      (value: boolean | undefined) => layoutConfig.sidebar.extraCollapse = value ?? false
    "
  >
    <!-- logo -->
    <template #logo>
      <ZayumLogo
        v-if="layoutConfig.logo.enable"
        :class="logoClass"
        :collapsed="logoCollapsed"
        :src="layoutConfig.logo.source"
        :text="layoutConfig.appName"
        :theme="showHeaderNav ? headerTheme : theme"
      />
    </template>
    <!-- 头部区域 -->
    <template #header>
      <LayoutHeader
        :theme="theme"
        @clear-preferences-and-logout="clearPreferencesAndLogout"
      >
        <template
          v-if="!showHeaderNav && layoutConfig.breadcrumb.enable"
          #breadcrumb
        >
            <Breadcrumb
              :hide-when-only-one="layoutConfig.breadcrumb.hideOnlyOne"
              :show-home="layoutConfig.breadcrumb.showHome"
              :show-icon="layoutConfig.breadcrumb.showIcon"
              :type="layoutConfig.breadcrumb.styleType"
            />
        </template>
        <template v-if="showHeaderNav" #menu>
          <LayoutMenu
            :default-active="headerActive"
            :menus="wrapperMenus(headerMenus)"
            :rounded="isMenuRounded"
            :theme="headerTheme"
            class="w-full"
            mode="horizontal"
            @select="handleMenuSelect"
          />
        </template>
        <template #user-dropdown>
          <slot name="user-dropdown"></slot>
        </template>
        <template #notification>
          <slot name="notification"></slot>
        </template>
        <template v-for="item in headerSlots" #[item]>
          <slot :name="item"></slot>
        </template>
      </LayoutHeader>
    </template>
    <!-- 侧边菜单区域 -->
    <template #menu>
      <LayoutMenu
        :accordion="layoutConfig.navigation.accordion"
        :collapse="layoutConfig.sidebar.collapsed"
        :collapse-show-title="layoutConfig.sidebar.collapsedShowTitle"
        :default-active="sidebarActive"
        :menus="wrapperMenus(sidebarMenus)"
        :rounded="isMenuRounded"
        :theme="sidebarTheme"
        mode="vertical"
        @open="handleMenuOpen"
        @select="handleMenuSelect"
      />
    </template>
    <template #mixed-menu>
      <LayoutMixedMenu
        :active-path="extraActiveMenu"
        :menus="wrapperMenus(mixHeaderMenus, false)"
        :rounded="isMenuRounded"
        :theme="sidebarTheme"
        @default-select="handleDefaultSelect"
        @enter="handleMenuMouseEnter"
        @select="handleMixedMenuSelect"
      />
    </template>
    <!-- 侧边额外区域 -->
    <template #side-extra>
      <LayoutExtraMenu
        :accordion="layoutConfig.navigation.accordion"
        :collapse="layoutConfig.sidebar.extraCollapse"
        :menus="wrapperMenus(extraMenus)"
        :rounded="isMenuRounded"
        :theme="sidebarTheme"
      />
    </template>
    <template #side-extra-title>
      <ZayumLogo
        v-if="layoutConfig.logo.enable"
        :text="layoutConfig.appName"
        :theme="theme"
      />
    </template>

    <template #tabbar>
      <LayoutTabbar
        v-if="layoutConfig.tabbar.enable"
        :show-icon="layoutConfig.tabbar.showIcon"
        :theme="theme"
      />
    </template>

    <!-- 主体内容 -->
    <template #content>
      <LayoutContent />
    </template>

    <template v-if="false" #content-overlay>
      <LayoutContentSpinner />
    </template>

    <!-- 页脚 -->
    <template v-if="layoutConfig.footer.enable" #footer>
      <LayoutFooter>
        <Copyright
          v-if="layoutConfig.copyright.enable"
          v-bind="layoutConfig.copyright"
        />
      </LayoutFooter>
    </template>

    <template #extra>
      <slot name="extra"></slot>
      <CheckUpdates
        v-if="false"
        :check-updates-interval="0"
      />

      <Transition v-if="false" name="slide-up">
        <slot v-if="lockStore.isLockScreen" name="lock-screen"></slot>
      </Transition>

      <template v-if="preferencesButtonPosition.fixed">
        <Preferences
          class="z-100 fixed bottom-20 right-0"
          @clear-preferences-and-logout="clearPreferencesAndLogout"
        />
      </template>
      <ZayumBackTop />
    </template>
  </ZayumLayout>
</template>
