<script setup lang="ts">
/*
  使用 <script setup> 语法糖，并指定使用 TypeScript 语言。
*/

// 从 '@/_core/typings' 导入 TabDefinition 类型定义
import type { TabDefinition } from '@/_core/typings';

// 从 '../../types' 导入 TabConfig 和 TabsProps 类型定义
import type { TabConfig, TabsProps } from '../../types';

// 从 Vue 中导入 computed 和 ref，computed 用于创建计算属性，ref 用于创建响应式引用
import { computed, ref } from 'vue';

// 从 '@/_core/ui/icons' 导入 Pin 和 X 图标组件
import { Pin, X } from '@/_core/ui/icons';

// 从 '@/_core/ui/common-ui/shadcn-ui' 导入 ZayumContextMenu 和 ZayumIcon 组件
import { ZayumContextMenu, ZayumIcon } from '@/_core/ui/common-ui/shadcn-ui';

// 定义组件的 Props 接口，继承自 TabsProps 类型
interface Props extends TabsProps {}

// 使用 defineOptions 定义组件选项
defineOptions({
  name: 'ZayumTabsChrome', // 设置组件名称为 'ZayumTabsChrome'
  // eslint-disable-next-line perfectionist/sort-objects
  inheritAttrs: false, // 不继承父级的非 prop 属性
});

// 定义组件的 props，并使用 withDefaults 设置默认值
const props = withDefaults(defineProps<Props>(), {
  contentClass: 'zayum-tabs-content', // 默认内容区域的 class
  contextMenus: () => [],             // 默认上下文菜单为空数组
  gap: 7,                             // 默认 gap 值为 7
  tabs: () => [],                     // 默认 tabs 数组为空
});

// 定义组件的事件发射器 emit，声明 close 和 unpin 事件
const emit = defineEmits<{
  close: [string];           // close 事件接收一个 string 类型的参数
  unpin: [TabDefinition];    // unpin 事件接收一个 TabDefinition 类型的参数
}>();

// 使用 defineModel 定义双向绑定的 active 属性，类型为 string
const active = defineModel<string>('active');

// 定义两个响应式引用，用于存储 DOM 元素引用
const contentRef = ref();
const tabRef = ref();

// 定义计算属性 style，根据 props.gap 动态生成 CSS 变量 --gap
const style = computed(() => {
  const { gap } = props;
  return {
    '--gap': `${gap}px`, // 将 gap 值转换为像素单位的字符串
  };
});

// 定义计算属性 tabsView，用于生成经过处理的 tabs 配置数组
const tabsView = computed(() => {
  return props.tabs.map((tab) => {
    // 对每个 tab 进行解构赋值，获取 fullPath、meta、name 和 path
    const { fullPath, meta, name, path } = tab || {};
    // 从 meta 中进一步解构出 affixTab、icon、newTabTitle、tabClosable 和 title
    const { affixTab, icon, newTabTitle, tabClosable, title } = meta || {};
    return {
      // affixTab：转换为布尔值，表示是否为固定 tab
      affixTab: !!affixTab,
      // closable：如果 meta 中存在 tabClosable 属性，则转换为布尔值，否则默认为 true（可关闭）
      closable: Reflect.has(meta, 'tabClosable') ? !!tabClosable : true,
      fullPath, // tab 的完整路径
      icon: icon as string, // 图标，强制转换为 string 类型
      key: fullPath || path, // 唯一标识符，优先使用 fullPath，否则使用 path
      meta, // 原始的 meta 对象
      name, // tab 的名称
      path, // tab 的路径
      // title：显示标题，优先使用 newTabTitle，其次是 title，最后使用 name，并强制转换为 string 类型
      title: (newTabTitle || title || name) as string,
    } as TabConfig;
  });
});

// 定义鼠标按下事件处理函数 onMouseDown
function onMouseDown(e: MouseEvent, tab: TabConfig) {
  // 判断条件：
  // 1. 鼠标按键为中键 (e.button === 1)
  // 2. 当前 tab 可关闭 (tab.closable 为 true)
  // 3. 当前 tab 不是固定 tab (tab.affixTab 为 false)
  // 4. tabsView 数组中的 tab 数量大于 1（确保至少有一个 tab）
  // 5. 允许中键关闭操作 (props.middleClickToClose 为 true)
  if (
    e.button === 1 &&
    tab.closable &&
    !tab.affixTab &&
    tabsView.value.length > 1 &&
    props.middleClickToClose
  ) {
    // 阻止默认的鼠标中键行为（例如滚动）
    e.preventDefault();
    // 阻止事件进一步冒泡
    e.stopPropagation();
    // 触发 close 事件，并传递 tab 的 key 作为参数
    emit('close', tab.key);
  }
}
</script>


