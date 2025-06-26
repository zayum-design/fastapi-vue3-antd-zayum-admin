<script setup lang="ts">
import type { ToolbarType } from "./types";

interface Props {
  appName?: string;
  logo?: string;
  pageTitle?: string;
  pageDescription?: string;
  sloganImage?: string;
  toolbar?: boolean;
  copyright?: boolean;
  toolbarList?: ToolbarType[];
}

withDefaults(defineProps<Props>(), {
  appName: "",
  copyright: true,
  logo: "",
  pageDescription: "",
  pageTitle: "",
  sloganImage: "",
  toolbar: true,
  toolbarList: () => ["color", "language", "layout", "theme"],
});

</script>

<template>
  <div
    :class="[isDark]"
    class="flex min-h-full flex-1 select-none overflow-x-hidden"
  >
    <!-- 头部 Logo 和应用名称 -->
    <div v-if="logo || appName" class="absolute left-0 top-0 z-10 flex flex-1">
      <div
        class="text-foreground lg:text-foreground ml-4 mt-4 flex flex-1 items-center sm:left-6 sm:top-6"
      >
        <img v-if="logo" :alt="appName" src="@/assets/logo-2.svg" class="mr-2" width="42" />
        <p v-if="appName" class="text-xl font-medium">
          {{ appName }}
        </p>
      </div>
    </div>

    <!-- 中心认证面板 -->
    <div class="flex-center relative w-full">
      <div class="login-background absolute left-0 top-0 size-full"></div>
      <div
        class="flex-col-center dark:bg-background-deep bg-background relative px-6 py-10 lg:flex-initial lg:px-8"
      >
        <RouterView v-slot="{ Component, route }">
          <Transition appear mode="out-in" name="slide-right">
            <KeepAlive :include="['Login']">
              <component
                :is="Component"
                :key="route.fullPath"
                class="enter-x bg-white rounded-md mt-6 w-full sm:mx-auto md:max-w-5xl"
                style="background-color: white !important"
              />
            </KeepAlive>
          </Transition>
        </RouterView>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-background {
  background: linear-gradient(
    154deg,
    #07070915 30%,
    hsl(var(--primary) / 30%) 48%,
    #07070915 64%
  );
  filter: blur(100px);
}

.dark {
  .login-background {
    background: linear-gradient(
      154deg,
      #07070915 30%,
      hsl(var(--primary) / 20%) 48%,
      #07070915 64%
    );
    filter: blur(100px);
  }
}
</style>
