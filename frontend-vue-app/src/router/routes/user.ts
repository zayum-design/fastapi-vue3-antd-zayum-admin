import type { RouteRecordRaw } from "vue-router";

import { $t } from "@/locales";
import { USER_ROUTE_PREFIX } from "@/constants";

const userRoutes: RouteRecordRaw[] = [
  {
    meta: {
      icon: "ic:baseline-view-in-ar",
      title: $t("user.user"),
    },
    name: "User",
    path: `/${USER_ROUTE_PREFIX}`,
    children: [
      {
        name: "UserLogin",
        path: "login",
        component: () =>
          import("@/views/user/authentication/login.vue"),
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
        component: () =>
          import("@/views/user/authentication/qrcode-login.vue"),
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
      {
        name: "UserManage",
        path: `/${USER_ROUTE_PREFIX}/user`,
        component: () => import("@/views/_core/user/user.vue"),
        meta: {
          icon: "lucide:area-chart",
          title: $t("user.user_manage"),
        },
      },
      {
        name: "UserGroup",
        path: `/${USER_ROUTE_PREFIX}/group`,
        component: () => import("@/views/_core/user/group.vue"),
        meta: {
          icon: "lucide:area-chart",
          title: $t("user_group.user_group"),
        },
      },
      {
        name: "UserRule",
        path: `/${USER_ROUTE_PREFIX}/rule`,
        component: () => import("@/views/_core/user/rule.vue"),
        meta: {
          icon: "lucide:area-chart",
          title: $t("user_rule.user_rule"),
        },
      },

    ],
  },
];

export default userRoutes;
