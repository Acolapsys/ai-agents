<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Статистика активности</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Задачи по дням -->
      <AppCard>
        <template #header>
          <span class="font-semibold text-charcoal-blue">Задачи по дням</span>
        </template>
        <canvas ref="tasksChart" class="h-64 w-full"></canvas>
      </AppCard>

      <!-- Активность по часам -->
      <AppCard>
        <template #header>
          <span class="font-semibold text-charcoal-blue">Активность по часам</span>
        </template>
        <canvas ref="hourlyChart" class="h-64 w-full"></canvas>
      </AppCard>

      <!-- Сообщения по агентам -->
      <AppCard>
        <template #header>
          <span class="font-semibold text-charcoal-blue">Сообщения по агентам</span>
        </template>
        <canvas ref="agentsChart" class="h-64 w-full"></canvas>
      </AppCard>

      <!-- Активность по дням недели -->
      <AppCard>
        <template #header>
          <span class="font-semibold text-charcoal-blue">Активность по дням недели</span>
        </template>
        <canvas ref="weekdayChart" class="h-64 w-full"></canvas>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useChart } from '@/composables/useChart' // предположим, что есть хелпер для графиков
import trackerService from '@/services/api/TrackerService'

const tasksChart = ref(null)
const hourlyChart = ref(null)
const agentsChart = ref(null)
const weekdayChart = ref(null)

onMounted(async () => {
  const [tasks, hourly, agents, weekday] = await Promise.all([
    trackerService.getTasksDaily(),
    trackerService.getHourlyActivity(),
    trackerService.getChatByAgent(),
    trackerService.getWeekdayActivity(),
  ])

  // Задачи по дням
  useChart(tasksChart.value, {
    x: tasks.map(d => d.date),
    y: tasks.map(d => d.count),
    type: 'line',
    title: 'Задачи по дням',
  })

  // Активность по часам
  useChart(hourlyChart.value, {
    x: hourly.map(d => `${d.hour}:00`),
    y: hourly.map(d => d.count),
    type: 'bar',
    title: 'Сообщения по часам',
  })

  // Сообщения по агентам
  useChart(agentsChart.value, {
    labels: agents.map(d => d.agent),
    values: agents.map(d => d.count),
    type: 'pie',
  })

  // Активность по дням недели
  useChart(weekdayChart.value, {
    x: weekday.map(d => d.weekday),
    y: weekday.map(d => d.count),
    type: 'bar',
    title: 'Сообщения по дням недели',
  })
})
</script>