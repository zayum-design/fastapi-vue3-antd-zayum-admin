<script lang="ts" setup>
import { AuthenticationQrCodeLogin } from './components/';
import { LOGIN_PATH } from '@/constants';

defineOptions({ name: 'QrCodeLogin' });
</script>

<template>
  <AuthenticationQrCodeLogin :login-path="LOGIN_PATH" />
</template>
