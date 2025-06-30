<script lang="ts" setup>
import { computed } from 'vue';
import type { MenuRecordRaw } from '@/_core/types';
import type { MenuProps } from '@/_core/ui/common-ui/menu-ui';
import { Menu } from '@/_core/ui/common-ui/menu-ui';
import { useUserMenu } from './use-user-menu';

interface Props extends MenuProps {
  menus?: MenuRecordRaw[];
}

const props = withDefaults(defineProps<Props>(), {
  accordion: true,
  menus: undefined,
});

const emit = defineEmits<{
  open: [string, string[]];
  select: [string, string?];
}>();

const { menuItems } = useUserMenu();

const menus = computed(() => props.menus || menuItems.value);

function handleMenuSelect(key: string) {
  emit('select', key, props.mode);
}

function handleMenuOpen(key: string, path: string[]) {
  emit('open', key, path);
}
</script>

<template>
  <Menu
    :accordion="accordion"
    :collapse="collapse"
    :collapse-show-title="collapseShowTitle"
    :default-active="defaultActive"
    :menus="menus"
    :mode="mode"
    :rounded="rounded"
    :theme="theme"
    @open="handleMenuOpen"
    @select="handleMenuSelect"
  />
</template>
