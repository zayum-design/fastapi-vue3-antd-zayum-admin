<script setup lang="ts">
import { FormLabel, ZayumHelpTooltip } from '@/_core/ui/common-ui/shadcn-ui';
import { cn } from '@/_core/shared/utils';

interface Props {
  class?: string;
  help?: string;
  required?: boolean;
}

const props = defineProps<Props>();
</script>

<template>
  <FormLabel :class="cn('flex items-center', props.class)">
    <span v-if="required" class="text-destructive mr-[2px]">*</span>
    <slot></slot>
    <ZayumHelpTooltip v-if="help" trigger-class="size-3.5 ml-1">
      {{ help }}
    </ZayumHelpTooltip>
  </FormLabel>
</template>
