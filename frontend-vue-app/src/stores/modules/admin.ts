import { acceptHMRUpdate, defineStore } from 'pinia';
import type { AdminInfo } from "@/_core/types";
 

interface AdminAccessState {
  /**
   * 用户信息
   */
  adminInfo: AdminInfo | null;
  /**
   * 用户角色
   */
  adminRoles: string[];
}

/**
 * @zh_CN 用户信息相关
 */
export const useAdminStore = defineStore('core-user', {
  actions: {
    setAdminInfo(adminInfo: AdminInfo | null) {
      // 设置用户信息
      this.adminInfo = adminInfo;
      // 设置角色信息
      const roles = adminInfo?.roles ?? [];
      this.setUserRoles(roles);
      
      console.log("设置用户信息",this.adminInfo,this.adminRoles); 
    },
    setUserRoles(roles: string[]) {
      this.adminRoles = roles;
    },
  },
  state: (): AdminAccessState => ({
    adminInfo: null,
    adminRoles: [],
  }),
});

// 解决热更新问题
const hot = import.meta.hot;
if (hot) {
  hot.accept(acceptHMRUpdate(useAdminStore, hot));
}
