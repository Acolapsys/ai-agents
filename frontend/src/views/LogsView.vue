<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Логи агентов</h1>

    <div class="bg-white rounded-lg shadow-sm p-4">
      <!-- Панель управления -->
      <div class="flex flex-wrap items-end gap-4 mb-4">
        <!-- Выбор агента -->
        <div class="w-64">
          <AppSelect
            v-model="selectedAgent"
            :options="agentOptions"
            placeholder="Выберите агента"
            label="Агент"
            @update:modelValue="onAgentChange"
          />
        </div>

        <!-- Количество строк -->
        <div class="w-32">
          <AppInput
            v-model.number="limit"
            type="number"
            min="10"
            max="1000"
            label="Строк"
          />
        </div>

        <!-- Кнопка загрузки -->
        <AppButton @click="loadLogs" :disabled="loading || !selectedAgent">
          {{ loading ? 'Загрузка...' : 'Загрузить' }}
        </AppButton>

        <!-- Автообновление -->
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="autoRefresh" />
          Автообновление (5с)
        </label>
      </div>

      <!-- Поиск -->
      <div class="mb-4">
        <AppInput
          v-model="search"
          placeholder="Поиск по логам..."
          class="w-full"
        />
      </div>

      <!-- Область логов -->
      <div
        v-if="filteredLogs.length"
        class="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm overflow-auto max-h-96"
      >
        <div
          v-for="(line, idx) in filteredLogs"
          :key="idx"
          class="whitespace-pre-wrap border-b border-gray-700 py-1"
        >
          {{ line }}
        </div>
        <div class="mt-2 text-gray-500 text-xs">
          Всего строк в файле: {{ totalLines }} (показано {{ filteredLogs.length }})
        </div>
      </div>

      <!-- Пустое состояние -->
      <div v-else-if="selectedAgent && !loading" class="text-gray-500 italic py-4">
        Лог пуст или не содержит записей.
      </div>

      <!-- Ошибка -->
      <div v-if="error" class="bg-red-50 text-red-800 p-3 rounded-lg mt-4">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import processManager from '@/services/api/ProcessManagerService.js'

// Состояние
const agents = ref([])
const selectedAgent = ref('')
const limit = ref(100)
const logs = ref([])
const totalLines = ref(0)
const loading = ref(false)
const error = ref('')
const search = ref('')
const autoRefresh = ref(false)
let refreshTimer = null

// Преобразуем список агентов в формат для AppSelect
const agentOptions = computed(() => {
  return agents.value.map(a => ({
    value: a.id,
    label: a.name
  }))
})

// Фильтрация логов по поисковому запросу
const filteredLogs = computed(() => {
  if (!search.value) return logs.value
  const query = search.value.toLowerCase()
  return logs.value.filter(line => line.toLowerCase().includes(query))
})

// Загрузка списка агентов
async function fetchAgents() {
  try {
    const agentsObj = await processManager.getAgents()
    agents.value = Object.values(agentsObj)
  } catch (e) {
    error.value = 'Не удалось загрузить список агентов'
  }
}

// Загрузка логов
async function loadLogs() {
  if (!selectedAgent.value) {
    error.value = 'Выберите агента'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const data = await processManager.getLogs(selectedAgent.value, limit.value)
    logs.value = data.lines || []
    totalLines.value = data.total || 0
  } catch (e) {
    error.value = e.message || 'Ошибка загрузки логов'
    logs.value = []
  } finally {
    loading.value = false
  }
}

// Обработчик смены агента
function onAgentChange() {
  logs.value = []
  error.value = ''
  if (autoRefresh.value) {
    autoRefresh.value = false
  }
}

// Автообновление
watch(autoRefresh, (newVal) => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (newVal && selectedAgent.value) {
    refreshTimer = setInterval(() => {
      loadLogs()
    }, 5000)
  }
})

// При размонтировании чистим таймер
onMounted(() => {
  fetchAgents()
})
</script>