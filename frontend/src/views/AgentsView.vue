<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Управление агентами</h1>
    <div v-if="loading" class="text-center py-8">Загрузка...</div>
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
        <p class="text-gray-600 text-sm mb-4">{{ agent.description }}</p>
        <template #footer>
          <div class="flex space-x-2">
            <AppButton
              :variant="agent.status === 'running' ? 'secondary' : 'primary'"
              size="sm"
              :disabled="agentLoading[agent.id]"
              @click="toggleAgent(agent)"
            >
              {{ agentLoading[agent.id] ? '...' : (agent.status === 'running' ? 'Выключить' : 'Включить') }}
            </AppButton>
            <AppButton
              variant="outline"
              size="sm"
              :disabled="agentLoading[agent.id]"
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
import { ref, onMounted } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import processManager from '@/services/api/ProcessManagerService'

const agentsList = ref([])
const loading = ref(true)
const agentLoading = ref({})

async function fetchAgents() {
  loading.value = true
  try {
    const agentsObj = await processManager.getAgents()
    // Преобразуем объект в массив
    agentsList.value = Object.values(agentsObj)
  } catch (e) {
    console.error('Failed to fetch agents', e)
  } finally {
    loading.value = false
  }
}

async function toggleAgent(agent) {
  agentLoading.value[agent.id] = true
  try {
    if (agent.status === 'running') {
      await processManager.stopAgent(agent.id)
    } else {
      await processManager.startAgent(agent.id)
    }
    // обновляем статус
    await fetchAgents()
  } catch (e) {
    console.error('Toggle failed', e)
  } finally {
    agentLoading.value[agent.id] = false
  }
}

async function restartAgent(agent) {
  agentLoading.value[agent.id] = true
  try {
    await processManager.restartAgent(agent.id)
    await fetchAgents()
  } catch (e) {
    console.error('Restart failed', e)
  } finally {
    agentLoading.value[agent.id] = false
  }
}

onMounted(fetchAgents)
</script>