<script lang="ts" setup>
import * as UserAuthApi from '@/api/user/auth';

const props = defineProps<{
  modelValue: string;
  phone: string;
}>();

const emit = defineEmits(['update:modelValue']);

const handleGetCode = async () => {
  if (props.phone) {
    await UserAuthApi.getSmsCodeApi(props.phone);
  }
};
</script>

<template>
  <div class="sms-code-input">
    <ZayumInput
      :model-value="modelValue"
      @update:model-value="emit('update:modelValue', $event)"
      :placeholder="$t('authentication.smsCode')"
    />
    <ZayumButton 
      type="link" 
      @click="handleGetCode"
    >
      {{ $t('authentication.getSmsCode') }}
    </ZayumButton>
  </div>
</template>

<style scoped>
.sms-code-input {
  display: flex;
  gap: 8px;
}
</style>
