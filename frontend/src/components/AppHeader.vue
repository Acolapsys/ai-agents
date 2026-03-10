<template>
  <header class="bg-white border-b border-sky-reflection/20 px-6 py-3 flex items-center justify-between">
    <!-- Левая часть: можно добавить краткое название или иконку меню для мобильных -->
    <div class="flex items-center space-x-4">
      <h2 class="text-lg font-semibold text-charcoal-blue hidden md:block">AI Agents</h2>
      <!-- Поиск (опционально) -->
      <div class="relative hidden lg:block">
        <AppInput
          v-model="search"
          placeholder="Поиск..."
          class="w-64"
          size="sm"
        />
      </div>
    </div>

    <!-- Правая часть: уведомления и профиль -->
    <div class="flex items-center space-x-4">
      <!-- Уведомления -->
      <button class="relative p-2 text-baltic-blue hover:text-charcoal-blue rounded-full hover:bg-sky-reflection/20 transition">
        <span class="sr-only">Уведомления</span>
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <span class="absolute top-1 right-1 w-2 h-2 bg-blaze-orange rounded-full"></span>
      </button>

      <!-- Профиль -->
      <div class="flex items-center space-x-3">
        <AppAvatar :name="user.name" size="md" />
        <div class="hidden md:block text-sm">
          <p class="font-medium text-charcoal-blue">{{ user.name }}</p>
          <p class="text-gray-500">{{ user.email }}</p>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import AppInput from './ui/AppInput.vue'
import AppAvatar from './ui/AppAvatar.vue'

const search = ref('')
const user = {
  name: 'Алексей Иванов',
  email: 'alex@example.com'
}
</script>