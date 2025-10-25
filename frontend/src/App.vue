<script setup lang="ts">

import { useTheme } from 'vuetify'

const theme = useTheme()
// Initialize from system preference
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
  theme.global.name.value = 'dark'
}
// Listen to system changes
const media = window.matchMedia?.('(prefers-color-scheme: dark)')
media?.addEventListener('change', (e) => {
  theme.global.name.value = e.matches ? 'dark' : 'light'
})
function toggleTheme() {
  theme.global.name.value = theme.global.name.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <v-app>
    <v-app-bar density="comfortable">
      <v-app-bar-title class="font-semibold">HTTP Interceptor
        <div class="text-sm mr-4">
        Send a request to: <a href="/inbound" class="text-primary">/inbound</a>
      </div>
      </v-app-bar-title>

      <v-btn icon="mdi-theme-light-dark" variant="text" @click="toggleTheme" :title="`Toggle theme (now: ${theme.global.name.value})`"></v-btn>
    </v-app-bar>
    <v-main>
      <RouterView />
    </v-main>
  </v-app>

</template>

<style scoped></style>
