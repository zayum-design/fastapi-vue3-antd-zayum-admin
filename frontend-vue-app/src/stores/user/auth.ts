import type { UserInfo } from "@/_core/types";
import { ref } from "vue";
import { defineStore } from "pinia";
import { getProfileApi, logoutApi } from '@/api/user/auth';
import { useUserAccessStore } from './access';

export const useUserAuthStore = defineStore('userAuth', () => {
  const accessStore = useUserAccessStore();
  const loginLoading = ref(false);
  const userInfo = ref<UserInfo | null>(null);

  async function fetchUserInfo() {
    try {
      console.log("开始获取用户信息...");
      const res = await getProfileApi();
      if (res) {
        userInfo.value = res;
        // 持久化存储用户信息
        localStorage.setItem('userProfile', JSON.stringify(res));
        console.log("用户信息获取成功并存储:", userInfo.value);
        return userInfo.value;
      }
      console.error("获取用户信息失败: 返回空数据");
      return null;
    } catch (error) {
      console.error("获取用户信息失败:", error);
      return null;
    }
  }

  function initFromStorage() {
    const profile = localStorage.getItem('userProfile');
    if (profile) {
      try {
        userInfo.value = JSON.parse(profile);
        console.log("从存储加载用户信息:", userInfo.value);
      } catch (error) {
        console.error("解析存储的用户信息失败:", error);
      }
    }
  }

  async function logout() {
    try {
      console.log("开始登出...");
      await logoutApi();
    } catch {
      console.log("登出过程中发生错误，但继续执行...");
    }
    accessStore.setUserAccessToken(null);
    accessStore.setLoginExpired(false);
    localStorage.removeItem('userProfile');
    userInfo.value = null;
    console.log("已清除用户信息和token");
  }

  // 初始化时从存储加载用户信息
  initFromStorage();
  console.log('AuthStore初始化完成，当前用户信息:', userInfo.value);

  return {
    fetchUserInfo,
    loginLoading,
    logout,
    userInfo,
    initFromStorage
  };
});
