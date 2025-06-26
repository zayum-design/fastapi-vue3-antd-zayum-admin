<template>
  <div class="install-layout">
    <router-view />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'InstallLayout'
})
</script>

<style scoped>
.install-layout {
  height: 100%;
}
</style>
