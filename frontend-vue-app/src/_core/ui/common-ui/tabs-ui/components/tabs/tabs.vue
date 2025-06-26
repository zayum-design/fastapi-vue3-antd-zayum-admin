<script lang="ts" setup>
// 引入类型定义：TabDefinition，用于描述标签的相关数据结构
import type { TabDefinition } from '@/_core/typings';

// 引入类型定义：TabConfig 和 TabsProps，分别描述单个标签配置和整个标签组件的属性类型
import type { TabConfig, TabsProps } from '../../types';

// 从 Vue 中引入 computed，用于定义响应式计算属性
import { computed } from 'vue';

// 从项目中的图标库中引入 Pin 和 X 图标
import { Pin, X } from '@/_core/ui/icons';

// 从通用 UI 组件库中引入右键菜单组件和图标组件
import { ZayumContextMenu, ZayumIcon } from '@/_core/ui/common-ui/shadcn-ui';

// 定义组件的 Props 接口，继承自 TabsProps，方便后续对标签组件属性的类型约束
interface Props extends TabsProps {}

// 定义组件选项，设置组件名称为 'ZayumTabs'，同时不继承父级组件的属性
defineOptions({
  name: 'ZayumTabs',
  // eslint-disable-next-line perfectionist/sort-objects
  inheritAttrs: false,
});

// 使用 withDefaults 和 defineProps 定义并初始化组件 props，设定默认值
const props = withDefaults(defineProps<Props>(), {
  // 默认内容区域 CSS 类名
  contentClass: 'zayum-tabs-content',
  // 默认右键菜单为空数组
  contextMenus: () => [],
  // 默认标签列表为空数组
  tabs: () => [],
});

// 定义组件发出的事件，支持关闭标签（传递标签 key）和取消固定标签（传递 TabDefinition 类型数据）
const emit = defineEmits<{
  close: [string];
  unpin: [TabDefinition];
}>();

// 使用 defineModel 定义一个响应式的 active 变量，表示当前激活的标签 key
const active = defineModel<string>('active');

// 计算属性：根据组件的 styleType 属性返回对应的 CSS 类字符串
const typeWithClass = computed(() => {
  // 定义不同风格标签对应的 CSS 类集合
  const typeClasses: Record<string, { content: string }> = {
    // brisk 风格下的样式定义
    brisk: {
      content: `h-full after:content-['']  after:absolute after:bottom-0 after:left-0 after:w-full after:h-[1.5px] after:bg-primary after:scale-x-0 after:transition-[transform] after:ease-out after:duration-300 hover:after:scale-x-100 after:origin-left [&.is-active]:after:scale-x-100 [&:not(:first-child)]:border-l last:border-r last:border-r border-border`,
    },
    // card 风格下的样式定义
    card: {
      content:
        'h-[calc(100%-6px)] rounded-md ml-2 border border-border  transition-all',
    },
    // plain 风格下的样式定义
    plain: {
      content:
        'h-full [&:not(:first-child)]:border-l last:border-r border-border',
    },
  };

  // 根据 props 中的 styleType 返回对应的样式，若未指定则默认使用 plain 风格；若找不到则返回空字符串
  return typeClasses[props.styleType || 'plain'] || { content: '' };
});

// 计算属性：处理传入的 tabs 数组，生成适用于内部使用的标签视图数据
const tabsView = computed(() => {
  // 遍历 props.tabs 数组，映射出每个标签的具体配置
  return props.tabs.map((tab) => {
    // 解构获取标签相关属性：fullPath、meta、name、path
    const { fullPath, meta, name, path } = tab || {};
    // 从 meta 中解构出固定标签、图标、新标签标题、是否可关闭、标题等信息
    const { affixTab, icon, newTabTitle, tabClosable, title } = meta || {};
    return {
      // 固定标签标志转换为布尔值
      affixTab: !!affixTab,
      // 如果 meta 中存在 tabClosable 属性，则取其布尔值，否则默认为 true（可关闭）
      closable: Reflect.has(meta, 'tabClosable') ? !!tabClosable : true,
      // 完整路径
      fullPath,
      // 图标，强制类型转换为 string 类型
      icon: icon as string,
      // 标签的唯一标识，优先使用 fullPath，其次为 path
      key: fullPath || path,
      // 原始 meta 数据，便于后续使用其他扩展属性
      meta,
      // 标签名称
      name,
      // 标签路径
      path,
      // 标签显示标题，优先级为 newTabTitle > title > name，并强制转换为 string 类型
      title: (newTabTitle || title || name) as string,
    } as TabConfig;
  });
});

