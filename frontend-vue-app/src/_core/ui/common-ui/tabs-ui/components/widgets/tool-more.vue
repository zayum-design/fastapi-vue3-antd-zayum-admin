<script lang="ts" setup>
import type { DropdownMenuProps } from '@/_core/ui/common-ui/shadcn-ui';

import { ChevronDown } from '@/_core/ui/icons';
import { ZayumDropdownMenu } from '@/_core/ui/common-ui/shadcn-ui';

defineProps<DropdownMenuProps>();
</script>

<template>
  <ZayumDropdownMenu :menus="menus" :modal="false">
    <div
      class="flex-center hover:bg-muted hover:text-foreground text-muted-foreground border-border h-full cursor-pointer border-l px-2 text-lg font-semibold"
    >
      <ChevronDown class="size-4" />
    </div>
  </ZayumDropdownMenu>
</template>
