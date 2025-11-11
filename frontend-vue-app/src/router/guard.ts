import type { Router } from "vue-router";

import { preferences } from "@/_core/preferences";
import { startProgress, stopProgress } from "@/_core/utils";
import { setupUserGuard } from "./guard/user";
import { setupAdminGuard } from "./guard/admin";
import { installCheck } from "@/api/admin/install";
import { ref } from "vue";

/**
 * 通用守卫配置
 * @param router
 */
function setupCommonGuard(router: Router) {
  // 记录已经加载的页面
  const loadedPaths = new Set<string>();

  router.beforeEach(async (to) => {
    to.meta.loaded = loadedPaths.has(to.path);

    // 页面加载进度条
    if (!to.meta.loaded && preferences.transition.progress) {
      startProgress();
    }
    return true;
  });

  router.afterEach((to) => {
    // 记录页面是否加载,如果已经加载，后续的页面切换动画等效果不在重复执行

    loadedPaths.add(to.path);

    // 关闭页面加载进度条
    if (preferences.transition.progress) {
      stopProgress();
    }
  });
}


/**
 * 安装路由守卫配置
 * @param router
 */
function setupInstallGuard(router: Router) {
  console.log("安装检查");
  router.beforeEach(async (to) => {
    console.log("安装检查", to.path, to);
    if (to.path === "/install/init") {
      const isInstalled = ref(true);

      const response = await installCheck();
      if (response.installed === false) {
        isInstalled.value = false;
      }
      if (isInstalled.value) {
        return "/";
      }
    }
    return true;
  });
}

/**
 * 项目守卫配置
 * @param router
 */
function createRouterGuard(router: Router) {
  /** 安装检查 */
  setupInstallGuard(router);
  /** 通用 */
  setupCommonGuard(router);
  /** 管理员路由 */
  setupAdminGuard(router);
  /** 用户路由 */
  setupUserGuard(router);
}

export { createRouterGuard };
