<script lang="ts" setup>
import { computed } from 'vue';

import { FullLayout } from '@/layouts/full';
import { preferences } from '@/_core/preferences';

import { $t } from '@/locales';

const appName = computed(() => preferences.app.name);
const logo = computed(() => preferences.logo.source);
</script>

<template>
  <FullLayout
    :app-name="appName"
    :logo="logo"
    :page-description="$t('authentication.pageDesc')"
    :page-title="$t('authentication.pageTitle')"
  >
    <!-- 自定义工具栏 -->
    <!-- <template #toolbar></template> -->
  </FullLayout>
</template>
