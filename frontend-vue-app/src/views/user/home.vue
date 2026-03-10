<script lang="ts" setup>
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useUserAuthStore } from '@/stores/user/auth';
import { useUserAccessStore } from '@/stores/user/access';
import { preferences } from '@/_core/preferences';
import { useAppConfig } from '@/_core/hooks';
import { openWindow } from '@/_core/utils';
import {
  ZayumAvatar,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  ZayumIcon,
} from '@/_core/ui/common-ui/shadcn-ui';

interface QuickNavItem {
  color?: string;
  icon: string;
  title: string;
  url?: string;
}

const router = useRouter();
const { t } = useI18n();
const authStore = useUserAuthStore();
const accessStore = useUserAccessStore();
const { attachmentURL } = useAppConfig(import.meta.env, import.meta.env.PROD);

const userInfo = computed(() => authStore.userInfo);

// 处理头像URL
const displayAvatar = computed(() => {
  const avatarUrl = userInfo.value?.avatar;
  const defaultAvatar = preferences.app.defaultAvatar;

  if (!avatarUrl || avatarUrl.trim() === '') {
    return defaultAvatar;
  }

  if (avatarUrl.startsWith('http://') || avatarUrl.startsWith('https://') || avatarUrl.startsWith('/src/assets/')) {
    return avatarUrl;
  }

  if (avatarUrl.startsWith('/uploads/')) {
    return attachmentURL + avatarUrl;
  }

  return attachmentURL + (avatarUrl.startsWith('/') ? avatarUrl : '/' + avatarUrl);
});

// 用户快速导航
const quickNavItems: QuickNavItem[] = [
  {
    color: '#1fdaca',
    icon: 'ion:person-outline',
    title: t('user-center.homePage.navProfile'),
    url: '/user/profile',
  },
  {
    color: '#bf0c2c',
    icon: 'ion:wallet-outline',
    title: t('user-center.homePage.navBalance'),
    url: '/user/balance_log',
  },
  {
    color: '#e18525',
    icon: 'ion:trophy-outline',
    title: t('user-center.homePage.navScore'),
    url: '/user/score_log',
  },
  {
    color: '#3fb27f',
    icon: 'ion:settings-outline',
    title: t('user-center.homePage.navSettings'),
    url: '#',
  },
  {
    color: '#4daf1bc9',
    icon: 'ion:shield-checkmark-outline',
    title: t('user-center.homePage.navSecurity'),
    url: '#',
  },
  {
    color: '#00d8ff',
    icon: 'ion:help-circle-outline',
    title: t('user-center.homePage.navHelp'),
    url: '#',
  },
];

// 导航处理
function navTo(nav: QuickNavItem) {
  if (nav.url?.startsWith('http')) {
    openWindow(nav.url);
    return;
  }
  if (nav.url?.startsWith('/')) {
    router.push(nav.url).catch((error) => {
      console.error('Navigation failed:', error);
    });
  } else {
    console.warn(`Unknown URL for navigation item: ${nav.title} -> ${nav.url}`);
  }
}

// 格式化日期
function formatDate(dateStr?: string) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString('zh-CN');
}

// 获取问候语
const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 12) return t('user-center.homePage.morningGreeting');
  if (hour < 18) return t('user-center.homePage.afternoonGreeting');
  return t('user-center.homePage.eveningGreeting');
});

onMounted(async () => {
  // 确保token已初始化
  if (!accessStore.userAccessToken) {
    accessStore.initFromStorage();
    await new Promise(resolve => setTimeout(resolve, 300));
  }

  if (!accessStore.isValidToken) {
    window.location.href = '/user/login';
    return;
  }

  if (!userInfo.value) {
    await authStore.fetchUserInfo();
  }
});
</script>

