<script lang="ts" setup>
import { ZayumSpinner } from '@/_core/ui/common-ui/shadcn-ui';

import { useContentSpinner } from './use-content-spinner';

defineOptions({ name: 'LayoutContentSpinner' });

const { spinning } = useContentSpinner();
</script>
<template>
  <ZayumSpinner :spinning="spinning" />
</template>
