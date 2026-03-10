<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Таск-трекер</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div v-for="status in statuses" :key="status" class="space-y-3">
        <h2 class="font-semibold text-baltic-blue">{{ status }}</h2>
        <TaskCard v-for="task in tasksByStatus[status]" :key="task.id" :task="task" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import TaskCard from '@/components/TaskCard.vue'

const tasks = ref([
  { id: 1, title: 'Настроить агента для Telegram', description: 'Интеграция с Bot API', status: 'Новые' },
  { id: 2, title: 'Оптимизация логирования', description: 'Добавить фильтры по уровню', status: 'В работе' },
  { id: 3, title: 'Дизайн карточки задачи', description: 'Сделать перетаскивание', status: 'Завершённые' },
])

const statuses = ['Новые', 'В работе', 'Завершённые']

const tasksByStatus = computed(() => {
  return statuses.reduce((acc, status) => {
    acc[status] = tasks.value.filter(t => t.status === status)
    return acc
  }, {})
})
</script>