<script setup lang="ts">
import type {
  AvatarFallbackProps,
  AvatarImageProps,
  AvatarRootProps,
} from 'radix-vue';
import type { ClassType } from '@/_core/typings';
import { computed } from 'vue';
import { Avatar, AvatarFallback, AvatarImage } from '@/_core/ui/common-ui/shadcn-ui/ui';
// 默认图片路径 
import defaultImage from '@/assets/avatar.png';

interface Props extends AvatarFallbackProps, AvatarImageProps, AvatarRootProps {
  alt?: string;
  class?: ClassType;
  dot?: boolean;
  dotClass?: ClassType;
}

defineOptions({
  inheritAttrs: false,
});

const props = withDefaults(defineProps<Props>(), {
  alt: 'avatar',
  as: 'button',
  dot: false,
  dotClass: 'bg-green-500',
});

const text = computed(() => {
  return props.alt.slice(-2).toUpperCase();
});


// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.src = defaultImage;
  // 强制显示图片元素
  img.style.display = 'block';
  // 防止无限循环，如果默认图片也加载失败
  img.onerror = null;
};
</script>

<template>
  <div :class="props.class" class="relative flex flex-shrink-0 items-center">
    <Avatar class="size-full">
      <AvatarImage 
        :alt="alt" 
        :src="src" 
        @error="handleImageError"
      />
      <AvatarFallback>{{ text }}</AvatarFallback>
    </Avatar>
    <span
      v-if="dot"
      :class="dotClass"
      class="border-background absolute bottom-0 right-0 size-3 rounded-full border-2"
    >
    </span>
  </div>
</template>
