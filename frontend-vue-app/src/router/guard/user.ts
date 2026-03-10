import type { Router } from "vue-router";
import { USER_LOGIN_PATH, DEFAULT_USER_PATH, USER_ROUTE_PREFIX } from "@/constants";
import { useUserAccessStore } from "@/stores/user/access";
import { useUserAuthStore } from "@/stores/user/auth";
import { generateUserAccess } from "../access-user";
import { accessRoutes } from "@/router/routes";


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
    if (!to.path.startsWith(`/${USER_ROUTE_PREFIX}`)) {
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
    // 检查缓存的菜单路径是否正确（以 /user 开头）
    console.log('[User Guard] accessMenus:', accessStore.accessMenus.map(m => m.path));
    console.log('[User Guard] isAccessChecked:', accessStore.isAccessChecked);
    
    const hasValidMenus = accessStore.accessMenus.length > 0 && 
      accessStore.accessMenus.every(menu => menu.path?.startsWith('/user'));
    
    console.log('[User Guard] hasValidMenus:', hasValidMenus);
    
    if (accessStore.isAccessChecked && hasValidMenus) {
      console.log('[User Guard] using cached menus');
      return true;
    }
    
    // 如果菜单路径不正确，清除缓存重新获取
    if (!hasValidMenus) {
      console.log('[User Guard] 菜单路径不正确，清除缓存重新获取...');
      accessStore.setAccessMenus([]);
      accessStore.setIsAccessChecked(false);
    }

    // 生成动态路由和菜单
    const { accessibleMenus, accessibleRoutes } = await generateUserAccess({
      roles: ['user'], // 普通用户角色
      router,
      routes: accessRoutes,
    });

    // 调试输出
    console.log('[User Guard] Generated routes:', accessibleRoutes.map(r => ({
      path: r.path,
      name: r.name,
      component: r.component ? 'defined' : 'undefined',
      children: r.children?.map(c => ({ path: c.path, name: c.name, component: c.component ? 'defined' : 'undefined' }))
    })));
    console.log('[User Guard] Generated menus:', accessibleMenus.map(m => ({ 
      path: m.path, 
      name: m.name,
      show: m.show,
      hasChildren: !!m.children && m.children.length > 0
    })));

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
