<script lang="ts" setup>
import type { ZayumFormSchema } from '@/_core/ui/common-ui';
import type { Recordable } from '@/_core/types';

import { computed, ref } from 'vue';

import { z } from '@/_core/ui/common-ui';
import { AuthenticationForgetPassword } from './components';

import { $t } from '@/locales';

defineOptions({ name: 'ForgetPassword' });

const loading = ref(false);

const formSchema = computed((): ZayumFormSchema[] => {
  return [
    {
      component: 'ZayumInput',
      componentProps: {
        placeholder: 'yixiniis@foxmail.com',
      },
      fieldName: 'email',
      label: $t('authentication.email'),
      rules: z
        .string()
        .min(1, { message: $t('authentication.emailTip') })
        .email($t('authentication.emailValidErrorTip')),
    },
  ];
});

function handleSubmit(value: Recordable<any>) {
  // eslint-disable-next-line no-console
  console.log('reset email:', value);
}
</script>

<template>
  <AuthenticationForgetPassword
    :form-schema="formSchema"
    :loading="loading"
    @submit="handleSubmit"
  />
</template>
