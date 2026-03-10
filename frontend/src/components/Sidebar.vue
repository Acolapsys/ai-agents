<template>
  <aside class="w-64 bg-charcoal-blue text-white flex flex-col">
    <div class="p-4 text-xl font-bold border-b border-sky-reflection/20">AI Agents Manager</div>
    <nav class="flex-1 p-4 space-y-2">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center px-4 py-2 rounded-lg transition-colors"
        active-class="bg-honey-bronze text-charcoal-blue font-medium"
        :class="{
          'hover:bg-baltic-blue': $route.path !== item.path,
        }"
      >
        <span class="w-5 h-5 mr-3" > {{ item.icon }} </span>
        {{ item.name }}
      </router-link>
    </nav>
    <div class="p-4 border-t border-sky-reflection/20 text-sm text-sky-reflection">
      v1.0.0
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'

// Иконки (можно заменить на любые SVG-компоненты, здесь простые эмодзи)
const menuItems = [
  { name: 'Дашборд', path: '/', icon: '' },
  { name: 'Чаты агентов', path: '/chats', icon: '💬' },
  { name: 'Управление агентами', path: '/agents', icon: '🤖' },
  { name: 'Логи', path: '/logs', icon: '📋' },
  { name: 'Таск-трекер', path: '/tasks', icon: '✅' },
  { name: 'Статистика', path: '/stats', icon: '📊' },
  { name: 'Биллинг', path: '/billing', icon: '💰' },
  { name: 'Личные данные', path: '/profile', icon: '👤' },
  { name: 'Библиотека аудиокниг', path: '/library', icon: '🎧' },
]

const route = useRoute()
</script>

<style scoped>
/* Для иконок-эмодзи (можно заменить на SVG-компоненты) */
.router-link-active {
  background-color: #f6ae2d;
  color: #2f4858;
}
</style>