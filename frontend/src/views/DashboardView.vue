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
          <span class="inline-block w-3 h-3 rounded-full"
            :class="gateway.ok ? 'bg-green-500' : 'bg-red-500'"></span>
          <span class="font-medium">{{ gateway.ok ? 'Доступен' : 'Недоступен' }}</span>
        </div>
      </AppCard>

      <!-- Process Manager -->
      <AppCard class="text-center">
        <div class="text-sm text-gray-500 mb-1">Process Manager</div>
        <div class="flex items-center justify-center space-x-2">
          <span class="inline-block w-3 h-3 rounded-full"
            :class="processManager.ok ? 'bg-green-500' : 'bg-red-500'"></span>
          <span class="font-medium">{{ processManager.ok ? 'Доступен' : 'Недоступен' }}</span>
        </div>
      </AppCard>

      <!-- Task Manager -->
      <AppCard class="text-center">
        <div class="text-sm text-gray-500 mb-1">Task Manager</div>
        <div class="flex items-center justify-center space-x-2">
          <span class="inline-block w-3 h-3 rounded-full"
            :class="taskManager.ok ? 'bg-green-500' : 'bg-red-500'"></span>
          <span class="font-medium">{{ taskManager.ok ? 'Доступен' : 'Недоступен' }}</span>
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
        <div v-for="(event, idx) in importantEvents" :key="idx"
          class="flex items-start space-x-2 text-sm border-b border-sky-reflection/20 pb-2 last:border-0">
          <span class="text-xs text-gray-400 whitespace-nowrap">{{ event.time }}</span>
          <span class="flex-1 text-gray-700">{{ event.message }}</span>
          <span class="px-1.5 py-0.5 rounded text-xs font-medium" :class="{
            'bg-red-100 text-red-800': event.level === 'error',
            'bg-yellow-100 text-yellow-800': event.level === 'warn',
            'bg-blue-100 text-blue-800': event.level === 'info'
          }">
            {{ event.level }}
          </span>
        </div>
      </div>
    </AppCard>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
  import { storeToRefs } from 'pinia'
import AppCard from '@/components/ui/AppCard.vue'
import { useServiceStatusStore } from '@/stores/serviceStatusStore'

const serviceStore = useServiceStatusStore()

const { gateway, processManager, taskManager, agents, importantEvents, tasks } = storeToRefs(serviceStore)

// Данные
const loadingEvents = ref(false)


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

onMounted(() => {
  loadingEvents.value = true
  serviceStore.checkAll()
  loadingEvents.value = false

})
</script>