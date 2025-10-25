<script setup lang="ts">
import { useApiStore } from '@/stores/apiStore';
const apiStore = useApiStore();
apiStore.updateRequestList();
apiStore.connectWS();
</script>

<template>
  <!-- Body: Sidebar + Main Content -->
  <div class="flex flex-1 overflow-hidden m-2 h-100">

    <!-- Sidebar -->
    <v-card elevation="2" class="w-80 ma-1 pa-1">
      <v-fade-transition mode="out-in">
        <v-list density="compact" lines="two">
          <v-list-subheader class="flex w-100"><span>Requests</span>
          <v-btn class="ml-15" size="small" color="primary" :loading="apiStore.isLoadingList" :disabled="apiStore.isLoadingList" @click="apiStore.updateRequestList()">
            Refresh
          </v-btn></v-list-subheader>
          <v-list-item v-for="request in apiStore.requestList" :value="request" :key="request.id" @click="apiStore.selectRequest(request.id)" color="primary" border="sm" class="rounded ma-1 elevation-1">
            <template #title>
              <div class="flex items-center gap-2">
                <span class="font-semibold w-16">{{ request.method }}</span>
                <span class="truncate flex-1">{{ request.path }}</span>
                <v-chip v-if="request.is_new" size="x-small" color="primary" label>new</v-chip>
              </div>
            </template>
            <template #subtitle>
              <div class="flex items-center gap-2 text-xs text-gray-500">
                <span>{{ apiStore.listWithRelative.find(r => r.id === request.id)?.since }}</span>
                <v-progress-circular
                  v-if="apiStore.selectedLoadingId === request.id"
                  indeterminate
                  size="12"
                  width="2"
                  class="ml-2"
                />
              </div>
            </template>
            <template #append>
              <v-icon v-if="apiStore.selectedRequest?.id === request.id" icon="mdi-chevron-right" />
            </template>
          </v-list-item>


        </v-list>
      </v-fade-transition>
    </v-card>

    <!-- Main Content -->
    <div class="flex-1 p-4 overflow-y-auto">


      <v-fade-transition v-if="apiStore.selectedRequest" mode="out-in" >
        <v-card density="compact" elevation="2" class="ma-1 pa-1" :key="apiStore.selectedRequest?.id">
          <h2 class="text-2xl font-bold ma-2">Request Details <span v-if="apiStore.selectedLoadingId" class="text-sm text-gray-500 mb-2">Loading...</span></h2>
          <div class="flex items-center gap-2">
            <div>
              <p><strong>{{ apiStore.selectedRequest.method }}</strong> {{ apiStore.selectedRequest.path }}</p>
            </div>
            <div class="ml-auto flex gap-2">
              <v-btn size="small" variant="tonal" @click="apiStore.downloadRaw(apiStore.selectedRequest.id)">Download Raw</v-btn>
              <v-btn size="small" variant="tonal" @click="apiStore.copyCurl(apiStore.selectedRequest)">Copy curl</v-btn>
            </div>
          </div>

          <p class="text-gray-600 text-sm">{{ new Date(apiStore.selectedRequest.ts * 1000).toLocaleString() }} - <strong>IP:</strong> {{ apiStore.selectedRequest.ip }}</p>

          <p class="mt-2"><strong>Headers:</strong></p>
          <v-sheet :elevation="2" border rounded class="pa-2 mb-2">
            <table>
            <template v-for="(value, key) in apiStore.selectedRequest.headers" :key="key">
              <tr>
                <td><span class="font-mono text-xs break-all"><strong>{{ key }}:</strong></span></td>
                <td><span class="ml-1 font-mono text-xs break-words">{{ value }}</span></td>
              </tr>
            </template>
            </table>
          </v-sheet>
          <p><strong>Body:</strong></p>
          <v-sheet :elevation="2" border rounded class="font-mono pa-2 text-xs rounded mb-2" tag="pre">{{ apiStore.selectedRequest.body_text }}</v-sheet>
          <template v-if="apiStore.selectedRequest.body_bytes_b64">
            <p><strong>Body (Base64):</strong></p>
            <v-sheet :elevation="2" border rounded class="font-mono pa-2 text-xs rounded mb-2" tag="pre">{{ apiStore.selectedRequest.body_bytes_b64 }}</v-sheet>
          </template>
        </v-card>


      </v-fade-transition>
      <template v-else>
          <p key="no-selection">Please select a request from the sidebar to view details.</p>
        </template>
    </div>

  </div>
</template>
