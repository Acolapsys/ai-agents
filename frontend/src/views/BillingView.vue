<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Биллинг и расходы</h1>

    <!-- Баланс и текущие расходы -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <AppCard>
        <div class="text-center">
          <div class="text-sm text-gray-500">Текущий баланс</div>
          <div class="text-3xl font-bold text-baltic-blue">$124.50</div>
        </div>
      </AppCard>
      <AppCard>
        <div class="text-center">
          <div class="text-sm text-gray-500">Расход за месяц</div>
          <div class="text-3xl font-bold text-charcoal-blue">$42.80</div>
        </div>
      </AppCard>
      <AppCard>
        <div class="text-center">
          <div class="text-sm text-gray-500">Лимит токенов</div>
          <div class="text-3xl font-bold text-honey-bronze">85%</div>
        </div>
      </AppCard>
    </div>

    <!-- История транзакций -->
    <AppCard>
      <template #header>
        <span class="font-semibold text-charcoal-blue">История транзакций</span>
      </template>
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-sky-reflection/20">
            <th class="text-left py-2">Дата</th>
            <th class="text-left py-2">Описание</th>
            <th class="text-left py-2">Сумма</th>
            <th class="text-left py-2">Статус</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tx in transactions" :key="tx.id" class="border-b border-sky-reflection/10">
            <td class="py-2">{{ tx.date }}</td>
            <td>{{ tx.description }}</td>
            <td :class="tx.amount > 0 ? 'text-green-600' : 'text-blaze-orange'">
              {{ tx.amount > 0 ? '+' : '-' }}${{ Math.abs(tx.amount).toFixed(2) }}
            </td>
            <td><AppBadge :variant="tx.status === 'completed' ? 'success' : 'warning'">{{ tx.status }}</AppBadge></td>
          </tr>
        </tbody>
      </table>
    </AppCard>

    <!-- Расходы по токенам -->
    <AppCard class="mt-6">
      <template #header>
        <span class="font-semibold text-charcoal-blue">Расход токенов по агентам</span>
      </template>
      <div v-for="agent in tokenUsage" :key="agent.name" class="mb-3">
        <div class="flex justify-between text-sm">
          <span>{{ agent.name }}</span>
          <span>{{ agent.tokens }} токенов</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-baltic-blue h-2 rounded-full" :style="{ width: agent.percentage + '%' }"></div>
        </div>
      </div>
    </AppCard>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'

const transactions = ref([
  { id: 1, date: '2025-03-09', description: 'Пополнение счета', amount: 50.00, status: 'completed' },
  { id: 2, date: '2025-03-08', description: 'Оплата токенов (Семейный советник)', amount: -12.40, status: 'completed' },
  { id: 3, date: '2025-03-07', description: 'Оплата токенов (Telegram)', amount: -23.10, status: 'completed' },
  { id: 4, date: '2025-03-06', description: 'Пополнение счета', amount: 100.00, status: 'pending' },
])

const tokenUsage = ref([
  { name: 'Семейный советник', tokens: 12400, percentage: 45 },
  { name: 'Библиотекарь', tokens: 8200, percentage: 30 },
  { name: 'Telegram-помощник', tokens: 23100, percentage: 84 },
])
</script>