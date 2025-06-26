<script lang="ts" setup>
  // 导入类型定义：DrawerProps（抽屉属性）和 ExtendedDrawerApi（扩展的抽屉 API）
  import type { DrawerProps, ExtendedDrawerApi } from './drawer';

  // 从 Vue 中导入一些常用的 API，如 computed、provide、ref、useId、watch
  import { computed, provide, ref, useId, watch } from 'vue';

  // 从自定义的组合函数中导入：判断是否为移动端、优先级数值处理、简单国际化处理
  import {
    useIsMobile,
    usePriorityValues,
    useSimpleLocale,
  } from '@/_core/composables';
  
  // 导入图标组件 X
  import { X } from '@/_core/ui/icons/icons';
  
  // 导入一系列来自 shadcn-ui 的 UI 组件，这些组件用于构建抽屉内部的布局、头部、底部、按钮、提示等
  import {
    Separator,
    Sheet,
    SheetClose,
    SheetContent,
    SheetDescription,
    SheetFooter,
    SheetHeader,
    SheetTitle,
    ZayumButton,
    ZayumHelpTooltip,
    ZayumIconButton,
    ZayumLoading,
    VisuallyHidden,
  } from '@/_core/ui/common-ui/shadcn-ui';
  
  // 导入全局常量，例如主内容区的元素 ID
  import { ELEMENT_ID_MAIN_CONTENT } from '@/_core/shared/constants';
  
  // 导入全局共享状态，这里用于获取全局组件配置
  import { globalShareState } from '@/_core/shared/global-state';
  
  // 导入工具函数，用于类名拼接等
  import { cn } from '@/_core/shared/utils';

  // 定义 Props 接口，继承自 DrawerProps，并增加了一个可选属性 drawerApi，用于扩展抽屉 API
  interface Props extends DrawerProps {
    drawerApi?: ExtendedDrawerApi;
  }

  // 使用 defineProps 定义组件属性，并通过 withDefaults 设置默认值
  const props = withDefaults(defineProps<Props>(), {
    appendToMain: false,
    closeIconPlacement: 'right',
    drawerApi: undefined,
    zIndex: 1000,
  });

  // 从全局共享状态中获取组件集合，方便后续动态使用默认按钮等组件
  const components = globalShareState.getComponents();

  // 使用 useId 生成一个唯一 ID，并将该 ID 提供给子组件，键名为 'DISMISSABLE_DRAWER_ID'
  const id = useId();
  provide('DISMISSABLE_DRAWER_ID', id);

  // 创建一个 ref 引用，用于绑定抽屉内容的外层包装 DOM 元素
  const wrapperRef = ref<HTMLElement>();
  // 使用国际化组合函数获取翻译方法
  const { $t } = useSimpleLocale();
  // 使用组合函数判断是否为移动端
  const { isMobile } = useIsMobile();

  // 如果传入了 drawerApi，则调用其 useStore 方法获取状态管理对象
  const state = props.drawerApi?.useStore?.();

  // 使用 usePriorityValues 处理属性和状态，优先级合并，解构出各个属性和配置项
  const {
    appendToMain,
    cancelText,
    class: drawerClass,
    closable,
    closeOnClickModal,
    closeOnPressEscape,
    confirmLoading,
    confirmText,
    contentClass,
    description,
    footer: showFooter,
    footerClass,
    header: showHeader,
    headerClass,
    loading: showLoading,
    modal,
    openAutoFocus,
    overlayBlur,
    placement,
    showCancelButton,
    showConfirmButton,
    title,
    titleTooltip,
    zIndex,
  } = usePriorityValues(props, state);

  // 监听 showLoading 的变化，当加载状态开启时，若 wrapperRef 存在则滚动到顶部
  watch(
    () => showLoading.value,
    (v) => {
      if (v && wrapperRef.value) {
        wrapperRef.value.scrollTo({
          // 如果需要平滑滚动，可启用 behavior: 'smooth'
          top: 0,
        });
      }
    },
  );

  // 当用户在抽屉外部进行交互时的回调函数
  function interactOutside(e: Event) {
    // 如果不允许点击遮罩层关闭，则阻止默认行为
    if (!closeOnClickModal.value) {
      e.preventDefault();
    }
  }
  
  // 当用户按下 Esc 键时的回调函数
  function escapeKeyDown(e: KeyboardEvent) {
    // 如果不允许按 Esc 键关闭，则阻止默认行为
    if (!closeOnPressEscape.value) {
      e.preventDefault();
    }
  }
  
  // 当检测到鼠标指针按下且在抽屉外部时触发的回调函数
  function pointerDownOutside(e: Event) {
    const target = e.target as HTMLElement;
    // 从目标元素的 data 属性中获取 dismissableDrawer 的值
    const dismissableDrawer = target?.dataset.dismissableDrawer;
    // 如果不允许点击遮罩层关闭，或者点击的元素不属于当前抽屉（ID 不匹配），则阻止默认行为
    if (!closeOnClickModal.value || dismissableDrawer !== id) {
      e.preventDefault();
    }
  }

  // 当抽屉打开时自动聚焦的处理函数，如果不允许自动聚焦则阻止默认行为
  function handerOpenAutoFocus(e: Event) {
    if (!openAutoFocus.value) {
      e?.preventDefault();
    }
  }

  // 阻止焦点转移到抽屉外部时的默认行为
  function handleFocusOutside(e: Event) {
    e.preventDefault();
    e.stopPropagation();
  }

  // 计算属性：确定是否将抽屉内容追加到主内容区中
  const getAppendTo = computed(() => {
    // 如果 appendToMain 为 true，则返回主内容区的选择器，否则返回 undefined
    return appendToMain.value ? `#${ELEMENT_ID_MAIN_CONTENT}` : undefined;
  });
