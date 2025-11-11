import type { Router } from "vue-router";
import { DEFAULT_ADMIN_PATH, ADMIN_LOGIN_PATH } from "@/constants";
import { useAdminAccessStore, useAdminStore } from "@/stores";
import { useAuthStore } from "@/store/admin";
import { generateAccess } from "../access";
import { accessRoutes, coreRouteNames } from "@/router/routes";

/**
 * 管理员路由守卫配置
 * @param router 
 */
export function setupAdminGuard(router: Router) {
  router.beforeEach(async (to, from) => {
    const accessStore = useAdminAccessStore();
    const adminStore = useAdminStore();
    const authStore = useAuthStore();

    // 初始化登录过期检查
    if (!accessStore.expiryTimer && accessStore.adminAccessToken && accessStore.loginTime) {
      accessStore.initExpiryCheck();
    }

    // 基本路由，这些路由不需要进入权限拦截
    if (coreRouteNames.includes(to.name as string)) {
      if (to.path === ADMIN_LOGIN_PATH && accessStore.adminAccessToken) {
        return decodeURIComponent(
          (to.query?.redirect as string) || DEFAULT_ADMIN_PATH
        );
      }
      return true;
    }

    // adminAccessToken 检查
    if (!accessStore.adminAccessToken) {
      // 明确声明忽略权限访问权限，则可以访问
      if (to.meta.ignoreAccess) {
        return true;
      }

      // 没有访问权限，跳转登录页面
      if (to.fullPath !== ADMIN_LOGIN_PATH) {
        return {
          path: ADMIN_LOGIN_PATH,
          query:
            to.fullPath === DEFAULT_ADMIN_PATH
              ? {}
              : { redirect: encodeURIComponent(to.fullPath) },
          replace: true,
        };
      }
      return to;
    }

    // 检查登录是否过期
    if (accessStore.checkLoginExpiry()) {
      console.log('登录已过期，自动退出登录');
      accessStore.setLoginExpired(true);
      await authStore.logout(false);
      return {
        path: ADMIN_LOGIN_PATH,
        query: { redirect: encodeURIComponent(to.fullPath) },
        replace: true,
      };
    }

    // 是否已经生成过动态路由
    if (accessStore.isAccessChecked) {
      return true;
    }

    // 生成路由表
    const adminInfo = adminStore.adminInfo || (await authStore.fetchAdminInfo());
    if (!adminInfo) {
      return {
        path: ADMIN_LOGIN_PATH,
        query: { redirect: encodeURIComponent(to.fullPath) },
        replace: true
      };
    }
    const adminGroupId = adminInfo.groupId;

    // 生成菜单和路由
    const { accessibleMenus, accessibleRoutes } = await generateAccess({
      roles: [String(adminGroupId)],
      router,
      routes: accessRoutes,
    });

    // 保存菜单信息和路由信息
    accessStore.setAccessMenus(accessibleMenus);
    accessStore.setAccessRoutes(accessibleRoutes);
    accessStore.setIsAccessChecked(true);
    const redirectPath = (from.query.redirect ??
      (to.path === DEFAULT_ADMIN_PATH
        ? DEFAULT_ADMIN_PATH
        : to.fullPath)) as string;

    return {
      ...router.resolve(decodeURIComponent(redirectPath)),
      replace: true,
    };
  });
}
