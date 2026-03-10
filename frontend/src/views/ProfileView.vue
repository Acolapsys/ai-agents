<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Личные данные</h1>
    <AppCard class="max-w-2xl">
      <form @submit.prevent="saveProfile">
        <div class="space-y-4">
          <AppInput v-model="form.name" label="Имя" required />
          <AppInput v-model="form.email" label="Email" type="email" required />
          <AppInput v-model="form.phone" label="Телефон" />
          <div>
            <label class="block text-sm font-medium text-charcoal-blue mb-1">Привычки</label>
            <div class="space-y-2">
              <div v-for="(habit, idx) in form.habits" :key="idx" class="flex items-center space-x-2">
                <AppInput v-model="form.habits[idx]" placeholder="Привычка" />
                <AppButton variant="danger" size="sm" @click="removeHabit(idx)">Удалить</AppButton>
              </div>
              <AppButton variant="secondary" size="sm" @click="addHabit">+ Добавить привычку</AppButton>
            </div>
          </div>
          <AppButton type="submit" block>Сохранить изменения</AppButton>
        </div>
      </form>
    </AppCard>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const form = reactive({
  name: 'Алексей Иванов',
  email: 'alex@example.com',
  phone: '+7 999 123-45-67',
  habits: ['Утренняя зарядка', 'Чтение 30 минут']
})

function addHabit() {
  form.habits.push('')
}
function removeHabit(index) {
  form.habits.splice(index, 1)
}
function saveProfile() {
  alert('Профиль сохранён (демо)')
}
</script>