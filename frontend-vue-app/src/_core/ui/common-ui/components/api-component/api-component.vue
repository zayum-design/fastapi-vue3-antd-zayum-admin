<script lang="ts" setup>
// 引入Vue相关类型和工具函数
import type { Component } from 'vue';
import type { AnyPromiseFunction } from '@/_core/typings';

// 引入Vue的组合式API
import { computed, ref, unref, useAttrs, watch } from 'vue';

// 引入自定义图标组件
import { LoaderCircle } from '@/_core/ui/icons/icons';

// 引入工具函数
import { get, isEqual, isFunction } from '@/_core/shared/utils';
import { objectOmit } from '@vueuse/core';

// 定义选项项的类型
type OptionsItem = {
  [name: string]: any;
  children?: OptionsItem[];
  disabled?: boolean;
  label?: string;
  value?: string; 
};

// 定义组件的Props接口
interface Props {
  /** 组件 */
  component: Component;
  /** 是否将value从数字转为string */
  numberToString?: boolean;
  /** 获取options数据的函数 */
  api?: (arg?: any) => Promise<OptionsItem[] | Record<string, any>>;
  /** 传递给api的参数 */
  params?: Record<string, any>;
  /** 从api返回的结果中提取options数组的字段名 */
  resultField?: string;
  /** label字段名 */
  labelField?: string;
  /** children字段名，需要层级数据的组件可用 */
  childrenField?: string;
  /** value字段名 */
  valueField?: string;
  /** 组件接收options数据的属性名 */
  optionsPropName?: string;
  /** 是否立即调用api */
  immediate?: boolean;
  /** 每次`visibleEvent`事件发生时都重新请求数据 */
  alwaysLoad?: boolean;
  /** 在api请求之前的回调函数 */
  beforeFetch?: AnyPromiseFunction<any, any>;
  /** 在api请求之后的回调函数 */
  afterFetch?: AnyPromiseFunction<any, any>;
  /** 直接传入选项数据，也作为api返回空数据时的后备数据 */
  options?: OptionsItem[];
  /** 组件的插槽名称，用来显示一个"加载中"的图标 */
  loadingSlot?: string;
  /** 触发api请求的事件名 */
  visibleEvent?: string;
  /** 组件的v-model属性名，默认为modelValue。部分组件可能为value */
  modelPropName?: string;
}

// 定义组件的选项
defineOptions({ name: 'ApiComponent', inheritAttrs: false });

// 定义Props的默认值
const props = withDefaults(defineProps<Props>(), {
  labelField: 'label',
  valueField: 'value',
  childrenField: '',
  optionsPropName: 'options',
  resultField: '',
  visibleEvent: '',
  numberToString: false,
  params: () => ({}),
  immediate: true,
  alwaysLoad: false,
  loadingSlot: '',
  beforeFetch: undefined,
  afterFetch: undefined,
  modelPropName: 'modelValue',
  api: undefined,
  options: () => [],
});

// 定义组件的事件
const emit = defineEmits<{
  optionsChange: [OptionsItem[]];
}>();

// 定义v-model绑定的值
const modelValue = defineModel({ default: '' });

// 获取组件的属性
const attrs = useAttrs();

// 定义响应式变量
const refOptions = ref<OptionsItem[]>([]);
const loading = ref(false);
// 首次是否加载过了
const isFirstLoaded = ref(false);

// 计算属性：获取处理后的options数据
const getOptions = computed(() => {
  const { labelField, valueField, childrenField, numberToString } = props;

  const refOptionsData = unref(refOptions);

  // 递归处理数据，将label、value、children字段转换为组件需要的格式
  function transformData(data: OptionsItem[]): OptionsItem[] {
    return data.map((item) => {
      const value = get(item, valueField);
      return {
        ...objectOmit(item, [labelField, valueField, childrenField]),
        label: get(item, labelField),
        value: numberToString ? `${value}` : value,
        ...(childrenField && item[childrenField]
          ? { children: transformData(item[childrenField]) }
          : {}),
      };
    });
  }

  const data: OptionsItem[] = transformData(refOptionsData);

  // 如果api返回的数据为空，则使用props中的options作为后备数据
  return data.length > 0 ? data : props.options;
});

// 计算属性：绑定到组件的props
const bindProps = computed(() => {
  return {
    [props.modelPropName]: unref(modelValue),
    [props.optionsPropName]: unref(getOptions),
    [`onUpdate:${props.modelPropName}`]: (val: string) => {
      modelValue.value = val;
    },
    ...objectOmit(attrs, [`onUpdate:${props.modelPropName}`]),
    ...(props.visibleEvent
      ? {
          [props.visibleEvent]: handleFetchForVisible,
        }
      : {}),
  };
});

// 请求api数据的函数
async function fetchApi() {
  let { api, beforeFetch, afterFetch, params, resultField } = props;

  // 如果api不存在或不是函数，或者正在加载中，则直接返回
  if (!api || !isFunction(api) || loading.value) {
    return;
  }
  refOptions.value = [];
  try {
    loading.value = true;
    // 如果有beforeFetch回调函数，则在请求前执行
    if (beforeFetch && isFunction(beforeFetch)) {
      params = (await beforeFetch(params)) || params;
    }
    let res = await api(params);
    // 如果有afterFetch回调函数，则在请求后执行
    if (afterFetch && isFunction(afterFetch)) {
      res = (await afterFetch(res)) || res;
    }
    isFirstLoaded.value = true;
    // 如果返回的结果是数组，则直接赋值
    if (Array.isArray(res)) {
      refOptions.value = res;
      emitChange();
      return;
    }
    // 如果指定了resultField，则从返回结果中提取options数据
    if (resultField) {
      refOptions.value = get(res, resultField) || [];
    }
    emitChange();
  } catch (error) {
    console.warn(error);
    // 重置状态
    isFirstLoaded.value = false;
  } finally {
    loading.value = false;
  }
}

// 处理visibleEvent事件的函数
async function handleFetchForVisible(visible: boolean) {
  if (visible) {
    // 如果alwaysLoad为true，则每次事件触发时都重新请求数据
    if (props.alwaysLoad) {
      await fetchApi();
    } else if (!props.immediate && !unref(isFirstLoaded)) {
      // 如果immediate为false且首次未加载过，则请求数据
      await fetchApi();
    }
  }
}

// 监听params的变化，如果变化则重新请求数据
watch(
  () => props.params,
  (value, oldValue) => {
    if (isEqual(value, oldValue)) {
      return;
    }
    fetchApi();
  },
  { deep: true, immediate: props.immediate },
);

// 触发optionsChange事件的函数
function emitChange() {
  emit('optionsChange', unref(getOptions));
}
</script>

<template>
  <!-- 动态组件 -->
  <component
    :is="component"
    v-bind="bindProps"
    :placeholder="$attrs.placeholder"
  >
    <!-- 插槽处理 -->
    <template v-for="item in Object.keys($slots)" #[item]="data">
      <slot :name="item" v-bind="data || {}"></slot>
    </template>
    <!-- 加载中的插槽 -->
    <template v-if="loadingSlot && loading" #[loadingSlot]>
      <LoaderCircle class="animate-spin" />
    </template>
  </component>
</template>