<template>
  <div class="user-home-page p-4">
    <!-- 头部欢迎区域 -->
    <div class="card-box p-4 py-6 lg:flex">
      <ZayumAvatar :src="displayAvatar" class="size-20" />
      <div class="flex flex-col justify-center md:ml-6 md:mt-0">
        <h1 class="text-md font-semibold md:text-xl">
          {{ greeting }}，{{ userInfo?.nickname || userInfo?.username }}
        </h1>
        <span class="text-foreground/80 mt-1">
          {{ t('user-center.homePage.welcomeBack') }}
        </span>
      </div>
      <div class="mt-4 flex flex-1 justify-end md:mt-0">
        <div class="flex flex-col justify-center text-right">
          <span class="text-foreground/80">{{ t('user-center.homePage.balance') }}</span>
          <span class="text-2xl">¥{{ userInfo?.balance || 0 }}</span>
        </div>
        <div class="mx-12 flex flex-col justify-center text-right md:mx-16">
          <span class="text-foreground/80">{{ t('user-center.homePage.score') }}</span>
          <span class="text-2xl">{{ userInfo?.score || 0 }}</span>
        </div>
        <div class="mr-4 flex flex-col justify-center text-right md:mr-10">
          <span class="text-foreground/80">{{ t('user-center.homePage.level') }}</span>
          <span class="text-2xl">LV.{{ userInfo?.level || 1 }}</span>
        </div>
      </div>
    </div>

    <div class="flex flex-col lg:flex-row mt-4">
      <!-- 左侧：个人信息卡片 -->
      <div class="mr-0 w-full lg:w-3/5 lg:mr-4">
        <Card>
          <CardHeader class="py-4">
            <a-flex class="w-full" align="center" justify="space-between">
              <CardTitle class="text-lg flex-1">{{ t('user-center.homePage.userInfo') }}</CardTitle>
              <a-button type="link" @click="router.push('/user/profile')">
                {{ t('user-center.homePage.editProfile') }}
              </a-button>
            </a-flex>
          </CardHeader>
          <CardContent class="p-5 pt-0">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="flex items-center py-3 border-b border-border">
                <span class="text-foreground/60 w-24">{{ t('user-center.homePage.username') }}</span>
                <span class="text-foreground font-medium">{{ userInfo?.username || '-' }}</span>
              </div>
              <div class="flex items-center py-3 border-b border-border">
                <span class="text-foreground/60 w-24">{{ t('user-center.homePage.nickname') }}</span>
                <span class="text-foreground font-medium">{{ userInfo?.nickname || '-' }}</span>
              </div>
              <div class="flex items-center py-3 border-b border-border">
                <span class="text-foreground/60 w-24">{{ t('user-center.homePage.email') }}</span>
                <span class="text-foreground font-medium">{{ userInfo?.email || t('user-center.homePage.notSet')
                }}</span>
              </div>
              <div class="flex items-center py-3 border-b border-border">
                <span class="text-foreground/60 w-24">{{ t('user-center.homePage.mobile') }}</span>
                <span class="text-foreground font-medium">{{ userInfo?.mobile || t('user-center.homePage.notSet')
                }}</span>
              </div>
              <div class="flex items-center py-3 border-b border-border">
                <span class="text-foreground/60 w-24">{{ t('user-center.homePage.gender') }}</span>
                <span class="text-foreground font-medium">
                  {{ userInfo?.gender === 'male' ? t('user-center.homePage.male') : userInfo?.gender === 'female' ?
                    t('user-center.homePage.female') : t('user-center.homePage.notSet') }}
                </span>
              </div>
              <div class="flex items-center py-3 border-b border-border">
                <span class="text-foreground/60 w-24">{{ t('user-center.homePage.birthday') }}</span>
                <span class="text-foreground font-medium">{{ userInfo?.birthday || t('user-center.homePage.notSet')
                  }}</span>
              </div>
              <div class="flex items-center py-3 border-b border-border md:col-span-2">
                <span class="text-foreground/60 w-24">{{ t('user-center.homePage.bio') }}</span>
                <span class="text-foreground font-medium">{{ userInfo?.bio || t('user-center.homePage.notSet') }}</span>
              </div>
              <div class="flex items-center py-3 border-b border-border">
                <span class="text-foreground/60 w-24">{{ t('user-center.homePage.registerTime') }}</span>
                <span class="text-foreground font-medium">{{ formatDate(userInfo?.createdAt) }}</span>
              </div>
              <div class="flex items-center py-3 border-b border-border">
                <span class="text-foreground/60 w-24">{{ t('user-center.homePage.lastLogin') }}</span>
                <span class="text-foreground font-medium">{{ formatDate(userInfo?.loginTime) }}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- 登录统计 -->
        <Card class="mt-4">
          <CardHeader class="py-4">
            <CardTitle class="text-lg">{{ t('user-center.homePage.loginStats') }}</CardTitle>
          </CardHeader>
          <CardContent class="p-5 pt-0">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="text-center p-4 bg-muted/50 rounded-lg">
                <div class="text-2xl font-bold text-primary">{{ userInfo?.successions || 0 }}</div>
                <div class="text-sm text-foreground/60 mt-1">{{ t('user-center.homePage.consecutiveLogins') }}</div>
              </div>
              <div class="text-center p-4 bg-muted/50 rounded-lg">
                <div class="text-2xl font-bold text-primary">{{ userInfo?.maxSuccessions || 0 }}</div>
                <div class="text-sm text-foreground/60 mt-1">{{ t('user-center.homePage.maxConsecutiveLogins') }}</div>
              </div>
              <div class="text-center p-4 bg-muted/50 rounded-lg">
                <div class="text-2xl font-bold text-primary">{{ userInfo?.loginFailure || 0 }}</div>
                <div class="text-sm text-foreground/60 mt-1">{{ t('user-center.homePage.loginFailures') }}</div>
              </div>
              <div class="text-center p-4 bg-muted/50 rounded-lg">
                <div class="text-2xl font-bold text-primary">{{ userInfo?.loginIp || '-' }}</div>
                <div class="text-sm text-foreground/60 mt-1">{{ t('user-center.homePage.lastLoginIp') }}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- 右侧：快速导航 -->
      <div class="w-full mt-4 lg:mt-0 lg:w-2/5">
        <Card>
          <CardHeader class="py-4">
            <CardTitle class="text-lg">{{ t('user-center.homePage.quickNav') }}</CardTitle>
          </CardHeader>
          <CardContent class="flex flex-wrap p-0">
            <template v-for="(item, index) in quickNavItems" :key="item.title">
              <div :class="{
                'border-r-0': index % 3 === 2,
                'pb-4': index > 2,
                'border-b-0': index < 3,
              }"
                class="flex-col-center border-border group w-1/3 cursor-pointer border-r border-t py-8 hover:shadow-xl transition-all duration-300"
                @click="navTo(item)">
                <ZayumIcon :color="item.color" :icon="item.icon"
                  class="size-7 transition-all duration-300 group-hover:scale-125" />
                <span class="text-md mt-2 truncate">{{ item.title }}</span>
              </div>
            </template>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-home-page {
  min-height: 100vh;
}

.card-box {
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
  border-radius: var(--radius);
  border: 1px solid hsl(var(--border));
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
}

.flex-col-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
