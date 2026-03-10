import type { MenuRecordRaw } from '@/_core/types';
import { defineStore } from 'pinia';

interface UserAccessState {
  userAccessToken: string | null;
  tokenExpireTime: number | null; // 存储token过期时间戳
  isAccessChecked: boolean;
  loginExpired: boolean;
  /** 可访问的菜单列表 (MenuRecordRaw 格式) */
  accessMenus: MenuRecordRaw[];
  routes: any[];
}

export const useUserAccessStore = defineStore('userAccess', {
  state: (): UserAccessState => ({
    userAccessToken: null,
    tokenExpireTime: null,
    isAccessChecked: false,
    loginExpired: false,
    accessMenus: [],
    routes: [],
  }),

  getters: {
    getUserAccessToken(): string | null {
      return this.userAccessToken;
    },
    getIsAccessChecked(): boolean {
      return this.isAccessChecked;
    },
    getLoginExpired(): boolean {
      return this.loginExpired;
    },
    isValidToken(): boolean {
      if (!this.userAccessToken || !this.tokenExpireTime) {
        console.log('检查token有效性: token或expireTime为空');
        return false;
      }
      const isValid = Date.now() < this.tokenExpireTime;
      console.log('检查token有效性:', {
        hasToken: !!this.userAccessToken,
        hasExpireTime: !!this.tokenExpireTime,
        currentTime: Date.now(),
        expireTime: this.tokenExpireTime,
        isExpired: Date.now() >= this.tokenExpireTime,
        isValid
      });
      return isValid;
    },
    /**
     * 获取菜单（兼容旧代码的 menus 别名）
     */
    menus(): MenuRecordRaw[] {
      return this.accessMenus;
    },
  },
  actions: {
    setUserAccessToken(token: string | null) {
      this.userAccessToken = token;
      // 设置72小时有效期
      this.tokenExpireTime = token ? Date.now() + 72 * 60 * 60 * 1000 : null;
      // 持久化存储到localStorage
      if (token) {
        localStorage.setItem('userAccessToken', token);
        localStorage.setItem('tokenExpireTime', String(this.tokenExpireTime));
      } else {
        localStorage.removeItem('userAccessToken');
        localStorage.removeItem('tokenExpireTime');
        localStorage.removeItem('userMenus');
      }
    },
    initFromStorage() {
      console.log('开始从localStorage初始化token和menus...');
      const token = localStorage.getItem('userAccessToken');
      const expireTime = localStorage.getItem('tokenExpireTime');
      const menus = localStorage.getItem('userMenus');
      
      if (menus) {
        try {
          const parsedMenus = JSON.parse(menus);
          console.log('[initFromStorage] parsed menus:', parsedMenus.map((m: any) => ({ path: m.path, name: m.name })));
          this.accessMenus = parsedMenus;
        } catch (e) {
          console.error('解析menus失败:', e);
        }
      } else {
        console.log('[initFromStorage] no menus in localStorage');
      }
      console.log('从localStorage获取的token:', token);
      console.log('从localStorage获取的expireTime:', expireTime);
      
      if (token && expireTime) {
        console.log('检查token有效期...');
        const currentTime = Date.now();
        const expireTimestamp = Number(expireTime);
        console.log('当前时间:', currentTime);
        console.log('过期时间:', expireTimestamp);
        
        if (currentTime < expireTimestamp) {
          console.log('token有效，设置到store');
          this.userAccessToken = token;
          this.tokenExpireTime = expireTimestamp;
        } else {
          console.log('token已过期，清除存储');
          localStorage.removeItem('userAccessToken');
          localStorage.removeItem('tokenExpireTime');
          localStorage.removeItem('userMenus');
        }
      } else {
        console.log('localStorage中没有找到token或expireTime');
      }
      console.log('初始化完成后的store状态:', {
        userAccessToken: this.userAccessToken,
        tokenExpireTime: this.tokenExpireTime,
        isValidToken: this.isValidToken
      });
    },
    setIsAccessChecked(checked: boolean) {
      this.isAccessChecked = checked;
    },
    setLoginExpired(expired: boolean) {
      this.loginExpired = expired;
    },
    /**
     * 设置可访问菜单列表 (MenuRecordRaw 格式)
     */
    setAccessMenus(menus: MenuRecordRaw[]) {
      this.accessMenus = menus;
      // 持久化存储到localStorage
      localStorage.setItem('userMenus', JSON.stringify(menus));
    },
    /**
     * 兼容旧代码的 setMenus 方法
     */
    setMenus(menus: MenuRecordRaw[]) {
      this.setAccessMenus(menus);
    },
    setRoutes(routes: any[]) {
      // 用户路由暂不需要持久化存储
      this.routes = routes;
    },
    /**
     * 根据路径查找菜单
     */
    getMenuByPath(path: string): MenuRecordRaw | undefined {
      function findMenu(menus: MenuRecordRaw[], targetPath: string): MenuRecordRaw | undefined {
        for (const menu of menus) {
          if (menu.path === targetPath) {
            return menu;
          }
          if (menu.children) {
            const matched = findMenu(menu.children, targetPath);
            if (matched) {
              return matched;
            }
          }
        }
      }
      return findMenu(this.accessMenus, path);
    },
  },
});

export function useUserAccessStoreWithOut() {
  return useUserAccessStore();
}
