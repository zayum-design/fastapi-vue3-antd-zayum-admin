```vue
<script setup lang="ts">
/*
  该部分代码为使用 Vue 3 的 <script setup> 语法编写的组件脚本部分，
  使用 TypeScript 进行类型检查，同时结合了 Radix Vue 和自定义 UI 组件。
*/

// 从 'radix-vue' 导入组件相关的类型，主要用于定义组件的 Props 和 Emits 类型
import type {
  ContextMenuContentProps, // 定义 ContextMenuContent 组件的 props 类型
  ContextMenuRootEmits, // 定义 ContextMenu 根组件的 emits 类型
  ContextMenuRootProps, // 定义 ContextMenu 根组件的 props 类型
} from "radix-vue";

// 导入 ClassType 类型，用于定义 CSS 类相关的类型
import type { ClassType } from "@/_core/typings";

// 导入自定义的上下文菜单项接口，定义每个菜单项的数据结构
import type { IContextMenuItem } from "./interface";

// 从 Vue 中导入 computed 函数，用于定义响应式计算属性
import { computed } from "vue";

// 从 'radix-vue' 中导入 useForwardPropsEmits 函数，用于转发 props 和 emits 到子组件
import { useForwardPropsEmits } from "radix-vue";

// 从自定义 UI 库导入各个上下文菜单组件
import {
  ContextMenu, // 上下文菜单根组件
  ContextMenuContent, // 上下文菜单的内容容器组件
  ContextMenuItem, // 上下文菜单项组件
  ContextMenuSeparator, // 菜单项分隔线组件
  ContextMenuShortcut, // 显示菜单快捷键的组件
  ContextMenuTrigger, // 用于触发上下文菜单的组件
} from "../../ui/context-menu";

// 定义组件的 props，类型为 ContextMenuRootProps 与扩展的自定义属性
const props = defineProps<
  ContextMenuRootProps & {
    class?: ClassType; // 根组件的 CSS 类
    contentClass?: ClassType; // 菜单内容容器的 CSS 类
    contentProps?: ContextMenuContentProps; // 传递给 ContextMenuContent 的额外属性
    handlerData?: Record<string, any>; // 传递给事件处理函数的数据
    itemClass?: ClassType; // 每个菜单项的 CSS 类
    menus: (data: any) => IContextMenuItem[]; // 函数，根据 handlerData 生成菜单项数组
  }
>();

// 定义组件的 emits，类型为 ContextMenuRootEmits
const emits = defineEmits<ContextMenuRootEmits>();

// 定义 delegatedProps 计算属性，用于过滤 props 中不需要转发的属性，只保留需要传递给 ContextMenu 组件的 props
const delegatedProps = computed(() => {
  // 通过对象解构，从 props 中提取出不需要转发的属性，并将剩余属性存入 delegated 对象中
  const {
    class: _cls, // 忽略 class 属性
    contentClass: _, // 忽略 contentClass 属性
    contentProps: _cProps, // 忽略 contentProps 属性
    itemClass: _iCls, // 忽略 itemClass 属性
    ...delegated // 剩余的属性将被转发
  } = props;

  return delegated;
});

// 使用 useForwardPropsEmits 函数，将 delegatedProps 和 emits 绑定后传递给子组件
const forwarded = useForwardPropsEmits(delegatedProps, emits);

// 定义 menusView 计算属性，根据传入的 handlerData 调用 menus 函数生成菜单项数组
const menusView = computed(() => {
  // 当 menus 函数存在时，传入 handlerData 得到菜单项数组
  return props.menus?.(props.handlerData);
});

// 定义点击菜单项时的事件处理函数
function handleClick(menu: IContextMenuItem) {
  // 如果菜单项处于禁用状态，则不执行任何操作
  if (menu.disabled) {
    return;
  }
  // 否则调用菜单项中定义的 handler 函数，并传入 handlerData
  menu?.handler?.(props.handlerData);
}
</script>

<template>
  <!-- ContextMenu 组件为上下文菜单的根容器，使用 forwarded 绑定所有转发的 props 与 emits -->
  <ContextMenu v-bind="forwarded">
    <!-- ContextMenuTrigger 组件用于指定触发上下文菜单的区域，这里通过 as-child 使包裹的 slot 元素作为触发器 -->
    <ContextMenuTrigger as-child>
      <slot></slot>
    </ContextMenuTrigger>
    <!-- ContextMenuContent 组件定义了菜单的显示内容 -->
    <ContextMenuContent
      :class="contentClass"
      v-bind="contentProps"
      class="side-content z-popup"
    >
      <!-- 使用 v-for 遍历 menusView 数组，生成每个菜单项，使用菜单项的 key 作为唯一标识 -->
      <template v-for="menu in menusView" :key="menu.key">
        <!-- ContextMenuItem 组件代表单个菜单项 -->
        <ContextMenuItem
          :class="itemClass"
          :disabled="menu.disabled"
          :inset="menu.inset || !menu.icon"
          class="cursor-pointer"
          @click="handleClick(menu)"
        >
          <!-- 如果菜单项定义了 icon，则使用动态组件显示图标 -->
          <component
            :is="menu.icon"
            v-if="menu.icon"
            class="mr-2 size-4 text-lg"
          />

          <!-- 显示菜单项的文本 -->
          {{ menu.text }}
          <!-- 如果菜单项定义了快捷键，则显示 ContextMenuShortcut 组件 -->
          <ContextMenuShortcut v-if="menu.shortcut">
            {{ menu.shortcut }}
          </ContextMenuShortcut>
        </ContextMenuItem>
        <!-- 如果菜单项配置了分隔线，则显示 ContextMenuSeparator 组件 -->
        <ContextMenuSeparator v-if="menu.separator" />
      </template>
    </ContextMenuContent>
  </ContextMenu>
</template>
```
