<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Управление агентами</h1>
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
        <p v-if="agent.uptime" class="text-xs text-gray-400">
          Время работы: {{ formatUptime(agent.uptime) }}
        </p>
        <template #footer>
          <div class="flex space-x-2">
            <AppButton :variant="agent.status === 'running' ? 'secondary' : 'primary'" size="sm"
              :disabled="loadingStates[agent.id]" @click="toggleAgent(agent)">
              {{ loadingStates[agent.id] ? '...' : (agent.status === 'running' ? 'Выключить' : 'Включить') }}
            </AppButton>
            <AppButton variant="outline" size="sm" :disabled="loadingStates[agent.id]" @click="restartAgent(agent)">
              Перезагрузить
            </AppButton>
          </div>
        </template>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import processManager from '@/services/api/ProcessManagerService'

const agentsList = ref([])
const loading = ref(true)
const loadingStates = ref({})

const fetchAgents = async()  =>{
  loading.value = true
  try {
    const agentsObj = await processManager.getAgents()
    agentsList.value = Object.values(agentsObj)
  } catch (e) {
    console.error('Failed to fetch agents', e)
  } finally {
    loading.value = false
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

const formatUptime = (seconds) => {
  if (!seconds) return '—'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return [h, m, s].map(v => String(v).padStart(2, '0')).join(':')
}

onMounted(fetchAgents)
</script>