<script setup lang="ts">
import type { SupportedLanguagesType } from '@/locales';

import { SUPPORT_LANGUAGES } from '@/constants';
import { Languages } from '@/_core/ui/icons';
import { loadLocaleMessages } from '@/locales';
import { preferences, updatePreferences } from '@/_core/preferences';

import { ZayumDropdownRadioMenu, ZayumIconButton } from '@/_core/ui/common-ui/shadcn-ui';

defineOptions({
  name: 'LanguageToggle',
});

async function handleUpdate(value: string) {
  const locale = value as SupportedLanguagesType;
  updatePreferences({
    app: {
      locale,
    },
  });
  await loadLocaleMessages(locale);
}
</script>

<template>
  <div>
    <ZayumDropdownRadioMenu
      :menus="SUPPORT_LANGUAGES"
      :model-value="preferences.app.locale"
      @update:model-value="handleUpdate"
    >
      <ZayumIconButton>
        <Languages class="text-foreground size-4" />
      </ZayumIconButton>
    </ZayumDropdownRadioMenu>
  </div>
</template>
