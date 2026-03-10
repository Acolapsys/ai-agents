<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Боковая панель (фиксированная ширина) -->
    <Sidebar />
    <!-- Основная область: шапка + контент -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <AppHeader />
      <main class="flex-1 overflow-auto p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from '@/components/Sidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
</script>