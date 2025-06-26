<script setup lang="ts">
import type { Recordable } from '@/_core/types';

import { computed, reactive } from 'vue';

import { $t } from '@/locales';

import { useZayumForm, z } from '@/_core/ui/common-ui/form-ui';
import { useZayumModal } from '@/_core/ui/common-ui/popup-ui';
import { ZayumAvatar, ZayumButton } from '@/_core/ui/common-ui/shadcn-ui';

interface Props {
  avatar?: string;
  text?: string;
}

defineOptions({
  name: 'LockScreenModal',
});

withDefaults(defineProps<Props>(), {
  avatar: '',
  text: '',
});

const emit = defineEmits<{
  submit: [Recordable<any>];
}>();

const [Form, { resetForm, validate, getValues }] = useZayumForm(
  reactive({
    commonConfig: {
      hideLabel: true,
      hideRequiredMark: true,
    },
    schema: computed(() => [
      {
        component: 'ZayumInputPassword' as const,
        componentProps: {
          placeholder: $t('ui.widgets.lockScreen.placeholder'),
        },
        fieldName: 'lockScreenPassword',
        formFieldProps: { validateOnBlur: false },
        label: $t('authentication.password'),
        rules: z
          .string()
          .min(1, { message: $t('ui.widgets.lockScreen.placeholder') }),
      },
    ]),
    showDefaultActions: false,
  }),
);

const [Modal] = useZayumModal({
  onConfirm() {
    handleSubmit();
  },
  onOpenChange(isOpen) {
    if (isOpen) {
      resetForm();
    }
  },
});

async function handleSubmit() {
  const { valid } = await validate();
  const values = await getValues();
  if (valid) {
    emit('submit', values?.lockScreenPassword);
  }
}
</script>

<template>
  <Modal
    :footer="false"
    :fullscreen-button="false"
    :title="$t('ui.widgets.lockScreen.title')"
  >
    <div
      class="mb-10 flex w-full flex-col items-center px-10"
      @keydown.enter.prevent="handleSubmit"
    >
      <div class="w-full">
        <div class="ml-2 flex w-full flex-col items-center">
          <ZayumAvatar
            :src="avatar"
            class="size-20"
            dot-class="bottom-0 right-1 border-2 size-4 bg-green-500"
          />
          <div class="text-foreground my-6 flex items-center font-medium">
            {{ text }}
          </div>
        </div>
        <Form />
        <ZayumButton class="mt-1 w-full" @click="handleSubmit">
          {{ $t('ui.widgets.lockScreen.screenButton') }}
        </ZayumButton>
      </div>
    </div>
  </Modal>
</template>
