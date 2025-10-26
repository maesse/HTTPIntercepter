<script setup lang="ts">
import { ref, computed, watch, shallowRef } from 'vue'
import { useApiStore } from '@/stores/apiStore'
import type * as monaco from 'monaco-editor'
import { formatISO9075 } from 'date-fns'
const apiStore = useApiStore()
apiStore.updateRequestList()
apiStore.connectWS()

// Headers panel state and helpers
const headersOpen = ref(true)
const headerCount = computed(() => Object.keys(apiStore.selectedRequest?.headers || {}).length)

const MONACO_EDITOR_OPTIONS = {
  automaticLayout: true,
}
// watch(
//   () => apiStore.darkMode,
//   (newVal) => {
//     console.log('Theme changed:', newVal)
//     if (monacoIns.value) {
//       console.log(monacoIns.value)
//       ;(monacoIns.value as any).editor.setTheme(newVal ? 'vs-dark' : 'vs')
//     }
//     // if (editor.value) {
//     //   editor.value.updateOptions({ theme: newVal ? 'vs-dark' : 'vs' })
//     // }
//   },
// )

// Authorization reveal toggle
const showAuth = ref(false)
watch(
  () => apiStore.selectedRequest?.id,
  () => {
    showAuth.value = false
  },
)

// Copy helpers and tooltips
const bodyCopyTip = ref('Copy to clipboard')
async function copyBody() {
  const txt = apiStore.selectedRequest?.body_text ?? apiStore.selectedRequest?.body_bytes_b64 ?? ''
  if (txt) await navigator.clipboard?.writeText(txt)
  bodyCopyTip.value = 'Copied!'
}

function openIpInfo(ip: string) {
  if (!ip) return
  window.open(`https://ipinfo.io/${ip}`, '_blank')
}

function maskAuthorization(value: string) {
  const [scheme] = value.split(/\s+/)
  return scheme ? `${scheme} ••••` : '••••'
}

function splitAndTrim(value: string, sep: RegExp | string) {
  return value
    .split(sep)
    .map((s) => s.trim())
    .filter(Boolean)
}

function decodeBasicAuth(value: string): { isBasic: boolean; user?: string; pass?: string } {
  const m = value.match(/^Basic\s+(.*)$/i)
  if (!m) return { isBasic: false }
  try {
    const b64 = m[1] as string
    const decoded = atob(b64)
    const idx = decoded.indexOf(':')
    if (idx >= 0) {
      return { isBasic: true, user: decoded.slice(0, idx), pass: decoded.slice(idx + 1) }
    }
    return { isBasic: true, user: decoded, pass: '' }
  } catch {
    return { isBasic: false }
  }
}

const editor = shallowRef<monaco.editor.IStandaloneCodeEditor>()
const monacoIns = shallowRef<unknown>()
function handleMount(monacoEditor: monaco.editor.IStandaloneCodeEditor, monacoInstance: unknown) {
  editor.value = monacoEditor
  monacoIns.value = monacoInstance
}

// Derive Monaco language from Content-Type header
function detectLanguageFromContentType(ct?: string | null): string {
  if (!ct) return 'plaintext'
  const base = ct.split(';')[0]?.trim().toLowerCase() || ''
  // Broad matches first
  if (base.includes('json')) return 'json'
  if (base.includes('xml')) return 'xml'
  if (base.includes('html')) return 'html'
  if (base.includes('markdown')) return 'markdown'
  if (base.includes('yaml') || base.endsWith('/yml')) return 'yaml'
  if (base.includes('javascript') || base.endsWith('/js')) return 'javascript'
  if (base.includes('typescript') || base.endsWith('/ts')) return 'typescript'
  if (base.includes('css')) return 'css'
  if (base.includes('sql')) return 'sql'
  if (base.includes('form-urlencoded')) return 'plaintext'
  if (base.startsWith('text/')) return 'plaintext'
  return 'plaintext'
}

const monacoLanguage = computed(() => {
  const ct = apiStore.selectedRequest?.headers?.['content-type']
  return detectLanguageFromContentType(ct)
})
</script>

