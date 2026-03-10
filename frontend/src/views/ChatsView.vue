<template>
  <div>
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Чаты агентов</h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Список агентов слева -->
      <AppCard class="md:col-span-1">
        <template #header>
          <span class="font-semibold text-charcoal-blue">Диалоги</span>
        </template>
        <div class="space-y-2">
          <div
            v-for="agent in agents"
            :key="agent.id"
            class="p-2 rounded-lg cursor-pointer transition"
            :class="
              selectedChat?.id === agent.id
                ? 'bg-sky-reflection/20'
                : 'hover:bg-gray-100'
            "
            @click="selectChat(agent)"
          >
            <div class="font-medium text-charcoal-blue">{{ agent.name }}</div>
            <div class="text-sm text-gray-500 truncate">
              {{ getLastMessage(agent.id) }}
            </div>
          </div>
        </div>
      </AppCard>

      <!-- Область сообщений справа -->
      <AppCard class="md:col-span-2 flex flex-col">
        <template #header>
          <span v-if="selectedChat" class="font-semibold text-charcoal-blue">{{
            selectedChat.name
          }}</span>
          <span v-else class="text-gray-500">Выберите чат</span>
        </template>

        <div v-if="selectedChat" class="flex flex-col h-96">
          <!-- Сообщения -->
          <div
            class="flex-1 overflow-y-auto space-y-3 p-2 messages-container"
            ref="messagesContainerRef"
          >
            <!-- Используем сообщения из messagesByAgent -->
            <div
              v-for="msg in currentMessages"
              :key="msg.id"
              class="flex"
              :class="msg.isMine ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-xs p-2 rounded-lg"
                :class="
                  msg.isMine
                    ? 'bg-baltic-blue text-white'
                    : 'bg-gray-100 text-charcoal-blue'
                "
              >
                <div v-html="renderMarkdown(msg.content)" />
              </div>
            </div>
            <div
              v-if="loadingByAgent[selectedChat?.id]"
              class="flex justify-start"
            >
              <div class="bg-gray-100 text-charcoal-blue rounded-lg px-4 py-2">
                <span class="typing-indicator">печатает</span>
              </div>
            </div>
          </div>
          <!-- Поле ввода -->
          <div class="flex mt-2">
            <AppInput
              v-model="newMessage"
              placeholder="Введите сообщение..."
              class="flex-1 mr-2"
              @keyup.enter="sendMessage"
            />
            <AppButton @click="sendMessage">Отправить</AppButton>
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

import { ref, onMounted, nextTick, computed } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import agentsService from '@/services/api/AgentsService'

const md = new MarkdownIt({
  highlight: (str, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return (
          '<pre class="hljs"><code>' +
          hljs.highlight(str, { language: lang }).value +
          '</code></pre>'
        )
      } catch (__) {}
    }
    return (
      '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>'
    )
  }
})

const renderMarkdown = (content = '') => md.render(content)

const agents = ref([])

const messagesByAgent = ref({}) // { agentId: [{ id, role, content, timestamp }] }
const loadingByAgent = ref({})   // { agentId: boolean }
const messagesContainerRef = ref(null)

const selectedChat = ref(null)
const newMessage = ref('')

// Вычисляемые сообщения для текущего чата
const currentMessages = computed(() => {
  if (!selectedChat.value) return []
  return messagesByAgent.value[selectedChat.value.id] || []
})

const selectChat = (chat) => {
  selectedChat.value = chat
  // При желании можно загрузить историю с сервера, но пока её нет
  // loadHistory(chat.id)
}

// Функция для загрузки истории (заглушка, можно реализовать позже)
// const loadHistory = async (agentId) => {
//   try {
//     const history = await agentsService.getHistory(agentId)
//     messagesByAgent.value[agentId] = history
//   } catch (e) {
//     console.error('Ошибка загрузки истории', e)
//   }
// }

const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedChat.value) return

  const agentId = selectedChat.value.id
  const userMsg = newMessage.value

  if (!messagesByAgent.value[agentId]) {
    messagesByAgent.value[agentId] = []
  }

  const userMessage = {
    id: `user-${Date.now()}-${Math.random()}`,
    role: 'user',
    content: userMsg,
    isMine: true,
    timestamp: Date.now()
  }
  messagesByAgent.value[agentId].push(userMessage)
  newMessage.value = ''
  loadingByAgent.value[agentId] = true
  scrollToBottom()

  try {
    const response = await agentsService.sendMessage(agentId, userMsg)
    const assistantMessage = {
      id: `assistant-${Date.now()}-${Math.random()}`,
      role: 'assistant',
      content: response.response,
      isMine: false,
      timestamp: Date.now()
    }
    messagesByAgent.value[agentId].push(assistantMessage)
  } catch (error) {
    const errorMessage = {
      id: `error-${Date.now()}`,
      role: 'assistant',
      content: `❌ Ошибка: ${error.message}`,
      isMine: false,
      timestamp: Date.now()
    }
    messagesByAgent.value[agentId].push(errorMessage)
  } finally {
    loadingByAgent.value[agentId] = false
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainerRef.value) {
      messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight
    }
  })
}

const getAgents = async () => {
  agents.value = await agentsService.getAgents()
}

const getLastMessage = (agentId) => {
  const messages = messagesByAgent.value[agentId] || []
  return messages.length ? messages[messages.length - 1].content : ''
}

onMounted(() => {
  getAgents()
})
</script>

<style scoped>
.typing-indicator::after {
  content: '...';
  animation: typing 1.4s infinite;
  width: 1.5em;
  display: inline-block;
  text-align: left;
}
@keyframes typing {
  0% { content: '.'; }
  33% { content: '..'; }
  66% { content: '...'; }
}
</style>