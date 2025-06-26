<script setup lang="ts">
import type { VNode } from 'vue';
import { computed, ref, watch, watchEffect } from 'vue';
import { usePagination } from '@/_core/hooks';
import { EmptyIcon, Grip, listIcons } from '@/_core/ui/icons';
import { $t } from '@/locales';

import {
  Button,
  Input,
  Pagination,
  PaginationEllipsis,
  PaginationFirst,
  PaginationLast,
  PaginationList,
  PaginationListItem,
  PaginationNext,
  PaginationPrev,
  ZayumIcon,
  ZayumIconButton,
  ZayumPopover,
} from '@/_core/ui/common-ui/shadcn-ui';

import { refDebounced, watchDebounced } from '@vueuse/core';
import { fetchIconsData } from './icons';

interface Props {
  pageSize?: number;
  /** 图标集的名字 */
  prefix?: string;
  /** 是否自动请求 API 获取图标数据，仅在提供 prefix 时有效 */
  autoFetchApi?: boolean;
  /** 图标列表 */
  icons?: string[];
  /** 自定义 Input 组件 */
  inputComponent?: VNode;
  /** 预览图标插槽名 */
  iconSlot?: string;
  /** Input 组件的值属性名称 */
  modelValueProp?: string;
  /** 图标样式 */
  iconClass?: string;
  /** 组件类型，支持 icon 和 input */
  type?: 'icon' | 'input';
}

// 定义 props，提供默认值
const props = withDefaults(defineProps<Props>(), {
  prefix: 'ant-design',
  pageSize: 36,
  icons: () => [],
  iconSlot: 'default',
  iconClass: 'size-4',
  autoFetchApi: true,
  modelValueProp: 'modelValue',
  inputComponent: undefined,
  type: 'input',
});

// 定义事件
const emit = defineEmits<{ change: [string] }>();

// 绑定组件的 modelValue
const modelValue = defineModel({ default: '', type: String });

const visible = ref(false); // 弹出框是否可见
const currentSelect = ref(''); // 当前选中的图标
const currentPage = ref(1); // 当前页码
const keyword = ref(''); // 搜索关键字
const keywordDebounce = refDebounced(keyword, 300); // 防抖处理的搜索关键字
const innerIcons = ref<string[]>([]); // 存储 API 获取的图标数据

// 监听 prefix 变化，自动获取图标数据
watchDebounced(
  () => props.prefix,
  async (prefix) => {
    if (prefix && prefix !== 'svg' && props.autoFetchApi) {
      innerIcons.value = await fetchIconsData(prefix);
    }
  },
  { immediate: true, debounce: 500, maxWait: 1000 },
);

// 计算当前的图标列表
const currentList = computed(() => {
  try {
    if (props.prefix) {
      if (
        props.prefix !== 'svg' &&
        props.autoFetchApi &&
        props.icons.length === 0
      ) {
        return innerIcons.value;
      }
      const icons = listIcons('', props.prefix);
      if (icons.length === 0) {
        console.warn(`未找到前缀为 ${props.prefix} 的图标`);
      }
      return icons;
    } else {
      return props.icons;
    }
  } catch (error) {
    console.error('加载图标失败:', error);
    return [];
  }
});

// 计算搜索后的图标列表
const showList = computed(() => {
  return currentList.value.filter((item) =>
    item.includes(keywordDebounce.value),
  );
});

// 使用分页功能
const { paginationList, total, setCurrentPage } = usePagination(
  showList,
  props.pageSize,
);

// 监听当前选中图标变化，更新 modelValue
watchEffect(() => {
  currentSelect.value = modelValue.value;
});

// 监听当前选中的图标，并触发 change 事件
watch(
  () => currentSelect.value,
  (v) => {
    emit('change', v);
  },
);

/**
 * 处理图标点击事件
 * @param icon 选中的图标
 */
const handleClick = (icon: string) => {
  currentSelect.value = icon;
  modelValue.value = icon;
  close();
};

/**
 * 处理分页变更
 * @param page 变更后的页码
 */
const handlePageChange = (page: number) => {
  currentPage.value = page;
  setCurrentPage(page);
};

/** 切换弹窗可见状态 */
function toggleOpenState() {
  visible.value = !visible.value;
}

/** 打开弹窗 */
function open() {
  visible.value = true;
}

/** 关闭弹窗 */
function close() {
  visible.value = false;
}

/**
 * 处理搜索输入框的值变化
 * @param v 输入值
 */
function onKeywordChange(v: string) {
  keyword.value = v;
}

// 计算搜索输入框的属性
const searchInputProps = computed(() => {
  return {
    placeholder: $t('ui.iconPicker.search'),
    [props.modelValueProp]: keyword.value,
    [`onUpdate:${props.modelValueProp}`]: onKeywordChange,
    class: 'mx-2',
  };
});

// 组件暴露的方法
defineExpose({ toggleOpenState, open, close });
</script>

<template>
  <ZayumPopover
    v-model:open="visible"
    :content-props="{ align: 'end', alignOffset: -11, sideOffset: 8 }"
    content-class="p-0 pt-3"
  >
    <template #trigger>
      <!-- 如果是 input 类型，渲染输入框 -->
      <template v-if="props.type === 'input'">
        <component
          v-if="props.inputComponent"
          :is="inputComponent"
          :[modelValueProp]="currentSelect"
          :placeholder="$t('ui.iconPicker.placeholder')"
          role="combobox"
          :aria-label="$t('ui.iconPicker.placeholder')"
          aria-expanded="visible"
          v-bind="$attrs"
        >
          <template #[iconSlot]>
            <ZayumIcon
              :icon="currentSelect || Grip"
              class="size-4"
              aria-hidden="true"
            />
          </template>
        </component>
        <div class="relative w-full" v-else>
          <Input
            v-bind="$attrs"
            v-model="currentSelect"
            :placeholder="$t('ui.iconPicker.placeholder')"
            class="h-8 w-full pr-8"
            role="combobox"
            :aria-label="$t('ui.iconPicker.placeholder')"
            aria-expanded="visible"
          />
          <ZayumIcon
            :icon="currentSelect || Grip"
            class="absolute right-1 top-1 size-6"
            aria-hidden="true"
          />
        </div>
      </template>
      <ZayumIcon
        :icon="currentSelect || Grip"
        v-else
        class="size-4"
        v-bind="$attrs"
      />
    </template>

    <div class="mb-2 flex w-full">
      <component
        v-if="inputComponent"
        :is="inputComponent"
        v-bind="searchInputProps"
      />
      <Input
        v-else
        class="mx-2 h-8 w-full"
        :placeholder="$t('ui.iconPicker.search')"
        v-model="keyword"
      />
    </div>

    <template v-if="paginationList.length > 0">
      <div class="grid max-h-[360px] w-full grid-cols-6 justify-items-center">
        <ZayumIconButton
          v-for="(item, index) in paginationList"
          :key="index"
          :tooltip="item"
          tooltip-side="top"
          @click="handleClick(item)"
        >
          <ZayumIcon
            :class="{
              'text-primary transition-all': currentSelect === item,
            }"
            :icon="item"
          />
        </ZayumIconButton>
      </div>
    </template>

    <template v-else>
      <div class="flex-col-center text-muted-foreground min-h-[150px] w-full">
        <EmptyIcon class="size-10" />
        <div class="mt-1 text-sm">{{ $t('common.noData') }}</div>
      </div>
    </template>
  </ZayumPopover>
</template>
