<script lang="ts" setup>
import { onMounted, ref } from 'vue';

const qrCodeUrl = ref('/api/user/auth/qr_code');

// 可以添加二维码刷新逻辑
const refreshQrCode = () => {
  qrCodeUrl.value = `/api/user/auth/qr_code?t=${Date.now()}`;
};

onMounted(() => {
  // 可以设置二维码自动刷新
  // setInterval(refreshQrCode, 30000);
});
</script>

<template>
  <div class="qr-code-login">
    <img 
      :src="qrCodeUrl" 
      :alt="$t('authentication.qrLogin')"
      style="width: 200px; height: 200px"
    />
    <p class="tip">{{ $t('authentication.qrLoginTip') }}</p>
  </div>
</template>

<style scoped>
.qr-code-login {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.tip {
  color: var(--color-text-secondary);
  font-size: 12px;
}
</style>
