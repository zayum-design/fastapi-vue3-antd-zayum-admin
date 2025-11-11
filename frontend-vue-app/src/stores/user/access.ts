import { defineStore } from 'pinia';

interface MenuItem {
  label: string;
  value: string;
  name?: string; // 兼容路由name
  icon?: any; // 使用any类型兼容Component和string
  path?: string;
  meta?: Record<string, any>; // 兼容路由meta
  children?: MenuItem[]; // 支持子菜单
}

interface UserAccessState {
  userAccessToken: string | null;
  tokenExpireTime: number | null; // 存储token过期时间戳
  isAccessChecked: boolean;
  loginExpired: boolean;
  menus: MenuItem[];
  routes: any[];
}

export const useUserAccessStore = defineStore('userAccess', {
  state: (): UserAccessState => ({
    userAccessToken: null,
    tokenExpireTime: null,
    isAccessChecked: false,
    loginExpired: false,
    menus: [],
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
      }
    },
    initFromStorage() {
      console.log('开始从localStorage初始化token和menus...');
      const token = localStorage.getItem('userAccessToken');
      const expireTime = localStorage.getItem('tokenExpireTime');
      const menus = localStorage.getItem('userMenus');
      
      if (menus) {
        try {
          this.menus = JSON.parse(menus);
        } catch (e) {
          console.error('解析menus失败:', e);
        }
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
    setMenus(menus: MenuItem[]) {
      this.menus = menus;
      // 持久化存储到localStorage
      localStorage.setItem('userMenus', JSON.stringify(menus));
    },
    setRoutes(routes: any[]) {
      // 用户路由暂不需要持久化存储
      this.routes = routes;
    },
  },
});

export function useUserAccessStoreWithOut() {
  return useUserAccessStore();
}
