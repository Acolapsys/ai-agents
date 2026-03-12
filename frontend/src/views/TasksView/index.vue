<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-charcoal-blue">Таск-трекер</h1>
      <AppButton @click="openCreateModal">+ Новая задача</AppButton>
    </div>

    <div class="mb-6 p-4 bg-white rounded-lg shadow-sm border border-sky-reflection/20">
      <h3 class="font-medium mb-2">Создать задачу</h3>
      <div class="flex gap-2">
        <AppInput v-model="newTaskTitle" placeholder="Название" class="flex-1" />
        <AppInput v-model="newTaskDescription" placeholder="Описание" class="flex-1" />
        <AppButton @click="createTask">Создать</AppButton>
      </div>
    </div>

    <!-- Фильтры: проект -->
    <div class="mb-4 flex gap-4 items-center">
      <div class="w-64">
        <AppSelect
          v-model="selectedProject"
          :options="projectOptions"
          placeholder="Все проекты"
          label="Проект"
          @update:modelValue="fetchTasks"
        />
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-baltic-blue"></div>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div v-for="status in statusList" :key="status.value" class="space-y-3">
        <h2 class="font-semibold text-baltic-blue">{{ status.label }}</h2>
        <TaskCard
          v-for="task in tasksByStatus[status.value]"
          :key="task.id"
          :task="task"
          @update="handleUpdate"
          @delete="handleDelete"
        />
      </div>
    </div>

    <!-- Модальное окно создания задачи (можно добавить позже) -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TaskCard from './TaskCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import taskManager from '@/services/api/TaskManagerService'

// Маппинг статусов
const statusList = [
  { value: 'new', label: 'Новые' },
  { value: 'in_progress', label: 'В работе' },
  { value: 'done', label: 'Завершённые' },
]

// Список проектов (пока статический, потом можно получать из API)
const projectOptions = [
  { value: '', label: 'Все проекты' },
  { value: 'Nexus', label: 'Nexus' },
  { value: 'WordStorm', label: 'WordStorm' },
  { value: 'AI Agents', label: 'AI Agents' },
]

const tasks = ref([])
const loading = ref(true)
const selectedProject = ref(null)

const tasksByStatus = computed(() => {
  const grouped = {}
  statusList.forEach(s => grouped[s.value] = [])
  tasks.value.forEach(task => {
    if (grouped[task.status]) {
      grouped[task.status].push(task)
    }
  })
  return grouped
})

async function fetchTasks() {
  loading.value = true
  try {
    const params = {}
    if (selectedProject.value) {
      params.project = selectedProject.value
    }
    const data = await taskManager.getTasks(params)
    tasks.value = data
  } catch (e) {
    console.error('Failed to load tasks', e)
  } finally {
    loading.value = false
  }
}

const handleUpdate = async (updatedTask) => {
  // обновление задачи
  await fetchTasks()
}

const handleDelete = async (taskId) => {
  // удаление задачи
  await fetchTasks()
}

const openCreateModal = () => {
  // TODO: открыть модалку
}

const newTaskTitle = ref('')
const newTaskDescription = ref('')

const createTask = async () => {
  if (!newTaskTitle.value) return
  try {
    await taskManager.createTask({
      title: newTaskTitle.value,
      description: newTaskDescription.value,
      status: 'new',
      priority: 'medium'
    })
    newTaskTitle.value = ''
    newTaskDescription.value = ''
    await fetchTasks()
  } catch (e) {
    console.error('Failed to create task', e)
  }
}

onMounted(fetchTasks)
</script>