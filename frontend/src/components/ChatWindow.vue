<template>
  <div class="chat-panel">
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="sidebar-empty">
        <div>
          <p style="font-size: 18px; margin-bottom: 8px;">🦜🔗 LangChain 文档助手</p>
          <p style="color: var(--text-secondary); font-size: 14px;">
            用中文提问，我会基于 LangChain 官方文档为您解答
          </p>
        </div>
      </div>

      <MessageBubble v-for="(msg, index) in messages" :key="index" :role="msg.role" :content="msg.content" />

      <div v-if="isLoading" class="message assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="loading-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <div class="chat-input-wrapper">
        <button class="clear-btn" @click="clearMessages" :title="清空对话">🗑️</button>
        <textarea v-model="inputText" @keydown.enter.exact.prevent="sendMessage"
          :placeholder="isLoading ? '正在回答中...' : '输入您的问题... (Enter 发送)'" :disabled="isLoading" rows="1"
          ref="inputRef"></textarea>
        <button class="send-btn" @click="sendMessage" :disabled="!inputText.trim() || isLoading">
          ↑
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import MessageBubble from './MessageBubble.vue'
import { sendQuestion } from '../api/client'

const props = defineProps({
  model: { type: String, default: '' },
  temperature: { type: Number, default: 0.7 },
})

const emit = defineEmits(['loading'])

const STORAGE_KEY = 'chat_messages'

const storedMessages = localStorage.getItem(STORAGE_KEY)
const messages = ref(storedMessages ? JSON.parse(storedMessages) : [])
const inputText = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)

function saveMessages() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value))
}

function clearMessages() {
  messages.value = []
  localStorage.removeItem(STORAGE_KEY)
}

async function sendMessage() {
  const question = inputText.value.trim()
  if (!question || isLoading.value) return

  messages.value.push({ role: 'user', content: question })
  saveMessages()
  inputText.value = ''
  isLoading.value = true
  emit('loading', true)

  await nextTick()
  scrollToBottom()

  try {
    const res = await sendQuestion(question, props.model, props.temperature)
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let assistantContent = ''

    messages.value.push({ role: 'assistant', content: '' })
    const assistantMsg = messages.value[messages.value.length - 1]

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const data = line.slice(6)
        if (data === '[DONE]') continue

        try {
          const parsed = JSON.parse(data)
          if (parsed.type === 'content') {
            assistantContent += parsed.data
            assistantMsg.content = assistantContent
            saveMessages()
            await nextTick()
            scrollToBottom()
          }
        } catch (e) {
          // skip invalid JSON
        }
      }
    }
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: `⚠️ 请求失败: ${e.message}`,
    })
    saveMessages()
  } finally {
    isLoading.value = false
    emit('loading', false)
    await nextTick()
    scrollToBottom()
    inputRef.value?.focus()
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>
