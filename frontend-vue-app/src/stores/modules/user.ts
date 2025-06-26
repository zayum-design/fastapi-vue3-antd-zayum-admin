import { acceptHMRUpdate, defineStore } from 'pinia';

interface BasicUserInfo {
  avatar: string;
  created_at: string;
  email: string;
  group_id: number;
  id: number;
  login_at: string;
  login_failure: number;
  login_ip: string;
  mobile: string;
  nickname: string;
  roles: string[];
  status: string;
  token: string;
  updated_at: string;
  username: string;
  logs:any[]
}

interface AccessState {
  /**
   * 用户信息
   */
  userInfo: BasicUserInfo | null;
  /**
   * 用户角色
   */
  userRoles: string[];
}

/**
 * @zh_CN 用户信息相关
 */
export const useUserStore = defineStore('core-user', {
  actions: {
    setUserInfo(userInfo: BasicUserInfo | null) {
      // 设置用户信息
      this.userInfo = userInfo;
      // 设置角色信息
      const roles = userInfo?.roles ?? [];
      this.setUserRoles(roles);
      
      console.log("设置用户信息",this.userInfo,this.userRoles); 
    },
    setUserRoles(roles: string[]) {
      this.userRoles = roles;
    },
  },
  state: (): AccessState => ({
    userInfo: null,
    userRoles: [],
  }),
});

// 解决热更新问题
const hot = import.meta.hot;
if (hot) {
  hot.accept(acceptHMRUpdate(useUserStore, hot));
}
