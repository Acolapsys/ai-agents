<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Логи</h1>
    <div class="flex flex-wrap gap-4 mb-4">
      <AppSelect v-model="levelFilter" placeholder="Все уровни" class="w-40">
        <option value="">Все уровни</option>
        <option value="info">Info</option>
        <option value="warn">Warn</option>
        <option value="error">Error</option>
      </AppSelect>
      <AppInput v-model="search" placeholder="Поиск..." class="flex-1" />
    </div>
    <div class="bg-gray-900 text-gray-200 p-4 rounded-lg font-mono text-sm space-y-1 overflow-auto max-h-96">
      <div v-for="log in filteredLogs" :key="log.id" class="border-b border-gray-700 pb-1 flex items-center">
        <span class="text-sky-reflection">{{ log.timestamp }}</span>
        <AppBadge :variant="log.level === 'info' ? 'info' : log.level === 'warn' ? 'warning' : 'danger'" class="ml-2">
          {{ log.level }}
        </AppBadge>
        <span class="ml-2">{{ log.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppBadge from '@/components/ui/AppBadge.vue'

const logs = ref([
  { id: 1, timestamp: '2025-03-10 10:23:45', level: 'info', message: 'Агент "Семейный советник" запущен' },
  { id: 2, timestamp: '2025-03-10 10:25:12', level: 'warn', message: 'Высокая загрузка CPU' },
  { id: 3, timestamp: '2025-03-10 10:27:03', level: 'error', message: 'Ошибка подключения к Telegram' },
])

const levelFilter = ref('')
const search = ref('')

const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    return (levelFilter.value ? log.level === levelFilter.value : true) &&
           (search.value ? log.message.toLowerCase().includes(search.value.toLowerCase()) : true)
  })
})
</script>