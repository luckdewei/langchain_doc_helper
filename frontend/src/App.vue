<template>
  <div id="app">
    <header class="app-header">
      <h1>🦜🔗 LangChain 文档助手</h1>
      <ModelSelector
        :model="selectedModel"
        :temperature="temperature"
        @update:model="selectedModel = $event"
        @update:temperature="temperature = $event"
      />
      <div class="header-controls">
        <button class="btn btn-secondary" @click="showIngestModal = true">
          📥 索引文档
        </button>
      </div>
    </header>

    <div class="app-body">
      <ChatWindow
        :model="selectedModel"
        :temperature="temperature"
      />
    </div>

    <div v-if="showIngestModal" class="ingest-modal-overlay" @click.self="showIngestModal = false">
      <div class="ingest-modal">
        <h3>📥 索引 LangChain 文档</h3>
        <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 12px;">
          将爬取 LangChain 官方文档并索引到 Pinecone。可留空使用默认文档列表。
        </p>
        <textarea
          v-model="ingestUrls"
          placeholder="每行一个 URL，留空使用默认列表..."
        ></textarea>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showIngestModal = false">取消</button>
          <button class="btn" @click="startIngest" :disabled="isIngesting">
            {{ isIngesting ? '索引中...' : '开始索引' }}
          </button>
        </div>
        <div v-if="ingestStatus" class="ingest-status" :class="ingestStatus.type">
          {{ ingestStatus.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ChatWindow from './components/ChatWindow.vue'
import ModelSelector from './components/ModelSelector.vue'
import { ingestDocuments } from './api/client'

const selectedModel = ref('')
const temperature = ref(0.7)
const showIngestModal = ref(false)
const ingestUrls = ref('')
const isIngesting = ref(false)
const ingestStatus = ref(null)

async function startIngest() {
  isIngesting.value = true
  ingestStatus.value = { type: 'loading', message: '正在爬取和索引文档，这可能需要几分钟...' }

  try {
    const urls = ingestUrls.value.trim()
      ? ingestUrls.value.trim().split('\n').map(u => u.trim()).filter(Boolean)
      : null

    await ingestDocuments(urls)
    ingestStatus.value = { type: 'success', message: '✅ 文档索引完成！' }
    setTimeout(() => {
      showIngestModal.value = false
      ingestStatus.value = null
      ingestUrls.value = ''
    }, 2000)
  } catch (e) {
    ingestStatus.value = { type: 'error', message: `❌ 索引失败: ${e.message}` }
  } finally {
    isIngesting.value = false
  }
}
</script>