<template>
  <div
    ref="contentRef"
    :class="contentClass"
    :style="style"
    class="tabs-chrome !flex h-full w-max overflow-y-hidden pr-6"
  >
    <TransitionGroup name="slide-left">
      <div
        v-for="(tab, i) in tabsView"
        :key="tab.key"
        ref="tabRef"
        :class="[
          {
            'is-active': tab.key === active,
            draggable: !tab.affixTab,
            'affix-tab': tab.affixTab,
          },
        ]"
        :data-active-tab="active"
        :data-index="i"
        class="tabs-chrome__item draggable translate-all group relative -mr-3 flex h-full select-none items-center"
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
          <div class="relative size-full px-1">
            <!-- divider -->
            <div
              v-if="i !== 0 && tab.key !== active"
              class="tabs-chrome__divider bg-border absolute left-[var(--gap)] top-1/2 z-0 h-4 w-[1px] translate-y-[-50%] transition-all"
            ></div>
            <!-- background -->
            <div
              class="tabs-chrome__background absolute z-[-1] size-full px-[calc(var(--gap)-1px)] py-0 transition-opacity duration-150"
            >
              <div
                class="tabs-chrome__background-content group-[.is-active]:bg-primary/15 dark:group-[.is-active]:bg-accent h-full rounded-tl-[var(--gap)] rounded-tr-[var(--gap)] duration-150"
              ></div>
              <svg
                class="tabs-chrome__background-before group-[.is-active]:fill-primary/15 dark:group-[.is-active]:fill-accent absolute bottom-0 left-[-1px] fill-transparent transition-all duration-150"
                height="7"
                width="7"
              >
                <path d="M 0 7 A 7 7 0 0 0 7 0 L 7 7 Z" />
              </svg>
              <svg
                class="tabs-chrome__background-after group-[.is-active]:fill-primary/15 dark:group-[.is-active]:fill-accent absolute bottom-0 right-[-1px] fill-transparent transition-all duration-150"
                height="7"
                width="7"
              >
                <path d="M 0 0 A 7 7 0 0 0 7 7 L 0 7 Z" />
              </svg>
            </div>

            <!-- extra -->
            <div
              class="tabs-chrome__extra absolute right-[var(--gap)] top-1/2 z-[3] size-4 translate-y-[-50%]"
            >
              <!-- close-icon -->
              <X
                v-show="!tab.affixTab && tabsView.length > 1 && tab.closable"
                class="hover:bg-accent stroke-accent-foreground/80 hover:stroke-accent-foreground text-accent-foreground/80 group-[.is-active]:text-accent-foreground mt-[2px] size-3 cursor-pointer rounded-full transition-all"
                @click.stop="() => emit('close', tab.key)"
              />
              <Pin
                v-show="tab.affixTab && tabsView.length > 1 && tab.closable"
                class="hover:text-accent-foreground text-accent-foreground/80 group-[.is-active]:text-accent-foreground mt-[1px] size-3.5 cursor-pointer rounded-full transition-all"
                @click.stop="() => emit('unpin', tab)"
              />
            </div>

            <!-- tab-item-main -->
            <div
              class="tabs-chrome__item-main group-[.is-active]:text-primary dark:group-[.is-active]:text-accent-foreground text-accent-foreground z-[2] mx-[calc(var(--gap)*2)] my-0 flex h-full items-center overflow-hidden rounded-tl-[5px] rounded-tr-[5px] pl-2 pr-4 duration-150"
            >
              <ZayumIcon
                v-if="showIcon"
                :icon="tab.icon"
                class="mr-1 flex size-4 items-center overflow-hidden"
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

<style scoped>
.tabs-chrome {
  &__item:not(.dragging) {
    @apply cursor-pointer;

    &:hover:not(.is-active) {
      & + .tabs-chrome__item {
        .tabs-chrome__divider {
          @apply opacity-0;
        }
      }

      .tabs-chrome__divider {
        @apply opacity-0;
      }

      .tabs-chrome__background {
        @apply pb-[2px];

        &-content {
          @apply mx-[2px];
        }
      }
    }

    &.is-active {
      @apply z-[2];

      & + .tabs-chrome__item {
        .tabs-chrome__divider {
          @apply opacity-0;
        }
      }
    }
  }
}
</style>
