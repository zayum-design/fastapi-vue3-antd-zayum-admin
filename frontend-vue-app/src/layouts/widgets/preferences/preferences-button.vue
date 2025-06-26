<script lang="ts" setup>
import { Settings } from '@/_core/ui/icons';

import { ZayumIconButton } from '@/_core/ui/common-ui/shadcn-ui';

import Preferences from './preferences.vue';

const emit = defineEmits<{ clearPreferencesAndLogout: [] }>();

function clearPreferencesAndLogout() {
  emit('clearPreferencesAndLogout');
}
</script>
<template>
  <Preferences @clear-preferences-and-logout="clearPreferencesAndLogout">
    <ZayumIconButton>
      <Settings class="text-foreground size-4" />
    </ZayumIconButton>
  </Preferences>
</template>
