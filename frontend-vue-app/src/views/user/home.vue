<template>
  <div class="home-page">
    <h1>用户主页</h1>
    <div v-if="userInfo" class="user-profile">
      <p>当前token: {{ accessStore.userAccessToken || '无' }}</p>
    <p>token是否有效: {{ accessStore.isValidToken }}</p>
      <h2>用户信息</h2>
      <p>用户名: {{ userInfo.username }}</p>
      <p>邮箱: {{ userInfo.email || '未设置' }}</p>
      <p>手机号: {{ userInfo.mobile || '未设置' }}</p>
      <p>注册时间: {{ userInfo.createdAt }}</p>
    </div>
  <div v-else>
    <p class="text-red-500">未获取到用户信息</p>
    <p>当前token: {{ accessStore.userAccessToken || '无' }}</p>
    <p>token是否有效: {{ accessStore.isValidToken }}</p>
    <p>用户信息获取状态: {{ authStore.loginLoading ? '获取中...' : '已完成' }}</p>
    <button 
      @click="authStore.fetchUserInfo()"
      class="px-4 py-2 bg-blue-500 text-white rounded"
    >
      手动获取用户信息
    </button>
  </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted } from 'vue';
import { useUserAuthStore } from '@/stores/user/auth';
import { useUserAccessStore } from '@/stores/user/access';

const authStore = useUserAuthStore();
const accessStore = useUserAccessStore();
const userInfo = computed(() => authStore.userInfo);

onMounted(async () => {
  console.log('Home mounted - checking user info');
  console.log('Current token:', accessStore.userAccessToken);
  console.log('Token valid:', accessStore.isValidToken);
  
  // 确保token已初始化
  if (!accessStore.userAccessToken) {
    accessStore.initFromStorage();
    await new Promise(resolve => setTimeout(resolve, 300)); // 增加等待时间确保初始化完成
    console.log('After init - token:', accessStore.userAccessToken);
    console.log('After init - isValid:', accessStore.isValidToken);
  }

  if (!accessStore.isValidToken) {
    console.log('Token invalid - redirecting to login');
    window.location.href = '/user/login';
    return;
  }
  
  if (!userInfo.value) {
    console.log('Token valid but no user info - fetching...');
    await authStore.fetchUserInfo();
    console.log('User info after fetch:', authStore.userInfo);
  }
});
</script>

<style scoped>
.home-page {
  @apply min-h-screen flex flex-col;
}

/* 覆盖Ant Design Vue菜单样式 */
:deep(.ant-menu) {
  background: transparent !important;
}
:deep(.ant-menu-horizontal) {
  border-bottom: none !important;
}
:deep(.ant-menu-item),
:deep(.ant-menu-item:hover),
:deep(.ant-menu-item-selected),
:deep(.ant-menu-item-active) {
  color: white !important;
}
:deep(.ant-menu-item:hover) {
  color: #bfdbfe !important; /* 浅蓝色hover效果 */
}
</style>
