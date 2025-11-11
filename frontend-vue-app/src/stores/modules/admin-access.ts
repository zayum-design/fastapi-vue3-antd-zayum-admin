import type { RouteRecordRaw } from 'vue-router';

import type { MenuRecordRaw } from '@/_core/typings';

import { acceptHMRUpdate, defineStore } from 'pinia';

type AdminAccessToken = null | string;

interface AdminAccessState {
  /**
   * 权限码
   */
  accessCodes: string[];
  /**
   * 可访问的菜单列表
   */
  accessMenus: MenuRecordRaw[];
  /**
   * 可访问的路由列表
   */
  accessRoutes: RouteRecordRaw[];
  /**
   * 登录 adminAccessToken
   */
  adminAccessToken: AdminAccessToken;
  /**
   * 是否已经检查过权限
   */
  isAccessChecked: boolean;
  /**
   * 登录是否过期
   */
  loginExpired: boolean;
  /**
   * 登录 adminAccessToken
   */
  refreshToken: AdminAccessToken;
  /**
   * 登录时间戳
   */
  loginTime: number | null;
  /**
   * 登录过期检查定时器
   */
  expiryTimer: number | null;
}

/**
 * @zh_CN 访问权限相关
 */
export const useAdminAccessStore = defineStore('core-access', {
  actions: {
    getMenuByPath(path: string) {
      function findMenu(
        menus: MenuRecordRaw[],
        path: string,
      ): MenuRecordRaw | undefined {
        for (const menu of menus) {
          if (menu.path === path) {
            return menu;
          }
          if (menu.children) {
            const matched = findMenu(menu.children, path);
            if (matched) {
              return matched;
            }
          }
        }
      }
      return findMenu(this.accessMenus, path);
    },
    setAccessCodes(codes: string[]) {
      this.accessCodes = codes;
    },
    setAccessMenus(menus: MenuRecordRaw[]) {
      this.accessMenus = menus;
    },
    setAccessRoutes(routes: RouteRecordRaw[]) {
      this.accessRoutes = routes;
    },
    setAccessToken(token: AdminAccessToken) {
      this.adminAccessToken = token;
    },
    setIsAccessChecked(isAccessChecked: boolean) {
      this.isAccessChecked = isAccessChecked;
    },
    setLoginExpired(loginExpired: boolean) {
      this.loginExpired = loginExpired;
    },
    setRefreshToken(token: AdminAccessToken) {
      this.refreshToken = token;
    },
    /**
     * 设置登录时间并启动过期检查
     */
    setLoginTime() {
      this.loginTime = Date.now();
      this.startExpiryCheck();
    },
    /**
     * 启动登录过期检查
     */
    startExpiryCheck() {
      // 清除之前的定时器
      if (this.expiryTimer) {
        clearTimeout(this.expiryTimer);
      }

      const expiryHours = import.meta.env.VITE_LOGIN_EXPIRY_HOURS || 2;
      const expiryMs = expiryHours * 60 * 60 * 1000; // 转换为毫秒

      this.expiryTimer = window.setTimeout(() => {
        console.log('登录已过期，自动退出登录');
        this.setLoginExpired(true);
        // 触发自动登出逻辑
        this.triggerAutoLogout();
      }, expiryMs);
    },

    /**
     * 触发自动登出
     */
    triggerAutoLogout() {
      // 这里可以添加自动登出的逻辑，比如显示通知等
      console.log('触发自动登出');
      // 在实际项目中，这里可以调用认证存储的logout方法
      // 但由于循环依赖问题，我们通过设置loginExpired状态来触发路由守卫中的登出
    },
    /**
     * 清除登录过期检查定时器
     */
    clearExpiryCheck() {
      if (this.expiryTimer) {
        clearTimeout(this.expiryTimer);
        this.expiryTimer = null;
      }
      this.loginTime = null;
    },
    /**
     * 检查登录是否过期
     */
    checkLoginExpiry(): boolean {
      if (!this.loginTime) return false;

      const expiryHours = import.meta.env.VITE_LOGIN_EXPIRY_HOURS || 2;
      const expiryMs = expiryHours * 60 * 60 * 1000;
      const currentTime = Date.now();
      const timeDiff = currentTime - this.loginTime;

      return timeDiff >= expiryMs;
    },

    /**
     * 初始化登录过期检查
     * 在应用启动时调用，重新启动过期检查定时器
     */
    initExpiryCheck() {
      if (this.adminAccessToken && this.loginTime) {
        // 检查是否已经过期
        if (this.checkLoginExpiry()) {
          console.log('登录已过期，设置过期状态');
          this.setLoginExpired(true);
        } else {
          // 重新启动过期检查定时器
          this.startExpiryCheck();
        }
      }
    },
  },
  persist: {
    // 持久化
    pick: ['adminAccessToken', 'refreshToken', 'accessCodes', 'loginTime'],
  },
  state: (): AdminAccessState => ({
    accessCodes: [],
    accessMenus: [],
    accessRoutes: [],
    adminAccessToken: null,
    isAccessChecked: false,
    loginExpired: false,
    refreshToken: null,
    loginTime: null,
    expiryTimer: null,
  }),
});

// 解决热更新问题
const hot = import.meta.hot;
if (hot) {
  hot.accept(acceptHMRUpdate(useAdminAccessStore, hot));
}
