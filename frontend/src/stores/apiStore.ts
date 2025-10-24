import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useApiStore = defineStore('api', () => {
  const requestList = ref([])
  const selectedRequest = ref(null)

  function updateRequestList() {
    // Call API to fetch updated request list
  }

  function selectRequest(requestId: string) {
    selectedRequest.value = requestList.value.find(req => req.id === requestId) || null
  }

  return { requestList, selectedRequest, updateRequestList, selectRequest }
})
