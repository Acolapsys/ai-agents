<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Статистика</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- График использования токенов -->
      <AppCard>
        <template #header>
          <span class="font-semibold text-charcoal-blue">Расход токенов (за 7 дней)</span>
        </template>
        <div class="h-48 flex items-end justify-around">
          <div v-for="(day, idx) in tokenData" :key="idx" class="flex flex-col items-center">
            <div class="w-8 bg-baltic-blue rounded-t" :style="{ height: day.value * 2 + 'px' }"></div>
            <span class="text-xs text-gray-500 mt-1">{{ day.label }}</span>
          </div>
        </div>
      </AppCard>

      <!-- Круговая диаграмма активности агентов (просто заглушка) -->
      <AppCard>
        <template #header>
          <span class="font-semibold text-charcoal-blue">Активность агентов</span>
        </template>
        <div class="flex justify-center items-center h-48">
          <div class="relative w-32 h-32 rounded-full bg-conic-gradient" style="background: conic-gradient(#33658a 0deg 120deg, #86bbd8 120deg 240deg, #f6ae2d 240deg 360deg);"></div>
        </div>
        <div class="flex justify-center space-x-4 mt-2">
          <span class="flex items-center text-sm"><span class="w-3 h-3 bg-baltic-blue rounded-full mr-1"></span> Семейный советник</span>
          <span class="flex items-center text-sm"><span class="w-3 h-3 bg-sky-reflection rounded-full mr-1"></span> Библиотекарь</span>
          <span class="flex items-center text-sm"><span class="w-3 h-3 bg-honey-bronze rounded-full mr-1"></span> Telegram</span>
        </div>
      </AppCard>
    </div>

    <!-- Дополнительная статистика: таблица -->
    <AppCard class="mt-6">
      <template #header>
        <span class="font-semibold text-charcoal-blue">Детальная статистика по агентам</span>
      </template>
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-sky-reflection/20">
            <th class="text-left py-2">Агент</th>
            <th class="text-left py-2">Запросов</th>
            <th class="text-left py-2">Токенов</th>
            <th class="text-left py-2">Ошибок</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="agent in agentStats" :key="agent.name" class="border-b border-sky-reflection/10">
            <td class="py-2">{{ agent.name }}</td>
            <td>{{ agent.requests }}</td>
            <td>{{ agent.tokens }}</td>
            <td><span class="text-blaze-orange">{{ agent.errors }}</span></td>
          </tr>
        </tbody>
      </table>
    </AppCard>
  </div>
</template>

<script setup>
import AppCard from '@/components/ui/AppCard.vue'

const tokenData = [
  { label: 'Пн', value: 20 },
  { label: 'Вт', value: 35 },
  { label: 'Ср', value: 25 },
  { label: 'Чт', value: 40 },
  { label: 'Пт', value: 30 },
  { label: 'Сб', value: 15 },
  { label: 'Вс', value: 10 },
]

const agentStats = [
  { name: 'Семейный советник', requests: 1240, tokens: '12.4k', errors: 2 },
  { name: 'Библиотекарь', requests: 856, tokens: '8.2k', errors: 0 },
  { name: 'Telegram-помощник', requests: 2341, tokens: '23.1k', errors: 5 },
]
</script>

<style scoped>
/* Для поддержки конического градиента */
.bg-conic-gradient {
  border-radius: 50%;
}
</style>