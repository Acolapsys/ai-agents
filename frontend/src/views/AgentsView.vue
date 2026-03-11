<template>
  <div>
    <!-- Шапка с кнопками и чекбоксом -->
    <div class="flex flex-wrap items-center justify-between mb-6 gap-4">
      <h1 class="text-2xl font-bold text-charcoal-blue">Управление агентами</h1>
      <div class="flex items-center gap-4">
        <!-- Кнопка ручного обновления -->
        <AppButton
          :disabled="refreshLoading"
          @click="handleRefresh"
          variant="outline"
          size="sm"
        >
          <span v-if="!refreshLoading" class="inline-flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Обновить
          </span>
          <span v-else class="inline-flex items-center gap-1">
            <span class="inline-block w-4 h-4 border-2 border-t-transparent border-gray-600 rounded-full animate-spin"></span>
            Обновление...
          </span>
        </AppButton>

        <!-- Чекбокс автообновления -->
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="autoRefresh" @change="toggleAutoRefresh" />
          <span>Автообновление (30 сек)</span>
        </label>

        <!-- Массовые действия -->
        <div class="flex space-x-2">
          <AppButton @click="startAll" :disabled="loadingAll">
            {{ loadingAll ? 'Запуск...' : 'Запустить всех' }}
          </AppButton>
          <AppButton variant="secondary" @click="stopAll" :disabled="loadingAll">
            {{ loadingAll ? 'Остановка...' : 'Остановить всех' }}
          </AppButton>
        </div>
      </div>
    </div>

    <!-- Список агентов (без изменений) -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-baltic-blue"></div>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <AppCard v-for="agent in agentsList" :key="agent.id">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-baltic-blue">{{ agent.name }}</h3>
            <AppBadge :variant="agent.status === 'running' ? 'success' : 'default'">
              {{ agent.status === 'running' ? 'Активен' : 'Неактивен' }}
            </AppBadge>
          </div>
        </template>
        <p class="text-gray-600 text-sm mb-2">{{ agent.description }}</p>
        <p v-if="agent.port" class="text-xs text-gray-400">Порт: {{ agent.port }}</p>
        <p v-if="agent.pid" class="text-xs text-gray-400">PID: {{ agent.pid }}</p>
        <p v-if="agent.pid" class="text-xs text-gray-400">
          Время работы: {{ formatUptime(agent.uptime) }}
        </p>
        <template #footer>
          <div class="flex space-x-2">
            <AppButton
              :variant="agent.status === 'running' ? 'secondary' : 'primary'"
              size="sm"
              :disabled="loadingStates[agent.id]"
              @click="toggleAgent(agent)"
            >
              {{ loadingStates[agent.id] ? '...' : (agent.status === 'running' ? 'Выключить' : 'Включить') }}
            </AppButton>
            <AppButton
              variant="outline"
              size="sm"
              :disabled="loadingStates[agent.id]"
              @click="restartAgent(agent)"
            >
              Перезагрузить
            </AppButton>
          </div>
        </template>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import processManager from '@/services/api/ProcessManagerService'

const agentsList = ref([])
const loading = ref(true)
const loadingStates = ref({})
const loadingAll = ref(false)
const autoRefresh = ref(false)
const refreshLoading = ref(false)
let refreshTimer = null

const fetchAgents = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    const agentsObj = await processManager.getAgents()
    agentsList.value = Object.values(agentsObj)
  } catch (e) {
    console.error('Failed to fetch agents', e)
  } finally {
    if (!silent) loading.value = false
  }
}

const handleRefresh = async () => {
  refreshLoading.value = true
  await fetchAgents(true)
  refreshLoading.value = false
}

const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => fetchAgents(true), 30000)
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }
}

const toggleAgent = async (agent) => {
  loadingStates.value[agent.id] = true
  try {
    if (agent.status === 'running') {
      await processManager.stopAgent(agent.id)
    } else {
      await processManager.startAgent(agent.id)
    }
    await fetchAgents()
  } catch (e) {
    console.error('Toggle failed', e)
  } finally {
    loadingStates.value[agent.id] = false
  }
}

const restartAgent = async (agent) => {
  loadingStates.value[agent.id] = true
  try {
    await processManager.restartAgent(agent.id)
    await fetchAgents()
  } catch (e) {
    console.error('Restart failed', e)
  } finally {
    loadingStates.value[agent.id] = false
  }
}

const startAll = async () => {
  loadingAll.value = true
  try {
    await processManager.startAll()
    await fetchAgents()
  } catch (e) {
    console.error('Start all failed', e)
  } finally {
    loadingAll.value = false
  }
}

const stopAll = async () => {
  loadingAll.value = true
  try {
    await processManager.stopAll()
    await fetchAgents()
  } catch (e) {
    console.error('Stop all failed', e)
  } finally {
    loadingAll.value = false
  }
}

const formatUptime = (seconds) => {
  if (typeof seconds !== 'number') return '—'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return [h, m, s].map(v => String(v).padStart(2, '0')).join(':')
}

onMounted(async () => {
  await fetchAgents()
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>