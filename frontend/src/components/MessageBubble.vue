<template>
  <div class="message" :class="role">
    <div class="message-avatar">
      {{ role === 'user' ? '👤' : '🤖' }}
    </div>
    <div class="message-content" v-html="renderedContent"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  role: {
    type: String,
    required: true,
    validator: (v) => ['user', 'assistant'].includes(v),
  },
  content: {
    type: String,
    required: true,
  },
})

const renderedContent = computed(() => {
  if (props.role === 'user') {
    return `<p>${escapeHtml(props.content)}</p>`
  }
  const rawHtml = marked.parse(props.content)
  return DOMPurify.sanitize(rawHtml)
})

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
</script>
