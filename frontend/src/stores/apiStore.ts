import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { formatDistanceToNow } from 'date-fns'

// from pydantic import BaseModel:

// class RequestSummary(BaseModel):
//     id: int
//     method: str
//     path: str
//     ts: float
//     ip: str
//     content_length: int

export type ApiRequestSummary = {
  id: number
  method: string
  path: string
  ts: number
  ip: string
  content_length: number
  is_new?: boolean
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
  id: number
  method: string
  path: string
  ts: number
  ip: string
  headers: Record<string, string>
  query: Record<string, string>
  body_text?: string
  body_bytes_b64?: string
  body_length: number
  raw_request_b64?: string
}



export const useApiStore = defineStore('api', () => {
  const requestList = ref<ApiRequestSummary[]>([])
  const selectedRequest = ref<ApiRequest | null>(null)
  const ws = ref<WebSocket | null>(null)
  const isLoadingList = ref(false)
  const selectedLoadingId = ref<number | null>(null)
  const isWsConnected = ref(false)

  async function updateRequestList() {
    console.log('[api] updateRequestList: start')
    isLoadingList.value = true
    try {
      const response = await fetch('/api/requests')
      if (response.ok) {
        const data = await response.json()
        requestList.value = data as ApiRequestSummary[]
        console.log('[api] updateRequestList: done, count=', requestList.value.length)
      } else {
        console.warn('[api] updateRequestList: http error', response.status)
      }
    } catch (e) {
      console.error('[api] updateRequestList: failed', e)
    } finally {
      isLoadingList.value = false
    }
  }

  async function selectRequest(requestId: number) {
    console.log('[api] selectRequest: start id=', requestId)
    selectedRequest.value = null
    const found = requestList.value.find(r => r.id === requestId)
    if (found) {
      found.is_new = false
    } else {
      console.warn('[api] selectRequest: id not in list, abort')
      return
    }
    selectedLoadingId.value = requestId
    try {
      const response = await fetch(`/api/requests/${requestId}`)
      if (response.ok) {
        const data = await response.json()
        selectedRequest.value = data as ApiRequest
        console.log('[api] selectRequest: done id=', requestId)
      } else {
        console.warn('[api] selectRequest: http error', response.status)
      }
    } catch (e) {
      console.error('[api] selectRequest: failed', e)
    } finally {
      selectedLoadingId.value = null
    }
  }

  function downloadRaw(requestId: number) {
    console.log('[api] downloadRaw: id=', requestId)
    window.open(`/api/requests/${requestId}/raw`, '_blank')
  }

  async function deleteRequest(requestId: number) {
    console.log('[api] deleteRequest: id=', requestId)
    try {
      const response = await fetch(`/api/requests/${requestId}`, { method: 'DELETE' })
      if (response.ok) {
        requestList.value = requestList.value.filter(r => r.id !== requestId)
        if (selectedRequest.value?.id === requestId) {
          selectedRequest.value = null
        }
        console.log('[api] deleteRequest: deleted id=', requestId)
      } else {
        console.warn('[api] deleteRequest: http error', response.status)
      }
    } catch (e) {
      console.error('[api] deleteRequest: failed', e)
    }
  }

  function connectWS() {
    if (ws.value) return
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${proto}://${location.host}/ws`
    console.log('[ws] connecting', url)
    ws.value = new WebSocket(url)
    ws.value.onopen = () => {
      console.log('[ws] open')
      isWsConnected.value = true
    }
    ws.value.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data)
        if (msg?.type === 'new_request' && msg.data?.id) {
          console.log('[ws] new_request', msg.data)
          requestList.value = [msg.data as ApiRequestSummary, ...requestList.value]
          requestList.value[0]!.is_new = true
        }
      } catch (e) {
        console.warn('[ws] message parse error', e)
      }
    }
    ws.value.onclose = () => {
      console.log('[ws] closed')
      ws.value = null
      isWsConnected.value = false
      // basic backoff reconnect
      setTimeout(connectWS, 1000)
    }
    ws.value.onerror = (e) => {
      console.error('[ws] error', e)
      isWsConnected.value = false
    }
  }

  const listWithRelative = computed(() =>
    requestList.value.map(r => ({
      ...r,
      since: formatDistanceToNow(new Date(r.ts * 1000), { addSuffix: true })
    }))
  )

  function copyCurl(req: ApiRequest) {
    const url = `${location.origin}${req.path}${Object.keys(req.query || {}).length ? '?' + new URLSearchParams(req.query as Record<string, string>).toString() : ''}`
    const method = req.method || 'GET'
    const headerParts = Object.entries(req.headers || {})
      .filter(([k]) => k.toLowerCase() !== 'host')
      .map(([k, v]) => `-H "${k}: ${v.replace(/"/g, '\\"')}"`)
      .join(' ')
    const bodyPart = req.body_text ? ` --data-binary @-` : ''
    const base = `curl -X ${method} ${headerParts} "${url}"${bodyPart}`.trim()
    const finalCmd = req.body_text ? `${base} < NUL` : base
    console.log('[api] copyCurl for id=', req.id, '\n', finalCmd)
    navigator.clipboard?.writeText(finalCmd)
  }

  return { requestList, selectedRequest, updateRequestList, selectRequest, downloadRaw, deleteRequest, connectWS, listWithRelative, copyCurl, isLoadingList, selectedLoadingId, isWsConnected }
})
