<script lang="ts" setup>
import { AuthenticationQrCodeLogin } from './components';
import { ADMIN_LOGIN_PATH } from '@/constants';

defineOptions({ name: 'QrCodeLogin' });
</script>

<template>
  <AuthenticationQrCodeLogin :login-path="ADMIN_LOGIN_PATH" />
</template>
