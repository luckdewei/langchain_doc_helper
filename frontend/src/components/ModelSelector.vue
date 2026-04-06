<template>
  <div class="header-controls">
    <label>
      模型
      <select v-model="selectedModel" @change="$emit('update:model', selectedModel)">
        <option v-for="m in models" :key="m" :value="m">{{ formatModelName(m) }}</option>
      </select>
    </label>
    <label>
      温度
      <input
        type="range"
        :value="temperature"
        min="0"
        max="1"
        step="0.1"
        @input="$emit('update:temperature', parseFloat($event.target.value))"
      />
      <span>{{ temperature.toFixed(1) }}</span>
    </label>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getModels } from '../api/client'

const props = defineProps({
  model: { type: String, default: '' },
  temperature: { type: Number, default: 0.7 },
})

const emit = defineEmits(['update:model', 'update:temperature'])

const models = ref([])
const selectedModel = ref(props.model)

onMounted(async () => {
  try {
    const data = await getModels()
    models.value = data.models
    if (!selectedModel.value && data.default) {
      selectedModel.value = data.default
      emit('update:model', data.default)
    }
  } catch (e) {
    console.error('Failed to load models:', e)
  }
})

function formatModelName(name) {
  return name.replace('Qwen/', 'Qwen ')
}
</script>
