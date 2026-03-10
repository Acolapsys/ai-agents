<template>
  <AppCard class="border-l-4" :style="{ borderLeftColor: colorByStatus }">
    <h3 class="font-medium text-charcoal-blue">{{ task.title }}</h3>
    <p class="text-sm text-gray-600 mt-1">{{ task.description }}</p>
    <div class="flex justify-between items-center mt-2">
      <span class="text-xs text-gray-400">ID: {{ task.id }}</span>
      <AppBadge :variant="badgeVariant">{{ task.status }}</AppBadge>
    </div>
  </AppCard>
</template>

<script setup>
import { computed } from 'vue'
import AppCard from './ui/AppCard.vue'
import AppBadge from './ui/AppBadge.vue'

const props = defineProps({
  task: Object
})

const colorByStatus = computed(() => {
  switch (props.task.status) {
    case 'Новые': return '#86bbd8'
    case 'В работе': return '#f6ae2d'
    case 'Завершённые': return '#33658a'
    default: return '#b0bec5'
  }
})

const badgeVariant = computed(() => {
  switch (props.task.status) {
    case 'Новые': return 'info'
    case 'В работе': return 'warning'
    case 'Завершённые': return 'success'
    default: return 'default'
  }
})
</script>