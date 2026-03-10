<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Управление агентами</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <AppCard v-for="agent in agents" :key="agent.id">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="font-semibold text-baltic-blue">{{ agent.name }}</h3>
            <AppBadge :variant="agent.status === 'active' ? 'success' : 'default'">
              {{ agent.status === 'active' ? 'Активен' : 'Неактивен' }}
            </AppBadge>
          </div>
        </template>
        <p class="text-gray-600 text-sm mb-4">{{ agent.description }}</p>
        <template #footer>
          <div class="flex space-x-2">
            <AppButton
              :variant="agent.status === 'active' ? 'secondary' : 'primary'"
              size="sm"
              @click="toggleAgent(agent)"
            >
              {{ agent.status === 'active' ? 'Выключить' : 'Включить' }}
            </AppButton>
            <AppButton variant="outline" size="sm" @click="restartAgent(agent)">
              Перезагрузить
            </AppButton>
          </div>
        </template>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'

const agents = ref([
  { id: 1, name: 'Семейный советник', description: 'Помогает с планированием и привычками', status: 'active' },
  { id: 2, name: 'Библиотекарь', description: 'Управляет аудиокнигами и рекомендациями', status: 'inactive' },
  { id: 3, name: 'Telegram-помощник', description: 'Отвечает в Telegram', status: 'active' },
])

function toggleAgent(agent) {
  agent.status = agent.status === 'active' ? 'inactive' : 'active'
}
function restartAgent(agent) {
  alert(`Перезагрузка агента ${agent.name}`)
}
</script>