</script>

<template>
  <!-- 使用 Sheet 组件包裹整个抽屉结构 -->
  <Sheet
    :modal="false"
    :open="state?.isOpen"
    @update:open="() => drawerApi?.close()"
  >
    <!-- SheetContent 组件用于渲染抽屉的主体内容 -->
    <SheetContent
      :append-to="getAppendTo"
      :class="
        // 根据传入的 drawerClass 以及响应式判断，动态设置抽屉的宽度和高度
        cn('flex w-[520px] flex-col', drawerClass, {
          '!w-full': isMobile || placement === 'bottom' || placement === 'top',
          'max-h-[100vh]': placement === 'bottom' || placement === 'top',
        })
      "
      :modal="modal"
      :open="state?.isOpen"
      :side="placement"
      :z-index="zIndex"
      :overlay-blur="overlayBlur"
      @close-auto-focus="handleFocusOutside"
      @closed="() => drawerApi?.onClosed()"
      @escape-key-down="escapeKeyDown"
      @focus-outside="handleFocusOutside"
      @interact-outside="interactOutside"
      @open-auto-focus="handerOpenAutoFocus"
      @opened="() => drawerApi?.onOpened()"
      @pointer-down-outside="pointerDownOutside"
    >
      <!-- SheetHeader 用于显示抽屉的头部信息 -->
      <SheetHeader
        v-if="showHeader"
        :class="
          // 根据 closable 和 closeIconPlacement 等属性设置头部的布局和样式
          cn(
            '!flex flex-row items-center justify-between border-b px-6 py-5',
            headerClass,
            {
              'px-4 py-3': closable,
              'pl-2': closable && closeIconPlacement === 'left',
            },
          )
        "
      >
        <div class="flex items-center">
          <!-- 当抽屉允许关闭且关闭图标放在左侧时，显示关闭按钮 -->
          <SheetClose
            v-if="closable && closeIconPlacement === 'left'"
            as-child
            class="data-[state=open]:bg-secondary ml-[2px] cursor-pointer rounded-full opacity-80 transition-opacity hover:opacity-100 focus:outline-none disabled:pointer-events-none"
          >
            <slot name="close-icon">
              <!-- 使用 ZayumIconButton 包裹图标组件 -->
              <ZayumIconButton>
                <X class="size-4" />
              </ZayumIconButton>
            </slot>
          </SheetClose>
          <!-- 如果存在左侧关闭按钮，则在按钮和标题之间添加分隔符 -->
          <Separator
            v-if="closable && closeIconPlacement === 'left'"
            class="ml-1 mr-2 h-8"
            decorative
            orientation="vertical"
          />
          <!-- 显示抽屉标题 -->
          <SheetTitle v-if="title" class="text-left">
            <slot name="title">
              {{ title }}

              <!-- 当存在标题提示时，显示帮助提示组件 -->
              <ZayumHelpTooltip v-if="titleTooltip" trigger-class="pb-1">
                {{ titleTooltip }}
              </ZayumHelpTooltip>
            </slot>
          </SheetTitle>
          <!-- 显示抽屉描述信息 -->
          <SheetDescription v-if="description" class="mt-1 text-xs">
            <slot name="description">
              {{ description }}
            </slot>
          </SheetDescription>
        </div>

        <!-- 如果没有提供标题或描述，则通过 VisuallyHidden 确保屏幕阅读器可以识别这些元素 -->
        <VisuallyHidden v-if="!title || !description">
          <SheetTitle v-if="!title" />
          <SheetDescription v-if="!description" />
        </VisuallyHidden>

        <div class="flex-center">
          <!-- 额外的插槽区域，可用于自定义其他内容 -->
          <slot name="extra"></slot>
          <!-- 当抽屉允许关闭且关闭图标放在右侧时，显示右侧的关闭按钮 -->
          <SheetClose
            v-if="closable && closeIconPlacement === 'right'"
            as-child
            class="data-[state=open]:bg-secondary ml-[2px] cursor-pointer rounded-full opacity-80 transition-opacity hover:opacity-100 focus:outline-none disabled:pointer-events-none"
          >
            <slot name="close-icon">
              <ZayumIconButton>
                <X class="size-4" />
              </ZayumIconButton>
            </slot>
          </SheetClose>
        </div>
      </SheetHeader>
      <!-- 如果不显示头部，则使用 VisuallyHidden 隐藏但保留标题和描述的结构，确保无障碍体验 -->
      <template v-else>
        <VisuallyHidden>
          <SheetTitle />
          <SheetDescription />
        </VisuallyHidden>
      </template>
      <!-- 内容区域，绑定了 wrapperRef 用于操作滚动行为 -->
      <div
        ref="wrapperRef"
        :class="
          // 动态设置内容区的样式，当加载状态时禁止滚动
          cn('relative flex-1 overflow-y-auto p-3', contentClass, {
            'overflow-hidden': showLoading,
          })
        "
      >
        <!-- 显示加载组件，当抽屉处于加载状态时展示全屏加载效果 -->
        <ZayumLoading v-if="showLoading" class="size-full" spinning />

        <!-- 默认插槽，用于放置抽屉内部的主要内容 -->
        <slot></slot>
      </div>

      <!-- 抽屉底部区域，显示确认和取消按钮等 -->
      <SheetFooter
        v-if="showFooter"
        :class="
          // 设置底部区域的样式，包含边框和内边距，并允许自定义 footerClass
          cn(
            'w-full flex-row items-center justify-end border-t p-2 px-3',
            footerClass,
          )
        "
      >
        <!-- 在底部区域前部插入额外内容 -->
        <slot name="prepend-footer"></slot>
        <slot name="footer">
          <!-- 根据全局组件配置或默认组件渲染取消按钮 -->
          <component
            :is="components.DefaultButton || ZayumButton"
            v-if="showCancelButton"
            variant="ghost"
            @click="() => drawerApi?.onCancel()"
          >
            <slot name="cancelText">
              <!-- 使用国际化文本作为取消按钮的默认文本 -->
              {{ cancelText || $t('cancel') }}
            </slot>
          </component>

          <!-- 根据全局组件配置或默认组件渲染确认按钮 -->
          <component
            :is="components.PrimaryButton || ZayumButton"
            v-if="showConfirmButton"
            :loading="confirmLoading"
            @click="() => drawerApi?.onConfirm()"
          >
            <slot name="confirmText">
              <!-- 使用国际化文本作为确认按钮的默认文本 -->
              {{ confirmText || $t('confirm') }}
            </slot>
          </component>
        </slot>
        <!-- 在底部区域后部插入额外内容 -->
        <slot name="append-footer"></slot>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>
