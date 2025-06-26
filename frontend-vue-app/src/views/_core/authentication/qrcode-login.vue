<script lang="ts" setup>
import { AuthenticationQrCodeLogin } from '@/views/_core/authentication/components/';
import { LOGIN_PATH } from '@/constants';

defineOptions({ name: 'QrCodeLogin' });
</script>

<template>
  <AuthenticationQrCodeLogin :login-path="LOGIN_PATH" />
</template>
