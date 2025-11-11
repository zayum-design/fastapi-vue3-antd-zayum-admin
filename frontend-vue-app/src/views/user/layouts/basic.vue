<script lang="ts" setup>
import type { NotificationItem } from '@/layouts/widgets';

import { computed, ref, watch } from 'vue';

import { AuthenticationLoginExpiredModal } from '@/layouts/basic';
import { ZAYUM_DOC_URL, ZAYUM_GITHUB_URL } from '@/constants';
import { useWatermark } from '@/_core/hooks';
import { BookOpenText, CircleHelp, MdiGithub } from '@/_core/ui/icons';
import {
  UserBasicLayout,
} from '@/views/user/layouts/basic';

import {
  LockScreen,
  Notification,
  UserDropdown,
} from '@/layouts/widgets';

import { preferences } from '@/_core/preferences';
import { useUserStore } from '@/stores/modules/user';

import { useUserAccessStore } from '@/stores/user/access';
import { useUserAuthStore } from '@/stores/user/auth';

import { openWindow } from '@/_core/utils';

import { $t } from '@/locales';
import LoginForm from '@/views/_core/authentication/login.vue';

const notifications = ref<NotificationItem[]>([
  // {
  //   avatar: 'https://avatar.vercel.sh/vercel.svg?text=VB',
  //   date: '3小时前',
  //   isRead: true,
  //   message: '描述信息描述信息描述信息',
  //   title: '收到了 14 份新周报',
  // },
]);

const userStore = useUserStore();
const accessStore = useUserAccessStore();
const { destroyWatermark, updateWatermark } = useWatermark();
const showDot = computed(() =>
  notifications.value.some((item) => !item.isRead),
);

const menus = computed(() => [
  {
    handler: () => {
      openWindow(ZAYUM_DOC_URL, {
        target: '_blank',
      });
    },
    icon: BookOpenText,
    text: $t('ui.widgets.document'),
  },
  {
    handler: () => {
      openWindow(ZAYUM_GITHUB_URL, {
        target: '_blank',
      });
    },
    icon: MdiGithub,
    text: 'GitHub',
  },
  {
    handler: () => {
      openWindow(`${ZAYUM_GITHUB_URL}/issues`, {
        target: '_blank',
      });
    },
    icon: CircleHelp,
    text: $t('ui.widgets.qa'),
  },
]);

const avatar = computed(() => {
  return userStore.userInfo?.avatar ?? preferences.app.defaultAvatar;
});

async function handleLogout() {
  try {
    console.log('开始退出登录...');
    
    // 调用用户认证store的logout方法
    const authStore = useUserAuthStore();
    await authStore.logout();
    
    // 清除用户store中的用户信息 - 使用更可靠的方式
    userStore.userInfo = null;
    userStore.userRoles = [];
    
    // 清除水印
    destroyWatermark();
    
    // 清除通知
    notifications.value = [];
    
    console.log('退出登录完成，准备跳转到登录页面');
    
    // 跳转到登录页面
    window.location.href = '/user/login';
  } catch (error) {
    console.error('退出登录过程中发生错误:', error);
    // 即使出错也要清除本地状态并跳转
    const authStore = useUserAuthStore();
    authStore.userInfo = null;
    userStore.userInfo = null;
    userStore.userRoles = [];
    localStorage.removeItem('userProfile');
    localStorage.removeItem('userAccessToken');
    localStorage.removeItem('tokenExpireTime');
    window.location.href = '/user/login';
  }
}

function handleNoticeClear() {
  notifications.value = [];
}

function handleMakeAll() {
  notifications.value.forEach((item) => (item.isRead = true));
}
watch(
  () => preferences.app.watermark,
  async (enable) => {
    if (enable) {
      await updateWatermark({
        content: `${userStore.userInfo?.username}`,
      });
    } else {
      destroyWatermark();
    }
  },
  {
    immediate: true,
  },
);
</script>

<template>
  <UserBasicLayout @clear-preferences-and-logout="handleLogout">
    <div>dsafd</div>
    <template #user-dropdown>
      <UserDropdown
        :avatar
        :menus
        :text="userStore.userInfo?.nickname"
        :description="userStore.userInfo?.email"
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
  </UserBasicLayout>
</template>
