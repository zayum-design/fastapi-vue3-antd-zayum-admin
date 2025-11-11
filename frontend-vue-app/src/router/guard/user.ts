import type { Router } from "vue-router";
import type { RouteRecordStringComponent } from '@/_core/types';
import { USER_LOGIN_PATH, DEFAULT_USER_PATH } from "@/constants";
import { useUserAccessStore } from "@/stores/user/access";
import { useUserAuthStore } from "@/stores/user/auth";
import { generateAccess } from "../access";
import { accessRoutes } from "@/router/routes";
import { getAllUserRouterApi } from "@/api/user/user_router";

interface UserMenu {
  name: string;
  path: string;
  meta?: {
    title: string;
    icon?: string;
  };
}

/**
 * 用户路由守卫配置
 * @param router 
 */
export function setupUserGuard(router: Router) {
  router.beforeEach(async (to, from) => {
    const accessStore = useUserAccessStore();
    const authStore = useUserAuthStore();

    // 初始化存储状态
    await authStore.initFromStorage();
    await accessStore.initFromStorage();

    // 登录页面特殊处理
    if (to.path === USER_LOGIN_PATH) {
      if (accessStore.userAccessToken && authStore.userInfo) {
        return decodeURIComponent(
          (to.query?.redirect as string) || DEFAULT_USER_PATH
        );
      }
      return true;
    }

    // 非用户路由直接放行
    if (!to.path.startsWith('/user')) {
      return true;
    }

    // 检查访问令牌
    if (!accessStore.userAccessToken) {
      return {
        path: USER_LOGIN_PATH,
        query: 
          to.fullPath === DEFAULT_USER_PATH
            ? {}
            : { redirect: encodeURIComponent(to.fullPath) },
        replace: true,
      };
    }

    // 检查用户信息
    if (!authStore.userInfo) {
      const userInfo = await authStore.fetchUserInfo();
      if (!userInfo) {
        await authStore.logout();
        return {
          path: USER_LOGIN_PATH,
          query: { redirect: encodeURIComponent(to.fullPath) },
          replace: true
        };
      }
    }

    // 检查是否已生成动态路由
    if (accessStore.isAccessChecked) {
      return true;
    }

    // 生成动态路由
    const userMenus = await getAllUserRouterApi();
    const { accessibleRoutes } = await generateAccess({
      roles: ['user'], // 普通用户角色
      router,
      routes: accessRoutes,
    });

    // 转换菜单格式并保存
    const accessibleMenus = userMenus.map((menu) => ({
      label: menu.meta?.title || '',
      value: String(menu.name),
      icon: menu.meta?.icon || '',
      path: menu.path
    }));
    
    // 保存路由信息
    accessStore.setMenus(accessibleMenus);
    accessStore.setRoutes(accessibleRoutes);
    accessStore.setIsAccessChecked(true);

    // 处理重定向
    const redirectPath = (from.query.redirect ??
      (to.path === DEFAULT_USER_PATH
        ? DEFAULT_USER_PATH
        : to.fullPath)) as string;

    return {
      ...router.resolve(decodeURIComponent(redirectPath)),
      replace: true,
    };
  });
}
