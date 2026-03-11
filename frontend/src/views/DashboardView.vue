<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Панель управления</h1>

    <!-- Карточки статистики + статусы сервисов -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <AppCard v-for="stat in stats" :key="stat.label" class="text-center">
        <div class="text-3xl font-bold text-baltic-blue">{{ stat.value }}</div>
        <div class="text-sm text-gray-500">{{ stat.label }}</div>
      </AppCard>

      <!-- Статус Gateway -->
      <AppCard class="text-center">
        <div class="text-sm text-gray-500 mb-1">Gateway</div>
        <div class="flex items-center justify-center space-x-2">
          <span class="inline-block w-3 h-3 rounded-full" :class="gatewayStatus.ok ? 'bg-green-500' : 'bg-red-500'"></span>
          <span class="font-medium">{{ gatewayStatus.ok ? 'Доступен' : 'Недоступен' }}</span>
        </div>
        <div v-if="gatewayStatus.error" class="text-xs text-red-600 mt-1">{{ gatewayStatus.error }}</div>
      </AppCard>

      <!-- Статус Process Manager -->
      <AppCard class="text-center">
        <div class="text-sm text-gray-500 mb-1">Process Manager</div>
        <div class="flex items-center justify-center space-x-2">
          <span class="inline-block w-3 h-3 rounded-full" :class="pmStatus.ok ? 'bg-green-500' : 'bg-red-500'"></span>
          <span class="font-medium">{{ pmStatus.ok ? 'Доступен' : 'Недоступен' }}</span>
        </div>
        <div v-if="pmStatus.error" class="text-xs text-red-600 mt-1">{{ pmStatus.error }}</div>
      </AppCard>
    </div>

    <!-- Две колонки: последние логи и задачи -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Последние логи -->
      <AppCard>
        <template #header>
          <div class="flex justify-between items-center">
            <span class="font-semibold text-charcoal-blue">Последние логи</span>
            <router-link to="/logs" class="text-sm text-baltic-blue hover:underline">Все логи →</router-link>
          </div>
        </template>
        <div class="space-y-2">
          <div v-for="log in recentLogs" :key="log.id" class="flex items-center text-sm border-b border-sky-reflection/20 pb-1">
            <AppBadge :variant="log.level === 'error' ? 'danger' : log.level === 'warn' ? 'warning' : 'info'" class="mr-2">
              {{ log.level }}
            </AppBadge>
            <span class="text-gray-600 truncate flex-1">{{ log.message }}</span>
            <span class="text-gray-400 text-xs">{{ log.time }}</span>
          </div>
        </div>
      </AppCard>

      <!-- Активные задачи -->
      <AppCard>
        <template #header>
          <div class="flex justify-between items-center">
            <span class="font-semibold text-charcoal-blue">Активные задачи</span>
            <router-link to="/tasks" class="text-sm text-baltic-blue hover:underline">Все задачи →</router-link>
          </div>
        </template>
        <div class="space-y-2">
          <div v-for="task in activeTasks" :key="task.id" class="flex items-center justify-between">
            <div class="flex items-center">
              <span class="w-2 h-2 rounded-full mr-2" :class="{
                'bg-honey-bronze': task.status === 'В работе',
                'bg-sky-reflection': task.status === 'Новые',
              }"></span>
              <span class="text-sm text-charcoal-blue">{{ task.title }}</span>
            </div>
            <AppBadge :variant="task.status === 'В работе' ? 'warning' : 'info'">{{ task.status }}</AppBadge>
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Состояние агентов -->
    <AppCard class="mt-6">
      <template #header>
        <span class="font-semibold text-charcoal-blue">Состояние агентов</span>
      </template>
      <div class="space-y-3">
        <div v-for="agent in agents" :key="agent.id" class="flex items-center justify-between">
          <div class="flex items-center">
            <span class="font-medium">{{ agent.name }}</span>
            <AppBadge :variant="agent.status === 'active' ? 'success' : 'default'" class="ml-3">
              {{ agent.status === 'active' ? 'Активен' : 'Неактивен' }}
            </AppBadge>
          </div>
          <div class="flex space-x-2">
            <AppButton size="sm" :variant="agent.status === 'active' ? 'secondary' : 'primary'" @click="toggleAgent(agent)">
              {{ agent.status === 'active' ? 'Выключить' : 'Включить' }}
            </AppButton>
            <AppButton size="sm" variant="outline" @click="restartAgent(agent)">Перезагрузить</AppButton>
          </div>
        </div>
      </div>
    </AppCard>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import gatewayService from '@/services/api/GatewayService'
import processManager from '@/services/api/ProcessManagerService'

// Статистика (пока мок)
const stats = ref([
  { label: 'Активные агенты', value: 3 },
  { label: 'Задач в работе', value: 7 },
  { label: 'Новых логов', value: 124 },
  { label: 'Расходы (мес.)', value: '$42.50' },
])

// Состояние сервисов
const gatewayStatus = ref({ ok: false })
const pmStatus = ref({ ok: false })

// Последние логи (мок)
const recentLogs = ref([
  { id: 1, level: 'info', message: 'Агент "Семейный советник" запущен', time: '10:23' },
  { id: 2, level: 'warn', message: 'Высокая загрузка CPU', time: '10:25' },
  { id: 3, level: 'error', message: 'Ошибка подключения к Telegram', time: '10:27' },
  { id: 4, level: 'info', message: 'Агент "Библиотекарь" синхронизирован', time: '10:30' },
])

// Активные задачи (мок)
const activeTasks = ref([
  { id: 1, title: 'Настроить агента для Telegram', status: 'В работе' },
  { id: 2, title: 'Оптимизация логирования', status: 'В работе' },
  { id: 3, title: 'Дизайн карточки задачи', status: 'Новые' },
])

// Агенты (мок)
const agents = ref([
  { id: 'family', name: 'Семейный советник', status: 'active' },
  { id: 'library', name: 'Библиотекарь', status: 'inactive' },
  { id: 'telegram', name: 'Telegram-помощник', status: 'active' },
])

async function checkServices() {
  gatewayStatus.value = await gatewayService.checkHealth()
  pmStatus.value = await processManager.checkHealth()
}

function toggleAgent(agent) {
  agent.status = agent.status === 'active' ? 'inactive' : 'active'
}
function restartAgent(agent) {
  alert(`Перезагрузка агента ${agent.name}`)
}

onMounted(() => {
  checkServices()
  // Можно добавить периодическую проверку, например, каждые 30 секунд
  // setInterval(checkServices, 30000)
})
</script>