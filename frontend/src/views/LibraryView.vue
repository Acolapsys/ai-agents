<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Библиотека аудиокниг</h1>

    <!-- Фильтры и поиск -->
    <div class="flex flex-wrap gap-4 mb-6">
      <AppInput v-model="search" placeholder="Поиск книг..." class="flex-1" />
      <AppSelect v-model="genreFilter" placeholder="Все жанры">
        <option value="">Все жанры</option>
        <option value="fiction">Художественная</option>
        <option value="science">Научная</option>
        <option value="biography">Биография</option>
      </AppSelect>
    </div>

    <!-- Сетка книг -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <AppCard v-for="book in filteredBooks" :key="book.id">
        <template #header>
          <div class="flex justify-between items-start">
            <h3 class="font-semibold text-charcoal-blue">{{ book.title }}</h3>
            <AppBadge variant="info">{{ book.genre }}</AppBadge>
          </div>
        </template>
        <p class="text-sm text-gray-600 mb-2">{{ book.author }}</p>
        <div class="flex items-center justify-between text-sm">
          <span class="flex items-center text-honey-bronze">
            ★ {{ book.rating }}
          </span>
          <span class="text-gray-500">Прослушано: {{ book.listenedCycles }} циклов</span>
        </div>
        <div class="mt-2">
          <div class="flex justify-between text-xs text-gray-500">
            <span>Прогресс</span>
            <span>{{ book.progress }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-1.5">
            <div class="bg-baltic-blue h-1.5 rounded-full" :style="{ width: book.progress + '%' }"></div>
          </div>
        </div>
        <template #footer>
          <div class="flex justify-end">
            <AppButton size="sm" variant="secondary">Продолжить</AppButton>
          </div>
        </template>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'

const search = ref('')
const genreFilter = ref('')

const books = ref([
  { id: 1, title: 'Война и мир', author: 'Лев Толстой', genre: 'fiction', rating: 4.5, listenedCycles: 2, progress: 34 },
  { id: 2, title: 'Краткая история времени', author: 'Стивен Хокинг', genre: 'science', rating: 4.8, listenedCycles: 1, progress: 78 },
  { id: 3, title: 'Стив Джобс', author: 'Уолтер Айзексон', genre: 'biography', rating: 4.7, listenedCycles: 3, progress: 92 },
  { id: 4, title: '1984', author: 'Джордж Оруэлл', genre: 'fiction', rating: 4.6, listenedCycles: 0, progress: 0 },
])

const filteredBooks = computed(() => {
  return books.value.filter(book => {
    const matchesSearch = book.title.toLowerCase().includes(search.value.toLowerCase()) ||
                         book.author.toLowerCase().includes(search.value.toLowerCase())
    const matchesGenre = genreFilter.value ? book.genre === genreFilter.value : true
    return matchesSearch && matchesGenre
  })
})
</script>