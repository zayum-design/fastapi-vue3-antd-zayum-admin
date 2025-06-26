<script lang="ts" setup>
import type {
  WorkbenchProjectItem,
  WorkbenchQuickNavItem,
  WorkbenchTrendItem,
} from './components';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import {
  WorkbenchHeader,
  WorkbenchQuickNav,
  WorkbenchTrends,
} from './components';
import { preferences } from '@/_core/preferences';
import { useUserStore } from '@/stores';
import { openWindow } from '@/utils';

const userStore = useUserStore();

// 同样，这里的 url 也可以使用以 http 开头的外部链接
const quickNavItems: WorkbenchQuickNavItem[] = [
  {
    color: '#1fdaca',
    icon: 'ion:home-outline',
    title: '首页',
    url: '/',
  },
  {
    color: '#bf0c2c',
    icon: 'ion:grid-outline',
    title: '仪表盘',
    url: '/admin/dashboard',
  },
  {
    color: '#e18525',
    icon: 'ion:layers-outline',
    title: '个人资料',
    url: '/admin/general/profile',
  },
  {
    color: '#3fb27f',
    icon: 'ion:settings-outline',
    title: '系统管理',
    url: '/admin/general/config', // 这里的 URL 是示例，实际项目中需要根据实际情况进行调整
  },
  {
    color: '#4daf1bc9',
    icon: 'ion:key-outline',
    title: '管理员规则',
    url: '/admin/admin/rule',
  },
  {
    color: '#00d8ff',
    icon: 'ion:bar-chart-outline',
    title: '分类',
    url: '/admin/general/category',
  },
];
 
const trendItems: WorkbenchTrendItem[] = userStore.userInfo?.logs?.map(log => ({
  avatar: 'svg:avatar-1',
  content: `${log.title} ${log.url}`,
  date: new Date(log.created_at).toLocaleString(),
  title: log.username,
  url: log.url,
  ip: log.ip,
  useragent: log.useragent,
  method: log.title,
  username: log.username
})) || [];

const router = useRouter();

// 这是一个示例方法，实际项目中需要根据实际情况进行调整
// This is a sample method, adjust according to the actual project requirements
function navTo(nav: WorkbenchProjectItem | WorkbenchQuickNavItem) {
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
console.log(userStore.userInfo?.logs)
</script>

<template>
  <div class="">
    <WorkbenchHeader
      :avatar="userStore.userInfo?.avatar || preferences.app.defaultAvatar"
    >
      <template #title>
        {{ $t('dashboard.workspace.morningGreeting', { name: userStore.userInfo?.nickname }) }} {{ $t('dashboard.workspace.startWorkPrompt') }}
      </template>
      <template #description>
        {{ $t('dashboard.workspace.todayDate', { 
          date: new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }),
          time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
        }) }}
      </template>
    </WorkbenchHeader>

    <div class="flex flex-col lg:flex-row">
      <div class="mr-4 w-full mt-5 lg:w-3/5"> 
        <WorkbenchTrends :items="trendItems" class="" :title="$t('dashboard.workspace.latestLogs')">
          <template #more>
            <a-button type="link" @click="router.push('/admin/admin/log')">{{ $t('dashboard.workspace.more') }}</a-button>
          </template>
        </WorkbenchTrends>
      </div>
      <div class="w-full mt-5 lg:w-2/5">
        <WorkbenchQuickNav
          :items="quickNavItems"
          class="lg:mt-0"
          :title="$t('dashboard.workspace.quickNav')"
          @click="navTo"
        />
      </div>
    </div>
  </div>
</template>