<template>
  <!-- Body: Sidebar + Main Content -->
  <div class="flex flex-1 overflow-hidden m-2 two-pane">
    <!-- Sidebar -->
    <div class="pane-card">
      <v-card elevation="2" class="w-80 ma-1 pa-1 pane-scroll flex-1">
        <v-fade-transition mode="out-in">
          <v-list density="compact" lines="two">
            <v-list-subheader class="flex w-100 align-center border-b-lg flexfix">
              <span>
                Requests
                <v-btn
                  class="ma-1"
                  icon="mdi-refresh"
                  :size="24"
                  variant="outlined"
                  color="primary"
                  :loading="apiStore.isLoadingList"
                  :disabled="apiStore.isLoadingList"
                  @click="apiStore.updateRequestList()"
                ></v-btn>
              </span>
              <!-- Live indicator -->
              <div class="d-inline-flex align-center ml-2" aria-label="WebSocket live status">
                <span :class="['live-lamp', apiStore.isWsConnected ? 'on' : 'off']" />
                <v-chip
                  size="x-small"
                  :color="apiStore.isWsConnected ? 'red-darken-2' : 'grey'"
                  variant="flat"
                  class="ml-1 live-chip"
                  label
                  >LIVE</v-chip
                >
              </div>
            </v-list-subheader>
            <v-list-item
              v-for="request in apiStore.requestList"
              :value="request"
              :key="request.id"
              @click="apiStore.selectRequest(request.id)"
              color="primary"
              border="sm"
              class="rounded ma-1 elevation-1"
            >
              <template #prepend>
                <span
                  class="font-mono text-xs text-grey-darken-2"
                  style="min-width: 24px; display: inline-block"
                  >#{{ request.id }}</span
                >
              </template>
              <template #title>
                <div class="flex items-center gap-2">
                  <span class="font-semibold w-16">{{ request.method }}</span>
                  <span class="truncate flex-1">{{ request.path }}</span>
                  <v-chip v-if="request.is_new" size="x-small" color="primary" label>new</v-chip>
                </div>
              </template>
              <template #subtitle>
                <div class="flex items-center gap-2 text-xs text-gray-500">
                  <span class="text-grey-darken-1">{{
                    formatISO9075(new Date(request.ts * 1000))
                  }}</span>
                  <span style="text-overflow: ellipsis"
                    >• {{ apiStore.listWithRelative.find((r) => r.id === request.id)?.since }}</span
                  >
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
                <v-icon
                  v-if="apiStore.selectedRequest?.id === request.id"
                  icon="mdi-chevron-right"
                  style="min-width: 24px"
                />
              </template>
            </v-list-item>
          </v-list>
        </v-fade-transition>
      </v-card>
    </div>
    <!-- Main Content -->
    <div class="flex-1 p-4 pane-scroll" style="height: 100%">
      <v-fade-transition v-if="apiStore.selectedRequest" mode="out-in">
        <v-card
          density="compact"
          elevation="2"
          class="ma-1 pa-1"
          :key="apiStore.selectedRequest?.id"
        >
          <div class="ma-2">
            <h2 class="text-2xl font-bold ma-2">
              Request Details
              <span v-if="apiStore.selectedLoadingId" class="text-sm text-gray-500 mb-2"
                >Loading...</span
              >
            </h2>
            <div class="flex items-center gap-2">
              <div class="text-primary">
                <p>
                  <strong>{{ apiStore.selectedRequest.method }}</strong>
                  {{ apiStore.selectedRequest.path
                  }}<span
                    v-if="
                      apiStore.selectedRequest.query &&
                      Object.keys(apiStore.selectedRequest.query).length
                    "
                    class="inline-flex items-center flex-wrap gap-1 ml-1"
                  >
                    <span class="text-grey">?</span>
                    <template
                      v-for="(entry, idx) in Object.entries(apiStore.selectedRequest.query)"
                      :key="entry[0]"
                    >
                      <v-chip
                        size="x-small"
                        color="indigo"
                        label
                        variant="tonal"
                        class="font-mono"
                        >{{ entry[0] }}</v-chip
                      >
                      <span>=</span>
                      <v-chip
                        size="x-small"
                        color="green"
                        label
                        variant="tonal"
                        class="font-mono"
                        >{{ entry[1] }}</v-chip
                      >
                      <span v-if="idx < Object.entries(apiStore.selectedRequest.query).length - 1"
                        >&</span
                      >
                    </template>
                  </span>
                </p>
              </div>
              <div class="ml-auto flex gap-2">
                <v-btn
                  size="small"
                  variant="tonal"
                  @click="apiStore.downloadRaw(apiStore.selectedRequest.id)"
                  ><v-icon icon="mdi-download" /> Full Request</v-btn
                >
                <v-btn
                  size="small"
                  variant="tonal"
                  @click="apiStore.copyCurl(apiStore.selectedRequest)"
                  ><v-icon icon="mdi-content-copy" /> curl</v-btn
                >
                <v-btn
                  size="small"
                  variant="tonal"
                  color="error"
                  :disabled="!apiStore.selectedRequest"
                  @click="
                    apiStore.selectedRequest && apiStore.deleteRequest(apiStore.selectedRequest.id)
                  "
                >
                  <v-icon icon="mdi-delete" start />Delete
                </v-btn>
              </div>
            </div>

            <p class="text-sm">
              Timestamp: {{ formatISO9075(new Date(apiStore.selectedRequest.ts * 1000)) }} •
              <strong>IP:</strong> {{ apiStore.selectedRequest.ip }}
              <v-tooltip text="Open http://ipinfo.io in new tab" open-delay="150">
                <template #activator="{ props }">
                  <v-btn
                    v-bind="props"
                    size="x-small"
                    icon
                    variant="text"
                    class="ml-1"
                    @click="openIpInfo(apiStore.selectedRequest.ip)"
                  >
                    <v-icon icon="mdi-information-outline" />
                  </v-btn>
                </template>
              </v-tooltip>
            </p>

            <v-expansion-panels variant="accordion" bg-color="surface-light" class="mt-2">
              <v-expansion-panel
                :value="headersOpen"
                @group:selected="(v: any) => (headersOpen = !!v?.length)"
              >
                <v-expansion-panel-title>
                  <strong>Headers</strong>
                  <span class="ml-2 text-caption text-grey">({{ headerCount }})</span>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-sheet :elevation="2" border rounded class="pa-2 mb-2">
                    <table class="headers-table w-100">
                      <tbody>
                        <template
                          v-for="(value, key) in apiStore.selectedRequest.headers"
                          :key="key"
                        >
                          <tr>
                            <td class="key-col">
                              <span class="font-mono text-xs"
                                ><strong>{{ key }}:</strong></span
                              >
                            </td>
                            <td class="val-col">
                              <!-- Special header renderings -->
                              <template v-if="key.toLowerCase() === 'content-type'">
                                <v-chip
                                  v-for="(part, idx) in splitAndTrim(value, ';')"
                                  :key="idx"
                                  size="x-small"
                                  color="primary"
                                  class="ma-1"
                                  label
                                  variant="tonal"
                                  >{{ part }}</v-chip
                                >
                              </template>
                              <template
                                v-else-if="
                                  ['accept', 'accept-encoding', 'accept-language'].includes(
                                    key.toLowerCase(),
                                  )
                                "
                              >
                                <v-chip
                                  v-for="(part, idx) in splitAndTrim(value, ',')"
                                  :key="idx"
                                  size="x-small"
                                  color="secondary"
                                  class="ma-1"
                                  label
                                  variant="tonal"
                                  >{{ part }}</v-chip
                                >
                              </template>
                              <template v-else-if="key.toLowerCase() === 'authorization'">
                                <div class="inline-flex align-center">
                                  <v-btn
                                    size="x-small"
                                    icon
                                    variant="text"
                                    class="ma-0 mr-1"
                                    :title="showAuth ? 'Hide credentials' : 'Show credentials'"
                                    @click="showAuth = !showAuth"
                                  >
                                    <v-icon :icon="showAuth ? 'mdi-eye-off' : 'mdi-eye'" />
                                  </v-btn>
                                  <template v-if="decodeBasicAuth(value).isBasic">
                                    <v-chip
                                      size="x-small"
                                      color="red"
                                      class="ma-1"
                                      label
                                      variant="tonal"
                                      >Basic</v-chip
                                    >
                                    <v-chip
                                      size="x-small"
                                      color="purple"
                                      class="ma-1"
                                      label
                                      variant="tonal"
                                    >
                                      {{ showAuth ? decodeBasicAuth(value).user : '••••' }} </v-chip
                                    >:
                                    <v-chip
                                      size="x-small"
                                      color="purple"
                                      class="ma-1"
                                      label
                                      variant="tonal"
                                    >
                                      {{ showAuth ? decodeBasicAuth(value).pass : '••••' }}
                                    </v-chip>
                                  </template>
                                  <template v-else>
                                    <v-chip
                                      size="x-small"
                                      color="red"
                                      class="ma-1"
                                      label
                                      variant="tonal"
                                    >
                                      {{ showAuth ? value : maskAuthorization(value) }}
                                    </v-chip>
                                  </template>
                                </div>
                              </template>
                              <template v-else-if="key.toLowerCase() === 'cookie'">
                                <v-chip
                                  size="x-small"
                                  color="teal"
                                  class="ma-1"
                                  label
                                  variant="tonal"
                                >
                                  {{ splitAndTrim(value, ';').length }} cookies
                                </v-chip>
                                <span class="font-mono text-xs break-words">{{ value }}</span>
                              </template>
                              <template v-else>
                                <span class="font-mono text-xs break-words">{{ value }}</span>
                              </template>
                            </td>
                          </tr>
                        </template>
                      </tbody>
                    </table>
                  </v-sheet>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <template
              v-if="
                (apiStore.selectedRequest.body_length ?? 0) > 0 ||
                apiStore.selectedRequest.body_text ||
                apiStore.selectedRequest.body_bytes_b64
              "
            >
              <p>
                <strong>Body:</strong>
                <v-tooltip :text="bodyCopyTip" open-delay="150">
                  <template #activator="{ props }">
                    <v-btn
                      v-bind="props"
                      size="x-small"
                      icon
                      variant="text"
                      class="ml-1"
                      @mouseenter="bodyCopyTip = 'Copy to clipboard'"
                      @click="copyBody"
                    >
                      <v-icon icon="mdi-content-copy" />
                    </v-btn>
                  </template>
                </v-tooltip>

                <!-- Special header renderings -->
                <template v-if="apiStore.selectedRequest.headers['content-type']">
                  <v-chip
                    v-for="(part, idx) in splitAndTrim(
                      apiStore.selectedRequest.headers['content-type'],
                      ';',
                    )"
                    :key="idx"
                    size="x-small"
                    color="primary"
                    class="ma-1"
                    label
                    variant="tonal"
                    >{{ part }}</v-chip
                  >
                </template>
              </p>

              <v-sheet
                :elevation="2"
                border
                rounded
                class="font-mono pa-2 text-xs rounded mb-2"
                tag="pre"
              >
                <vue-monaco-editor
                  v-model:value="apiStore.selectedRequest.body_text"
                  :theme="apiStore.darkMode ? 'vs-dark' : 'vs'"
                  :language="monacoLanguage"
                  :options="MONACO_EDITOR_OPTIONS"
                  style="min-height: 300px"
                  @mount="handleMount"
              /></v-sheet>
            </template>
          </div>
        </v-card>
      </v-fade-transition>
      <template v-else>
        <p key="no-selection">Please select a request from the sidebar to view details.</p>
      </template>
    </div>
  </div>
