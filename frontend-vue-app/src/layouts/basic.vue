<script lang="ts" setup>
import type { NotificationItem } from "@/layouts/widgets";

import { computed, ref, watch, onMounted } from "vue";

import { AuthenticationLoginExpiredModal } from "@/layouts/basic";
import { ZAYUM_DOC_URL, ZAYUM_GITHUB_URL } from "@/constants";
import { useWatermark } from "@/_core/hooks";
import {
  BookOpenText,
  CircleHelp,
  MdiGithub,
  RefreshIcon,
} from "@/_core/ui/icons";
import { useZayumModal } from "@/_core/ui/common-ui/popup-ui";
import { BasicLayout } from "@/layouts/basic";

import { LockScreen, Notification, UserDropdown } from "@/layouts/widgets";

import { preferences } from "@/_core/preferences";
import { useAdminAccessStore, useAdminStore } from "@/stores";
import { openWindow } from "@/_core/utils";

import { $t } from "@/locales";
import { useAuthStore } from "@/store/admin";
import LoginForm from "@/views/_core/authentication/login.vue";
import { clearAnalyticsCacheApi } from "@/api/admin";
import { 
  getNotificationsListApi, 
  markAllNotificationsReadApi, 
  clearAllNotificationsApi,
  type NotificationsApi 
} from "@/api/admin/notifications";
import { message } from "ant-design-vue";

const notifications = ref<NotificationItem[]>([]);
const loading = ref(false);

const adminStore = useAdminStore();
const authStore = useAuthStore();
const accessStore = useAdminAccessStore();
const { destroyWatermark, updateWatermark } = useWatermark();
const showDot = computed(() =>
  notifications.value.some((item) => !item.isRead)
);

// 加载通知数据
async function loadNotifications() {
  try {
    loading.value = true;
    const response = await getNotificationsListApi();
    notifications.value = response.notifications;
  } catch (error) {
    console.error('获取通知列表失败:', error);
    message.error('获取通知列表失败');
  } finally {
    loading.value = false;
  }
}

// 组件挂载时加载通知数据
onMounted(() => {
  loadNotifications();
});

// 缓存清理确认对话框
const [CacheCleanModal, cacheCleanModalApi] = useZayumModal({
  onConfirm: async () => {
    try {
      const result = await clearAnalyticsCacheApi();
      console.log('缓存清理成功:', result.message);
      // 显示成功提示
      message.success($t('ui.widgets.cache.success'));
    } catch (error) {
      console.error('缓存清理失败:', error);
      // 显示错误提示
      message.error($t('ui.widgets.cache.error'));
    }
    cacheCleanModalApi.close();
  },
});
 

const menus = computed(() => [
  {
    handler: () => { 
      cacheCleanModalApi.open();
    },
    icon: RefreshIcon,
    text: $t("ui.widgets.cache.clean"),
  },
  {
    handler: () => {
      openWindow(ZAYUM_DOC_URL, {
        target: "_blank",
      });
    },
    icon: BookOpenText,
    text: $t("ui.widgets.document"),
  },
  {
    handler: () => {
      openWindow(ZAYUM_GITHUB_URL, {
        target: "_blank",
      });
    },
    icon: MdiGithub,
    text: "GitHub",
  },
  {
    handler: () => {
      openWindow(`${ZAYUM_GITHUB_URL}/issues`, {
        target: "_blank",
      });
    },
    icon: CircleHelp,
    text: $t("ui.widgets.qa"),
  },
]);

const avatar = computed(() => {
  return adminStore.adminInfo?.avatar ?? preferences.app.defaultAvatar;
});

async function handleLogout() {
  await authStore.logout(false);
}

async function handleNoticeClear() {
  try {
    await clearAllNotificationsApi();
    notifications.value = [];
    message.success('通知已清空');
  } catch (error) {
    console.error('清空通知失败:', error);
    message.error('清空通知失败');
  }
}

async function handleMakeAll() {
  try {
    await markAllNotificationsReadApi();
    notifications.value.forEach((item) => (item.isRead = true));
    message.success('所有通知已标记为已读');
  } catch (error) {
    console.error('标记通知为已读失败:', error);
    message.error('标记通知为已读失败');
  }
}
watch(
  () => preferences.app.watermark,
  async (enable) => {
    if (enable) {
      await updateWatermark({
        content: `${adminStore.adminInfo?.username}`,
      });
    } else {
      destroyWatermark();
    }
  },
  {
    immediate: true,
  }
);
</script>

<template>
  <BasicLayout @clear-preferences-and-logout="handleLogout">
    <template #user-dropdown>
      <UserDropdown
        :avatar
        :menus
        :text="adminStore.adminInfo?.nickname"
        :description="adminStore.adminInfo?.email"
        tag-text="Pro"
        @logout="handleLogout"
      />
    </template>
    <template #notification>
      <Notification
        :dot="showDot"
        :notifications="notifications"
        @clear="handleNoticeClear"
        @make-all="handleMakeAll"
      />
    </template>
    <template #extra>
      <AuthenticationLoginExpiredModal
        v-model:open="accessStore.loginExpired"
        :avatar
      >
        <LoginForm />
      </AuthenticationLoginExpiredModal>
    </template>
    <template #lock-screen>
      <LockScreen :avatar @to-login="handleLogout" />
    </template>
  </BasicLayout>
  <CacheCleanModal
    :cancel-text="$t('common.cancel')"
    :confirm-text="$t('common.confirm')"
    :fullscreen-button="false"
    :title="$t('ui.widgets.cache.confirmTitle')"
    centered
    content-class="px-8 min-h-10"
    footer-class="border-none mb-3 mr-3"
    header-class="border-none"
  >
    <p>{{ $t("ui.widgets.cache.confirmMessage") }}</p>
  </CacheCleanModal>
</template>
