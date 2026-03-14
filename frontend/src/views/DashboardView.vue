<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Панель управления</h1>

    <!-- Карточки статистики -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <AppCard v-for="stat in stats" :key="stat.label" class="text-center">
        <div class="text-3xl font-bold text-baltic-blue">{{ stat.value }}</div>
        <div class="text-sm text-gray-500">{{ stat.label }}</div>
      </AppCard>
    </div>

    <!-- Статусы сервисов (4 карточки в ряд) -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <!-- Gateway -->
      <AppCard class="text-center">
        <div class="text-sm text-gray-500 mb-1">Gateway</div>
        <div class="flex items-center justify-center space-x-2">
          <span class="inline-block w-3 h-3 rounded-full" :class="gatewayStatus.ok ? 'bg-green-500' : 'bg-red-500'"></span>
          <span class="font-medium">{{ gatewayStatus.ok ? 'Доступен' : 'Недоступен' }}</span>
        </div>
      </AppCard>

      <!-- Process Manager -->
      <AppCard class="text-center">
        <div class="text-sm text-gray-500 mb-1">Process Manager</div>
        <div class="flex items-center justify-center space-x-2">
          <span class="inline-block w-3 h-3 rounded-full" :class="pmStatus.ok ? 'bg-green-500' : 'bg-red-500'"></span>
          <span class="font-medium">{{ pmStatus.ok ? 'Доступен' : 'Недоступен' }}</span>
        </div>
      </AppCard>

      <!-- Task Manager -->
      <AppCard class="text-center">
        <div class="text-sm text-gray-500 mb-1">Task Manager</div>
        <div class="flex items-center justify-center space-x-2">
          <span class="inline-block w-3 h-3 rounded-full" :class="tmStatus.ok ? 'bg-green-500' : 'bg-red-500'"></span>
          <span class="font-medium">{{ tmStatus.ok ? 'Доступен' : 'Недоступен' }}</span>
        </div>
      </AppCard>

      <!-- Агенты (общий статус) -->
      <AppCard class="text-center">
        <div class="text-sm text-gray-500 mb-1">Агенты</div>
        <div class="flex items-center justify-center space-x-2">
          <span class="inline-block w-3 h-3 rounded-full" :class="agentsStatusClass"></span>
          <span class="font-medium">{{ agentsStatusText }}</span>
        </div>
      </AppCard>
    </div>

    <!-- Лента важных событий -->
    <AppCard class="mt-6">
      <template #header>
        <span class="font-semibold text-charcoal-blue">Важные события</span>
      </template>
      <div v-if="loadingEvents" class="flex justify-center py-4">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-baltic-blue"></div>
      </div>
      <div v-else-if="importantEvents.length === 0" class="text-gray-500 italic py-4">
        Нет важных событий
      </div>
      <div v-else class="space-y-2 max-h-80 overflow-y-auto pr-2">
        <div
          v-for="(event, idx) in importantEvents"
          :key="idx"
          class="flex items-start space-x-2 text-sm border-b border-sky-reflection/20 pb-2 last:border-0"
        >
          <span class="text-xs text-gray-400 whitespace-nowrap">{{ event.time }}</span>
          <span class="flex-1 text-gray-700">{{ event.message }}</span>
          <span
            class="px-1.5 py-0.5 rounded text-xs font-medium"
            :class="{
              'bg-red-100 text-red-800': event.level === 'error',
              'bg-yellow-100 text-yellow-800': event.level === 'warn',
              'bg-blue-100 text-blue-800': event.level === 'info'
            }"
          >
            {{ event.level }}
          </span>
        </div>
      </div>
    </AppCard>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import gatewayService from '@/services/api/GatewayService'
import processManager from '@/services/api/ProcessManagerService'
import taskManager from '@/services/api/TaskManagerService'
import agentsService from '@/services/api/AgentsService'
import dashboardService from '@/services/api/DashboardService'

// Данные
const agents = ref([])
const importantEvents = ref([])
const loadingEvents = ref(false)

// Статусы сервисов
const gatewayStatus = ref({ ok: false })
const pmStatus = ref({ ok: false })
const tmStatus = ref({ ok: false })

// Загрузка агентов и задач для статистики
const tasks = ref([])

// Статистика
const stats = computed(() => {
  const activeAgents = agents.value.filter(a => a.status === 'running').length
  const tasksInProgress = tasks.value.filter(t => t.status === 'in_progress').length
  const totalTasks = tasks.value.length
  return [
    { label: 'Активные агенты', value: activeAgents },
    { label: 'Задач в работе', value: tasksInProgress },
    { label: 'Всего задач', value: totalTasks },
    { label: 'Важных событий', value: importantEvents.value.length },
  ]
})

// Общий статус агентов
const agentsStatusClass = computed(() => {
  const running = agents.value.filter(a => a.status === 'running').length
  const total = agents.value.length
  if (running === total) return 'bg-green-500'
  if (running === 0) return 'bg-red-500'
  return 'bg-yellow-500'
})
const agentsStatusText = computed(() => {
  const running = agents.value.filter(a => a.status === 'running').length
  const total = agents.value.length
  if (running === total) return 'Все активны'
  if (running === 0) return 'Все остановлены'
  return `${running}/${total} активны`
})

// Загрузка всех данных
async function fetchDashboardData() {
  try {
    const data = await dashboardService.getDashboard()

    gatewayStatus.value = { ok: data.gateway?.status === 'ok' }
    pmStatus.value = { ok: data.processManager?.status === 'ok' }
    tmStatus.value = { ok: data.taskManager?.status === 'ok' }
    agents.value = data.agents || []
    tasks.value = data.tasks || []
    importantEvents.value = data.importantEvents || []
  } catch (e) {
    console.error('Ошибка загрузки данных дашборда', e)
  }
}

// Загрузка важных событий (пока из логов task-manager)
async function fetchImportantEvents() {
  loadingEvents.value = true
  try {
    const logs = await taskManager.getLastLogs(50) // берём 50 последних строк
    // Фильтруем строки, содержащие ERROR, WARNING, и парсим их
    const events = []
    for (const line of logs) {
      // Пытаемся извлечь уровень и сообщение (формат логов: "2025-03-14 10:23:45 - name - ERROR - сообщение")
      const match = line.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(\bERROR\b|\bWARNING\b|\bINFO\b).*?[-]\s*(.*)/i)
      if (match) {
        events.push({
          time: match[1].slice(11), // только время (HH:MM:SS)
          level: match[2].toLowerCase(),
          message: match[3].trim()
        })
      } else {
        // Если не удалось распарсить, просто показываем строку целиком (обрезанную)
        events.push({
          time: '',
          level: 'info',
          message: line.slice(0, 80) + (line.length > 80 ? '...' : '')
        })
      }
    }
    importantEvents.value = events.slice(0, 10) // последние 10
  } catch (e) {
    console.error('Ошибка загрузки событий', e)
  } finally {
    loadingEvents.value = false
  }
}

onMounted(fetchDashboardData)
</script>