<script setup lang="ts">
import { useApiStore } from '@/stores/apiStore';
const apiStore = useApiStore();
apiStore.updateRequestList();
apiStore.connectWS();
</script>

<template>
  <!-- Body: Sidebar + Main Content -->
  <div class="flex flex-1 overflow-hidden">

    <!-- Sidebar -->
    <aside class="w-80 bg-white shadow-md p-4 overflow-y-auto">
      <h2 class="text-lg font-semibold mb-4">Menu</h2>
      <button
        class="w-full mb-4 px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        :disabled="apiStore.isLoadingList"
        @click="apiStore.updateRequestList()"
      >
        <span v-if="apiStore.isLoadingList" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
        <span>Refresh Requests</span>
      </button>
      <ul class="space-y-2">
        <template v-for="request in apiStore.requestList" :key="request.id">
          <li :class="[apiStore.selectedRequest?.id === request.id ? 'bg-blue-200' : '', request.is_new ? 'ring-2 ring-blue-500' : '']">
            <button
              class="w-full text-left px-3 py-2 rounded hover:bg-blue-100 disabled:opacity-60 disabled:cursor-not-allowed"
              :disabled="apiStore.selectedLoadingId === request.id"
              @click="apiStore.selectRequest(request.id)"
            >
              <div class="flex gap-2 items-center">
                <span class="font-semibold w-16">{{ request.method }}</span>
                <span class="truncate flex-1">{{ request.path }}</span>
                <span class="text-xs text-gray-500">{{ apiStore.listWithRelative.find(r => r.id === request.id)?.since }}</span>
                <span v-if="apiStore.selectedLoadingId === request.id" class="ml-2 inline-block w-3 h-3 border-2 border-gray-500 border-t-transparent rounded-full animate-spin"></span>
              </div>
            </button>
          </li>
        </template>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-6 overflow-y-auto">
  <h2 class="text-2xl font-bold mb-4">Request Details</h2>
  <div v-if="apiStore.selectedLoadingId" class="text-sm text-gray-500 mb-2">Loading selected request...</div>
      <template v-if="apiStore.selectedRequest">
        <div>
          <div class="flex items-center gap-2">
            <p><strong>Method:</strong> {{ apiStore.selectedRequest.method }}</p>
            <p><strong>Path:</strong> {{ apiStore.selectedRequest.path }}</p>
            <div class="ml-auto flex gap-2">
              <button class="px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-800" @click="apiStore.downloadRaw(apiStore.selectedRequest.id)">Download Raw</button>
              <button class="px-3 py-2 bg-gray-700 text-white rounded hover:bg-gray-800" @click="apiStore.copyCurl(apiStore.selectedRequest)">Copy curl</button>
            </div>
          </div>
          <p class="text-gray-600 text-sm">{{ new Date(apiStore.selectedRequest.ts * 1000).toLocaleString() }}</p>

          <p><strong>Headers:</strong></p>
          <div class="grid grid-cols-3 gap-x-2 gap-y-1 bg-gray-50 p-2 rounded mb-2">
            <template v-for="(value, key) in apiStore.selectedRequest.headers" :key="key">
              <div class="col-span-1 font-mono text-xs text-gray-700 break-all">{{ key }}</div>
              <div class="col-span-2 font-mono text-xs text-gray-900 break-words">{{ value }}</div>
            </template>
          </div>
          <p><strong>Body:</strong></p>
          <pre class="bg-gray-100 p-2 rounded">{{ apiStore.selectedRequest.body_text }}</pre>
          <p><strong>Body (Base64):</strong></p>
          <pre class="bg-gray-100 p-2 rounded">{{ apiStore.selectedRequest.body_bytes_b64 }}</pre>
        </div>
      </template>
      <template v-else>
        <p>Please select a request from the sidebar to view details.</p>
      </template>
    </main>

  </div>
</template>