</template>
<style>
.flexfix > div {
  flex: 1 0 100%;
  display: flex;
  justify-content: space-between;
}
</style>
<style scoped>
.live-lamp {
  width: 10px;
  height: 10px;
  border-radius: 9999px;
  display: inline-block;
  background-color: #9e9e9e; /* grey */
}
.live-lamp.on {
  background-color: #ff1744; /* red A400 */
  box-shadow:
    0 0 4px #ff1744,
    0 0 8px rgba(255, 23, 68, 0.6);
  animation: livePulse 1.2s ease-in-out infinite;
}
.live-chip {
  color: #fff !important;
  padding-inline: 6px;
}
@keyframes livePulse {
  0% {
    box-shadow:
      0 0 4px #ff1744,
      0 0 8px rgba(255, 23, 68, 0.6);
  }
  50% {
    box-shadow:
      0 0 8px #ff1744,
      0 0 16px rgba(255, 23, 68, 0.8);
  }
  100% {
    box-shadow:
      0 0 4px #ff1744,
      0 0 8px rgba(255, 23, 68, 0.6);
  }
}

/* Two-pane layout sizing and scrolling */
.two-pane {
  height: calc(100vh - var(--v-layout-top));
}
.pane-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.pane-scroll {
  overflow-y: auto;
}

/* Headers table styling */
.headers-table {
  border-collapse: collapse;
  width: 100%;
  table-layout: auto;
}
.headers-table td {
  vertical-align: top;
}
.headers-table tr:nth-child(even) td {
  /* light/dark friendly slight stripe */
  background: color-mix(in srgb, var(--v-theme-surface-variant), transparent 88%);
}
.headers-table .key-col {
  white-space: nowrap; /* don't shrink key column */
  width: 1%;
}
.headers-table .val-col {
  word-break: break-word;
}
</style>
