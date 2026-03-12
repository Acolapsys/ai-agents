<template>
  <AppCard class="border-l-4" :style="{ borderLeftColor: getColorByStatus(task.status) }">
    <h3 class="font-medium text-charcoal-blue">{{ task.title }}</h3>
    <p v-if="task.description" class="text-sm text-gray-600 mt-1">{{ task.description }}</p>
    <div class="flex justify-between items-center mt-2">
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-400">ID: {{ task.id }}</span>
        <span v-if="task.project" class="text-xs bg-gray-100 px-2 py-0.5 rounded-full text-gray-600">
          {{ task.project }}
        </span>
      </div>
      <AppBadge :variant="getBadgeVariants(task.status)">{{ getTaskStatusLabel(task.status) }}</AppBadge>
    </div>
  </AppCard>
</template>

<script setup>
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'

const props = defineProps({
  task: Object
})

const emit = defineEmits(['update', 'delete'])

const statusOptions = {
  new: 'Новые',
  'in_progress': 'В работе',
  done: 'Завершённые'
}

const getTaskStatusLabel = (status) => {
  return statusOptions[status] || ''
}


const colorOptions = {
  new: '#86bbd8',
  'in_progress': '#f6ae2d',
  done: '#33658a'
}

const getColorByStatus = (status) => {
  return colorOptions[status] || '#b0bec5'
}

const badgeVariants = {
  new: 'info',
  'in_progress': 'warning',
  done: 'success'
}

const getBadgeVariants = (status) => {
  return badgeVariants[status] || 'default'
}


</script>