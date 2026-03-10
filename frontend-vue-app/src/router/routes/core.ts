import type { RouteRecordRaw } from "vue-router";

import {
  DEFAULT_ADMIN_PATH,
  ADMIN_LOGIN_PATH,
  DEFAULT_HOME_PATH,
  ADMIN_ROUTE_PREFIX,
  USER_ROUTE_PREFIX,
  WEB_ROUTE_PREFIX,
} from "@/constants";

import { AuthPageLayout, BasicLayout, FullLayout } from "@/layouts";

import { UserPageLayout } from "@/views/user/layouts/auth";

import { UserBasicLayout } from "@/views/user/layouts";

import { $t } from "@/locales";
import Login from "@/views/_core/authentication/login.vue";
import Install from "@/views/_core/install/install.vue";

import Home from "@/views/web/home.vue";

/** 全局404页面 */
const fallbackNotFoundRoute: RouteRecordRaw = {
  component: () => import("@/views/_core/fallback/not-found.vue"),
  meta: {
    hideInBreadcrumb: true,
    hideInMenu: true,
    hideInTab: true,
    title: "404",
  },
  name: "FallbackNotFound",
  path: "/:path(.*)*",
};

/** 基本路由，这些路由是必须存在的 */
const coreRoutes: RouteRecordRaw[] = [
  /**
   * 根路由
   * 使用基础布局，作为所有页面的父级容器，子级就不必配置BasicLayout。
   * 此路由必须存在，且不应修改
   */
  {
    component: BasicLayout,
    meta: {
      hideInBreadcrumb: true,
      title: "Root",
    },
    name: "AdminRoot",
    path: "/",
    redirect: DEFAULT_HOME_PATH,
    children: [],
  },
  {
    component: FullLayout,
    meta: {
      hideInTab: true,
      title: "Installation",
    },
    name: "Installation",
    path: "/install",
    children: [
      {
        component: Install,
        meta: {
          hideInBreadcrumb: true,
          title: $t("page.install.install"),
        },
        name: "Install",
        path: "init",
      },
    ],
  },
  {
    meta: {
      hideInBreadcrumb: true,
      title: "Home",
    },
    name: "web",
    path: `/${WEB_ROUTE_PREFIX}`,
    children: [
      {
        name: "Home",
        path: "home",
        component: Home,
        meta: {
          title: "Home",
        },
      },
    ],
  },
  {
    meta: {
      icon: "ic:baseline-view-in-ar",
      title: $t("user.user"),
    },
    name: "User",
    path: `/${USER_ROUTE_PREFIX}`,
    component: UserPageLayout,
    children: [
      {
        name: "UserLogin",
        path: "login",
        component: () => import("@/views/user/authentication/login.vue"),
        meta: {
          title: $t("page.auth.login"),
        },
      },
      {
        name: "UserCodeLogin",
        path: "code-login",
        component: () => import("@/views/user/authentication/code-login.vue"),
        meta: {
          title: $t("page.auth.codeLogin"),
        },
      },
      {
        name: "UserQrCodeLogin",
        path: "qrcode-login",
        component: () => import("@/views/user/authentication/qrcode-login.vue"),
        meta: {
          title: $t("page.auth.qrcodeLogin"),
        },
      },
      {
        name: "UserForgetPassword",
        path: "forget-password",
        component: () =>
          import("@/views/user/authentication/forget-password.vue"),
        meta: {
          title: $t("page.auth.forgetPassword"),
        },
      },
      {
        name: "UserRegister",
        path: "register",
        component: () => import("@/views/user/authentication/register.vue"),
        meta: {
          title: $t("page.auth.register"),
        },
      },
    ],
  },
  {
    name: "UserCenter",
    path: `/${USER_ROUTE_PREFIX}/home`,
    component: UserBasicLayout,
    children: [],
  },
  {
    component: BasicLayout,
    meta: {
      hideInBreadcrumb: true,
      title: "Admin",
    },
    name: "admin-language-manager",
    path: `/${ADMIN_ROUTE_PREFIX}`,
    redirect: DEFAULT_ADMIN_PATH,
    children: [
      {
        name: "LanguageManager",
        path: "language-manager",
        component: () => import("@/views/_core/general/language-manager.vue"),
        meta: {
          icon: "mdi:translate",
          title: $t("general.language_manager"),
        },
      },
    ],
  },
  {
    component: AuthPageLayout,
    meta: {
      hideInTab: true,
      title: "Authentication",
    },
    name: "Authentication",
    path: `/${ADMIN_ROUTE_PREFIX}`,
    redirect: ADMIN_LOGIN_PATH,
    children: [
      {
        name: "Login",
        path: "login",
        component: Login,
        meta: {
          title: $t("page.auth.login"),
        },
      },
    ],
  },
];

export { coreRoutes, fallbackNotFoundRoute };
