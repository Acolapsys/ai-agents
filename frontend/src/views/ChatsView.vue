<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Чаты агентов</h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Список чатов слева -->
      <AppCard class="md:col-span-1">
        <template #header>
          <span class="font-semibold text-charcoal-blue">Диалоги</span>
        </template>
        <div class="space-y-2">
          <div
            v-for="chat in chats"
            :key="chat.id"
            class="p-2 rounded-lg cursor-pointer transition"
            :class="selectedChat?.id === chat.id ? 'bg-sky-reflection/20' : 'hover:bg-gray-100'"
            @click="selectChat(chat)"
          >
            <div class="font-medium text-charcoal-blue">{{ chat.name }}</div>
            <div class="text-sm text-gray-500 truncate">{{ chat.lastMessage }}</div>
          </div>
        </div>
      </AppCard>

      <!-- Область сообщений справа -->
      <AppCard class="md:col-span-2 flex flex-col">
        <template #header>
          <span v-if="selectedChat" class="font-semibold text-charcoal-blue">{{ selectedChat.name }}</span>
          <span v-else class="text-gray-500">Выберите чат</span>
        </template>

        <div v-if="selectedChat" class="flex flex-col h-96">
          <!-- Сообщения -->
          <div class="flex-1 overflow-y-auto space-y-3 p-2">
            <div
              v-for="msg in selectedChat.messages"
              :key="msg.id"
              class="flex"
              :class="msg.isMine ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-xs p-2 rounded-lg"
                :class="msg.isMine ? 'bg-baltic-blue text-white' : 'bg-gray-100 text-charcoal-blue'"
              >
                {{ msg.text }}
              </div>
            </div>
          </div>
          <!-- Поле ввода -->
          <div class="flex mt-2">
            <AppInput v-model="newMessage" placeholder="Введите сообщение..." class="flex-1 mr-2" @keyup.enter="sendMessage" />
            <AppButton @click="sendMessage">Отправить</AppButton>
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const chats = ref([
  {
    id: 1,
    name: 'Семейный советник',
    lastMessage: 'Привет, как дела?',
    messages: [
      { id: 1, text: 'Привет, как дела?', isMine: false },
      { id: 2, text: 'Всё отлично!', isMine: true },
    ]
  },
  {
    id: 2,
    name: 'Библиотекарь',
    lastMessage: 'Рекомендую книгу "Война и мир"',
    messages: [
      { id: 1, text: 'Рекомендую книгу "Война и мир"', isMine: false },
    ]
  },
])

const selectedChat = ref(null)
const newMessage = ref('')

function selectChat(chat) {
  selectedChat.value = chat
}

function sendMessage() {
  if (!newMessage.value.trim() || !selectedChat.value) return
  selectedChat.value.messages.push({
    id: Date.now(),
    text: newMessage.value,
    isMine: true
  })
  newMessage.value = ''
}
</script>