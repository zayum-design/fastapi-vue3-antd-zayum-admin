<script setup lang="ts">
import { ZayumAvatar } from '../avatar';

interface Props {
  /**
   * @zh_CN 是否收起文本
   */
  collapsed?: boolean;
  /**
   * @zh_CN Logo 跳转地址
   */
  href?: string;
  /**
   * @zh_CN Logo 文本
   */
  text: string;
}

defineOptions({
  name: 'ZayumLogo',
});

withDefaults(defineProps<Props>(), {
  collapsed: false,
  href: 'javascript:void 0',
});
</script>

<template>
  <div class="flex h-full items-center text-lg">
    <a
      :class="$attrs.class"
      :href="href"
      class="flex h-full items-center gap-2 px-3 text-lg leading-normal transition-all duration-500"
    >
      <ZayumAvatar
        :alt="text"
        src="/src/assets/logo-2.svg"
        class="relative w-8 rounded-none bg-transparent"
      />
      <span
        v-if="!collapsed"
        class="text-foreground truncate text-nowrap font-semibold"
      >
        {{ text }}
      </span>
    </a>
  </div>
</template>
