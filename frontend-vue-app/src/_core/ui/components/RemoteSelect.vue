<template>
  <a-select
    v-model:value="selectedValue"
    class="w-full"
    :disabled="disabled"
    @change="handleChange"
  >
    <a-select-option v-for="item in options" :key="item.value" :value="item.value">
      {{ item.name }}
    </a-select-option>
  </a-select>
</template>

<script lang="ts" setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue';
import { $t } from "@/locales";

interface SelectOptionData {
  name: string;
  value: string | number;
}

// 定义 props
const props = defineProps<{
  requestFn: () => Promise<SelectOptionData[]>; // 获取选项的函数
  defaultValue?: string | number; // 默认值
  disabled?: boolean; // 是否禁用
  includeZeroOption?: boolean; // 是否包括0选项
}>();

// 定义 emits
const emit = defineEmits<{
  (event: 'change', value: string | number | null): void; // 触发change事件
}>();

// 响应式数据
const selectedValue = ref<string | number | null>(props.defaultValue);
const options = ref<SelectOptionData[]>([]);

// 获取数据
const fetchOptions = async () => {
  try {
    const data = await props.requestFn();
    if (props.includeZeroOption) {
      data.unshift({ name: $t('None'), value: 0 });
    }
    options.value = data;
    if (!props.defaultValue && data.length > 0) {
      selectedValue.value = data[0].value;
    }
  } catch (error) {
    console.error('Error fetching options:', error);
  }
};

// 组件挂载时获取数据
onMounted(fetchOptions);

// 处理 @change 事件
const handleChange = (value: string | number | null) => {
  emit('change', value); // 直接触发 change 事件
};
</script>

<style scoped>
/* 可以根据需要加样式 */
</style>
