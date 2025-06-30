<script lang="ts" setup>
import type { ZayumFormSchema } from '@/_core/ui/common-ui';

import { computed, markRaw } from 'vue';

import { SliderCaptcha, z } from '@/_core/ui/common-ui';
import { AuthenticationLogin } from './components';
import { $t } from '@/locales';

import { useAuthStore } from '@/store/admin';

defineOptions({ name: 'Login' });

const authStore = useAuthStore();

const formSchema = computed((): ZayumFormSchema[] => {
  return [
    {
      component: 'ZayumInput',
      componentProps: {
        placeholder: $t('authentication.usernameTip'),
      },
      fieldName: 'username',
      label: $t('authentication.username'),
      rules: z.string().min(1, { message: $t('authentication.usernameTip') }),
    },
    {
      component: 'ZayumInputPassword',
      componentProps: {
        placeholder: $t('authentication.password'),
      },
      fieldName: 'password',
      label: $t('authentication.password'),
      rules: z.string().min(1, { message: $t('authentication.passwordTip') }),
    },
    {
      component: markRaw(SliderCaptcha),
      fieldName: 'captcha',
      rules: z.boolean().refine((value) => value, {
        message: $t('authentication.verifyRequiredTip'),
      }),
    },
  ];
});
</script>

<template>
  <AuthenticationLogin
    :form-schema="formSchema"
    :loading="authStore.loginLoading"
    @submit="async (formData) => { await authStore.authLogin(formData); }"
  />
</template>
