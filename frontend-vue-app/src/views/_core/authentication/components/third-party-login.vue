<script setup lang="ts">
import { MdiGithub, MdiGoogle, MdiQqchat, MdiWechat } from '@/_core/ui/icons';
import { $t } from '@/locales';

import { ZayumIconButton } from '@/_core/ui/common-ui/shadcn-ui';

defineOptions({
  name: 'ThirdPartyLogin',
});
</script>

<template>
  <div class="w-full sm:mx-auto md:max-w-md">
    <div class="mt-4 flex items-center justify-between">
      <span class="border-input w-[35%] border-b dark:border-gray-600"></span>
      <span class="text-muted-foreground text-center text-xs uppercase">
        {{ $t('authentication.thirdPartyLogin') }}
      </span>
      <span class="border-input w-[35%] border-b dark:border-gray-600"></span>
    </div>

    <div class="mt-4 flex flex-wrap justify-center">
      <ZayumIconButton class="mb-3">
        <MdiWechat />
      </ZayumIconButton>
      <ZayumIconButton class="mb-3">
        <MdiQqchat />
      </ZayumIconButton>
      <ZayumIconButton class="mb-3">
        <MdiGithub />
      </ZayumIconButton>
      <ZayumIconButton class="mb-3">
        <MdiGoogle />
      </ZayumIconButton>
    </div>
  </div>
</template>
