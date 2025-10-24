import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// from pydantic import BaseModel:

// class RequestSummary(BaseModel):
//     id: int
//     method: str
//     path: str
//     ts: float
//     ip: str
//     content_length: int

export type ApiRequestSummary = {
  id: string
  method: string
  path: string
  ts: number
  ip: string
  content_length: number
}

// class StoredRequest(BaseModel):
//     id: int
//     method: str
//     path: str
//     ts: float
//     ip: str
//     headers: Dict[str, str]
//     query: Dict[str, str]
//     body_text: Optional[str] = None
//     body_bytes_b64: Optional[str] = None
//     body_length: int = 0


export type ApiRequest = {
  id: string
  method: string
  path: string
  ts: number
  ip: string
  headers: Record<string, string>
  query: Record<string, string>
  body_text?: string
  body_bytes_b64?: string
  body_length: number
}



export const useApiStore = defineStore('api', () => {
  const requestList = ref<ApiRequestSummary[]>([])
  const selectedRequest = ref<ApiRequest | null>(null)

  async function updateRequestList() {
    // Call API to fetch updated request list
    const response = await fetch('/api/requests')
    if (response.ok) {
      const data = await response.json()
      requestList.value = data as ApiRequestSummary[]
    }
  }

  async function selectRequest(requestId: string) {
    const response = await fetch(`/api/requests/${requestId}`)
    if (response.ok) {
      const data = await response.json()
      selectedRequest.value = data as ApiRequest
    }
  }

  return { requestList, selectedRequest, updateRequestList, selectRequest }
})
