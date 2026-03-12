<template>
  <AppCard class="border-l-4" :style="{ borderLeftColor: colorByStatus }">
    <h3 class="font-medium text-charcoal-blue">{{ task.title }}</h3>
    <p class="text-sm text-gray-600 mt-1">{{ task.description }}</p>
    <div class="flex justify-between items-center mt-2">
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-400">ID: {{ task.id }}</span>
        <select
          v-model="task.status"
          @change="updateStatus"
          class="text-xs border rounded px-1 py-0.5"
        >
          <option v-for="s in statusOptions" :key="s.value" :value="s.value">
            {{ s.label }}
          </option>
        </select>
      </div>
      <div class="flex gap-1">
        <button @click="editTask" class="text-xs text-blue-600 hover:underline">✎</button>
        <button @click="deleteTask" class="text-xs text-red-600 hover:underline">🗑</button>
      </div>
    </div>
  </AppCard>
</template>

<script setup>
import { computed } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import taskManager from '@/services/api/TaskManagerService'

const props = defineProps({
  task: Object
})

const emit = defineEmits(['update', 'delete'])

const statusOptions = [
  { value: 'new', label: 'Новые' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'done', label: 'Завершённые' },
]

const colorByStatus = computed(() => {
  switch (props.task.status) {
    case 'new': return '#86bbd8'
    case 'in_progress': return '#f6ae2d'
    case 'done': return '#33658a'
    default: return '#b0bec5'
  }
})

const updateStatus = async () => {
  try {
    await taskManager.updateTask(props.task.id, { status: props.task.status })
    emit('update')
  } catch (e) {
    console.error('Failed to update status', e)
  }
}

const deleteTask = async () => {
  if (confirm('Удалить задачу?')) {
    try {
      await taskManager.deleteTask(props.task.id)
      emit('delete')
    } catch (e) {
      console.error('Failed to delete', e)
    }
  }
}

const editTask = () => {
  // TODO: открыть модалку редактирования
}
</script>