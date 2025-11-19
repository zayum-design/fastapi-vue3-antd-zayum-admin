<script lang="ts" setup>
import type { ZayumFormSchema } from '@/_core/ui/common-ui';

import { computed, markRaw, ref } from 'vue';

import { SliderCaptcha, z } from '@/_core/ui/common-ui';
import { AuthenticationLogin } from './components';
import { $t } from '@/locales';

import { useAuthStore } from '@/store/admin';

defineOptions({ name: 'Login' });

const authStore = useAuthStore();

// 验证码相关状态
const captchaId = ref<string | null>(null);
const captchaCode = ref<string | null>(null);

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
      componentProps: {
        onSuccess: (data: any) => {
          // 当验证码验证成功时，生成模拟的验证码数据
          // 在实际项目中，这里应该调用后端API获取真实的验证码ID和代码
          captchaId.value = 'slider_captcha_' + Date.now();
          captchaCode.value = 'slider_verified';
        }
      },
      rules: z.boolean().refine((value) => value, {
        message: $t('authentication.verifyRequiredTip'),
      }),
    },
  ];
});

// 处理登录提交
const handleLogin = async (formData: any) => {
  // 添加验证码相关参数
  const loginData = {
    ...formData,
    captcha_type: 'code', // 设置为 "code" 类型，表示需要验证码验证
    captcha_id: captchaId.value,
    captcha_code: captchaCode.value
  };
  
  await authStore.authLogin(loginData);
};
</script>

<template>
  <AuthenticationLogin
    :form-schema="formSchema"
    :loading="authStore.loginLoading"
    @submit="handleLogin"
  />
</template>
