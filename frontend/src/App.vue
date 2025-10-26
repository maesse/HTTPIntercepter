<script setup lang="ts">

import { computed } from 'vue'
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
// Full inbound URL (proxied in dev, same origin in prod)
const inboundUrl = computed(() => `${location.origin}/inbound`)
function copyInboundUrl() {
  navigator.clipboard?.writeText(inboundUrl.value)
}
function selectAllInbound(e: Event) {
  const t = e.target as HTMLInputElement | null
  if (t && typeof t.select === 'function') {
    t.select()
  } else {
    // Fallback: find input inside the field
    const input = (e.currentTarget as HTMLElement | null)?.querySelector?.('input') as HTMLInputElement | null
    input?.select()
  }
}
</script>

<template>
  <v-app>
    <v-app-bar density="comfortable" extensionHeight="64px">
      <v-app-bar-title class="font-semibold">
        <div class="flex items-center">
          <div>
            HTTP Intercepter
            <div class="text-sm mr-4">
              Send a request to: <a href="/inbound" class="text-primary">/inbound</a>
            </div>
          </div>
          <!-- Where to send requests -->
           <div class="w-33">
      <v-text-field
              :model-value="inboundUrl"
              readonly
              density="compact"
              variant="outlined"
              hide-details
              class="font-mono text-sm ma-auto"
              append-inner-icon="mdi-content-copy"
        @click:append-inner="copyInboundUrl"
        @click:control="selectAllInbound"
        @focus="selectAllInbound"
            /></div>

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
