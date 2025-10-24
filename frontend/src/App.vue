<script setup lang="ts">
import { useApiStore } from './stores/apiStore';


const apiStore = useApiStore();
apiStore.updateRequestList();
</script>

<template>
  <!-- Header -->
  <header class="bg-blue-600 text-white p-4 shadow">
    <h1 class="text-xl font-semibold">My Page Header</h1>
  </header>

  <!-- Body: Sidebar + Main Content -->
  <div class="flex flex-1 overflow-hidden">

    <!-- Sidebar -->
    <aside class="w-64 bg-white shadow-md p-4 overflow-y-auto">
      <h2 class="text-lg font-semibold mb-4">Menu</h2>
      <button class="w-full mb-4 px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600" @click="apiStore.updateRequestList()">
        Refresh Requests
      </button>
      <ul class="space-y-2">
        <template v-for="request in apiStore.requestList" :key="request.id">
          <li :class="apiStore.selectedRequest?.id === request.id ? 'bg-blue-200' : ''">
            <button class="w-full text-left px-3 py-2 rounded hover:bg-blue-100" @click="apiStore.selectRequest(request.id)">
              {{ request.method }} {{ request.path }}
            </button>
          </li>
        </template>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-6 overflow-y-auto">
      <h2 class="text-2xl font-bold mb-4">Main Content</h2>
      <template v-if="apiStore.selectedRequest">
        <div>
          <h3 class="text-xl font-semibold mb-2">Request Details</h3>
          <p><strong>Method:</strong> {{ apiStore.selectedRequest.method }}</p>
          <p><strong>Path:</strong> {{ apiStore.selectedRequest.path }}</p>

          <p><strong>Headers:</strong></p>
          <pre class="bg-gray-100 p-2 rounded mb-2">{{ JSON.stringify(apiStore.selectedRequest.headers, null, 2) }}</pre>
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

<style scoped></style>
