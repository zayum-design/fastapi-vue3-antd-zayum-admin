import type { Recordable, UserInfo } from "@/_core/types";

import { ref } from "vue";
import { useRouter } from "vue-router";

import { DEFAULT_ADMIN_PATH, LOGIN_PATH } from "@/constants";
import { resetAllStores, useAccessStore, useUserStore } from "@/stores";

import { notification } from "ant-design-vue";
import { defineStore } from "pinia";

import { getAccessCodesApi, getProfileApi, loginApi, logoutApi } from "@/api";
import { $t } from "@/locales";

export const useAuthStore = defineStore("auth", () => {
  const accessStore = useAccessStore();
  const userStore = useUserStore();
  const router = useRouter();

  const loginLoading = ref(false);

  /**
   * 异步处理登录操作
   * Asynchronously handle the login process
   * @param params 登录表单数据
   */
  async function authLogin(
    params: Recordable<any>,
    onSuccess?: () => Promise<void> | void
  ) {
    // 异步处理用户登录操作并获取 accessToken
    let userInfo: null | UserInfo = null;
    try {
      loginLoading.value = true;
      console.log("开始登录..."); // 中文测试输出

      const { access_token } = await loginApi(params);
      console.log("登录成功，获取到 access_token:", access_token); // 中文测试输出

      // 存储 access_token 到 accessStore
      accessStore.setAccessToken(access_token);

      // 获取用户信息并存储到 accessStore 中
      console.log("开始获取用户信息和权限码..."); // 中文测试输出
      const [fetchUserInfoResult, accessCodes] = await Promise.all([
        fetchUserInfo(),
        getAccessCodesApi(),
      ]);

      userInfo = fetchUserInfoResult;
      
      userStore.setUserInfo(userInfo);
      accessStore.setAccessCodes(accessCodes);

      if (accessStore.loginExpired) {
        console.log("检测到登录过期，重置登录状态..."); // 中文测试输出
        accessStore.setLoginExpired(false);
      } else {
        console.log("登录成功，准备跳转到首页或指定页面..."); // 中文测试输出
        onSuccess
          ? await onSuccess?.()
          : await router.push(DEFAULT_ADMIN_PATH);
      }

      if (userInfo?.nickname) {
        console.log("用户信息获取成功，显示通知..."); // 中文测试输出
        notification.success({
          description: `${$t("authentication.loginSuccessDesc")}:${
            userInfo?.nickname
          }`,
          duration: 3,
          message: $t("authentication.loginSuccess"),
        });
      }
    } finally {
      loginLoading.value = false;
      console.log("登录流程结束，重置登录加载状态..."); // 中文测试输出
    }

    return {
      userInfo,
    };
  }

  async function logout(redirect: boolean = true) {
    try {
      console.log("开始登出..."); // 中文测试输出
      await logoutApi();
    } catch {
      console.log("登出过程中发生错误，但继续执行..."); // 中文测试输出
      // 不做任何处理
    }
    console.log("重置所有存储状态..."); // 中文测试输出
    resetAllStores();
    accessStore.setLoginExpired(false);

    // 回登录页带上当前路由地址
    console.log("跳转到登录页..."); // 中文测试输出
    await router.replace({
      path: LOGIN_PATH,
      query: redirect
        ? {
            redirect: encodeURIComponent(router.currentRoute.value.fullPath),
          }
        : {},
    });
  }

  async function fetchUserInfo() {
    let userInfo: null | UserInfo = null;
    console.log("开始获取用户信息..."); // 中文测试输出
    userInfo = await getProfileApi();
    console.log("用户信息获取成功:", userInfo); // 中文测试输出
    userStore.setUserInfo(userInfo);
    return userInfo;
  }

  function $reset() {
    console.log("重置登录加载状态..."); // 中文测试输出
    loginLoading.value = false;
  }

  return {
    $reset,
    authLogin,
    fetchUserInfo,
    loginLoading,
    logout,
  };
});
