import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8181',
      '/inbound': 'http://localhost:8181',
      '/ws': {
        target: 'ws://localhost:8181', // Adjust the target to your backend server
        ws: true,
        rewriteWsOrigin: true,
      },
    },
  },
  plugins: [vue(), vuetify({ autoImport: true }), vueDevTools(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
