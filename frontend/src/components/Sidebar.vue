<template>
  <aside class="w-64 bg-charcoal-blue text-white flex flex-col shadow-lg">
    <!-- Заголовок с названием и слоганом -->
    <div class="p-4 border-b border-sky-reflection/20">
      <div class="text-2xl font-bold tracking-tight flex items-center gap-2">
        <span class="text-honey-bronze text-3xl">✦</span>
        <span>Nexus</span>
      </div>
      <div class="text-xs text-sky-reflection/80 mt-1 italic">
        Точка притяжения. Собирая камни.
      </div>
    </div>

    <!-- Навигация -->
    <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center px-3 py-2 rounded-lg transition-all duration-200 group"
        active-class="bg-honey-bronze text-charcoal-blue font-medium"
        :class="{
          'hover:bg-baltic-blue hover:text-white': $route.path !== item.path,
        }"
      >
        <span class="w-6 h-6 mr-3 flex items-center justify-center text-lg transition-transform group-hover:scale-110">
          {{ item.icon }}
        </span>
        <span>{{ item.name }}</span>
      </router-link>
    </nav>

    <!-- Футер с версией и доп. информацией -->
    <div class="p-4 border-t border-sky-reflection/20 text-xs text-sky-reflection space-y-1">
      <div class="flex items-center gap-1">
        <span class="opacity-50">⚙️</span>
        <span>Nexus v1.0.0</span>
      </div>
      <div class="text-[10px] opacity-40">
        Система управления AI-агентами
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'

const menuItems = [
  { name: 'Дашборд', path: '/', icon: '📊' },
  { name: 'Чаты агентов', path: '/chats', icon: '💬' },
  { name: 'Управление агентами', path: '/agents', icon: '🤖' },
  { name: 'Логи', path: '/logs', icon: '📋' },
  { name: 'Таск-трекер', path: '/tasks', icon: '✅' },
  { name: 'Статистика', path: '/stats', icon: '📈' },
  { name: 'Биллинг', path: '/billing', icon: '💰' },
  { name: 'Личные данные', path: '/profile', icon: '👤' },
  { name: 'Библиотека аудиокниг', path: '/library', icon: '🎧' },
]

const route = useRoute()
</script>

<style scoped>
.router-link-active {
  background-color: #f6ae2d; /* honey-bronze */
  color: #2f4858; /* charcoal-blue */
  font-weight: 500;
}
</style>