// 定义鼠标按下事件处理函数：用于响应鼠标中键点击标签时关闭标签的操作
function onMouseDown(e: MouseEvent, tab: TabConfig) {
  // 判断条件：
  // 1. e.button === 1 表示鼠标中键点击
  // 2. 标签是可关闭的（closable 为 true）
  // 3. 标签不是固定标签（affixTab 为 false）
  // 4. 当前标签总数大于 1（防止关闭最后一个标签）
  // 5. props.middleClickToClose 为 true，表示启用了中键关闭功能
  if (
    e.button === 1 &&
    tab.closable &&
    !tab.affixTab &&
    tabsView.value.length > 1 &&
    props.middleClickToClose
  ) {
    // 阻止默认行为（例如打开链接新标签页）
    e.preventDefault();
    // 阻止事件冒泡，避免触发其他点击事件处理程序
    e.stopPropagation();
    // 触发关闭标签的事件，并传递标签的 key 值
    emit('close', tab.key);
  }
}
</script>


<template>
  <div
    :class="contentClass"
    class="relative !flex h-full w-max items-center overflow-hidden pr-6"
  >
    <TransitionGroup name="slide-left">
      <div
        v-for="(tab, i) in tabsView"
        :key="tab.key"
        :class="[
          {
            'is-active dark:bg-accent bg-primary/15': tab.key === active,
            draggable: !tab.affixTab,
            'affix-tab': tab.affixTab,
          },
          typeWithClass.content,
        ]"
        :data-index="i"
        class="tab-item [&:not(.is-active)]:hover:bg-accent translate-all group relative flex cursor-pointer select-none"
        data-tab-item="true"
        @click="active = tab.key"
        @mousedown="onMouseDown($event, tab)"
      >
        <ZayumContextMenu
          :handler-data="tab"
          :menus="contextMenus"
          :modal="false"
          item-class="pr-6"
        >
          <div class="relative flex size-full items-center">
            <!-- extra -->
            <div
              class="absolute right-1.5 top-1/2 z-[3] translate-y-[-50%] overflow-hidden"
            >
              <!-- close-icon -->
              <X
                v-show="!tab.affixTab && tabsView.length > 1 && tab.closable"
                class="hover:bg-accent stroke-accent-foreground/80 hover:stroke-accent-foreground dark:group-[.is-active]:text-accent-foreground group-[.is-active]:text-primary size-3 cursor-pointer rounded-full transition-all"
                @click.stop="() => emit('close', tab.key)"
              />
              <Pin
                v-show="tab.affixTab && tabsView.length > 1 && tab.closable"
                class="hover:bg-accent hover:stroke-accent-foreground group-[.is-active]:text-primary dark:group-[.is-active]:text-accent-foreground mt-[1px] size-3.5 cursor-pointer rounded-full transition-all"
                @click.stop="() => emit('unpin', tab)"
              />
            </div>

            <!-- tab-item-main -->
            <div
              class="text-accent-foreground group-[.is-active]:text-primary dark:group-[.is-active]:text-accent-foreground mx-3 mr-4 flex h-full items-center overflow-hidden rounded-tl-[5px] rounded-tr-[5px] pr-3 transition-all duration-300"
            >
              <ZayumIcon
                v-if="showIcon"
                :icon="tab.icon"
                class="mr-2 flex size-4 items-center overflow-hidden"
                fallback
              />

              <span class="flex-1 overflow-hidden whitespace-nowrap text-sm">
                {{ tab.title }}
              </span>
            </div>
          </div>
        </ZayumContextMenu>
      </div>
    </TransitionGroup>
  </div>
</template>
