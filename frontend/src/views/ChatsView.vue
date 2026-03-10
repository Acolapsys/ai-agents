<template>
  <div class="p-6 h-[calc(100vh-8rem)] flex flex-col">
    <h1 class="text-2xl font-bold text-charcoal-blue mb-6">Чаты агентов</h1>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
      <!-- Список агентов слева -->
      <AppCard class="lg:col-span-1 flex flex-col">
        <template #header>
          <div class="flex justify-between items-center">
            <span class="font-semibold text-charcoal-blue">Диалоги</span>
            <span class="text-xs text-gray-500">{{ agents.length }} агентов</span>
          </div>
        </template>

        <div class="flex-1 overflow-y-auto">
          <div class="space-y-2">
            <div
              v-for="agent in agents"
              :key="agent.id"
              class="p-3 rounded-lg cursor-pointer transition-all duration-200"
              :class="
                selectedChat?.id === agent.id
                  ? 'bg-sky-reflection/20 border-l-4 border-baltic-blue'
                  : 'hover:bg-gray-100'
              "
              @click="selectChat(agent)"
            >
              <div class="flex items-center">
                <div class="w-8 h-8 rounded-full bg-baltic-blue/10 flex items-center justify-center mr-3">
                  <span class="text-baltic-blue text-sm">🤖</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-charcoal-blue truncate">{{ agent.name }}</div>
                  <div class="text-sm text-gray-500 truncate">
                    {{ getLastMessage(agent.id) || 'Начните диалог...' }}
                  </div>
                </div>
                <div
                  v-if="unreadCount[agent.id]"
                  class="w-5 h-5 rounded-full bg-baltic-blue flex items-center justify-center ml-2"
                >
                  <span class="text-white text-xs">{{ unreadCount[agent.id] }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </AppCard>

      <!-- Область сообщений справа -->
      <AppCard class="lg:col-span-2 flex flex-col">
        <template #header>
          <div class="flex justify-between items-center">
            <span v-if="selectedChat" class="font-semibold text-charcoal-blue">
              {{ selectedChat.name }}
            </span>
            <span v-else class="text-gray-500">Выберите чат</span>

            <div v-if="selectedChat" class="flex space-x-2">
              <button
                class="p-1 rounded hover:bg-gray-100"
                @click="copyCodeToClipboard"
                title="Копировать код в буфер обмена"
              >
                📋
              </button>
              <button
                class="p-1 rounded hover:bg-gray-100"
                @click="clearChat"
                title="Очистить диалог"
              >
                🗑️
              </button>
            </div>
          </div>
        </template>

        <div v-if="selectedChat" class="flex flex-col flex-1 min-h-0">
          <!-- Контейнер для сообщений - занимает всё свободное место -->
          <div
            class="flex-1 overflow-y-auto space-y-4 p-4 bg-gray-50/50 rounded-lg custom-scrollbar"
            ref="messagesContainerRef"
          >
            <div
              v-if="currentMessages.length === 0"
              class="flex items-center justify-center h-full text-gray-500"
            >
              Начните диалог с {{ selectedChat.name }}
            </div>

            <div
              v-for="msg in currentMessages"
              :key="msg.id"
              class="flex"
              :class="msg.isMine ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-[80%] p-3 rounded-2xl shadow-sm relative"
                :class="
                  msg.isMine
                    ? 'bg-baltic-blue text-white rounded-br-none'
                    : 'bg-white text-charcoal-blue border border-gray-200 rounded-bl-none'
                "
              >
                <div
                  v-if="containsCode(msg.content)"
                  class="absolute top-2 right-2"
                >
                  <button
                    @click="copyMessageCode(msg.content)"
                    class="text-xs p-1 rounded hover:bg-black/10"
                    :title="getCopyButtonTitle(msg.content)"
                  >
                    📋
                  </button>
                </div>

                <div
                  v-html="renderMarkdown(msg.content)"
                  class="prose prose-sm max-w-none"
                  :class="msg.isMine ? 'prose-invert' : ''"
                />
                <div
                  class="text-xs mt-1"
                  :class="msg.isMine ? 'text-baltic-blue/70' : 'text-gray-500'"
                >
                  {{ formatTime(msg.timestamp) }}
                </div>
              </div>
            </div>

            <div
              v-if="loadingByAgent[selectedChat?.id]"
              class="flex justify-start"
            >
              <div class="bg-white text-charcoal-blue rounded-2xl px-4 py-3 border border-gray-200 rounded-bl-none">
                <span class="typing-indicator">печатает</span>
              </div>
            </div>
          </div>

          <!-- Поле ввода - всегда внизу -->
          <div class="border-t border-gray-100 p-4">
            <ChatInput
              v-model="newMessage"
              @send="sendMessage"
              :disabled="!selectedChat || loadingByAgent[selectedChat?.id]"
            />
          </div>
        </div>

        <div v-else class="flex-1 flex items-center justify-center text-gray-500">
          Выберите чат для начала общения
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

import { ref, onMounted, nextTick, computed, watch } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import ChatInput from '@/components/ChatInput.vue'
import agentsService from '@/services/api/AgentsService'

const md = new MarkdownIt({
  highlight: (str, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return (
          '<pre class="hljs rounded-lg"><code>' +
          hljs.highlight(str, { language: lang }).value +
          '</code></pre>'
        )
      } catch (__) {}
    }
    return (
      '<pre class="hljs rounded-lg"><code>' + md.utils.escapeHtml(str) + '</code></pre>'
    )
  },
  linkify: true,
  breaks: true
})

const renderMarkdown = (content = '') => md.render(content)

const agents = ref([])
const messagesByAgent = ref({}) // { agentId: [{ id, role, content, timestamp }] }
const loadingByAgent = ref({})
const unreadCount = ref({}) // Для отслеживания непрочитанных сообщений

const messagesContainerRef = ref(null)
const selectedChat = ref(null)
const newMessage = ref('')

// Вычисляемые сообщения для текущего чата
const currentMessages = computed(() => {
  if (!selectedChat.value) return []
  return messagesByAgent.value[selectedChat.value.id] || []
})

// Проверка наличия кода в сообщении
const containsCode = (content) => {
  return /```[\s\S]*?```|`[^`]+`/.test(content)
}

// Получение заголовка для кнопки копирования
const getCopyButtonTitle = (content) => {
  if (content.includes('```')) {
    return 'Копировать блок кода'
  }
  if (content.includes('`')) {
    return 'Копировать код'
  }
  return 'Копировать'
}

// Копирование кода из сообщения
const copyMessageCode = async (content) => {
  try {
    // Извлекаем код из markdown
    let codeToCopy = content

    // Если есть блоки кода
    if (content.includes('```')) {
      const codeBlocks = content.match(/```(?:\w+)?\n([\s\S]*?)```/g)
      if (codeBlocks) {
        codeToCopy = codeBlocks.map(block => {
          return block.replace(/```(?:\w+)?\n/, '').replace(/```$/, '')
        }).join('\n\n')
      }
    }
    // Если есть inline код
    else if (content.includes('`')) {
      const inlineCodes = content.match(/`([^`]+)`/g)
      if (inlineCodes) {
        codeToCopy = inlineCodes.map(code => code.slice(1, -1)).join('\n')
      }
    }

    await navigator.clipboard.writeText(codeToCopy)
  } catch (err) {
    console.error('Ошибка копирования:', err)
  }
}

// Копирование всего кода из диалога
const copyCodeToClipboard = async () => {
  try {
    const messages = currentMessages.value
    let codeContent = ''

    messages.forEach(msg => {
      if (containsCode(msg.content)) {
        // Извлекаем код из сообщения
        let extractedCode = msg.content

        if (msg.content.includes('```')) {
          const codeBlocks = msg.content.match(/```(?:\w+)?\n([\s\S]*?)```/g)
          if (codeBlocks) {
            extractedCode = codeBlocks.map(block => {
              return block.replace(/```(?:\w+)?\n/, '').replace(/```$/, '')
            }).join('\n\n')
          }
        } else if (msg.content.includes('`')) {
          const inlineCodes = msg.content.match(/`([^`]+)`/g)
          if (inlineCodes) {
            extractedCode = inlineCodes.map(code => code.slice(1, -1)).join('\n')
          }
        }

        codeContent += `${extractedCode}\n\n`
      }
    })

    if (codeContent) {
      await navigator.clipboard.writeText(codeContent.trim())
    }
  } catch (err) {
    console.error('Ошибка копирования кода:', err)
  }
}

const selectChat = (chat) => {
  selectedChat.value = chat
  // Сбрасываем счетчик непрочитанных при выборе чата
  unreadCount.value[chat.id] = 0
  scrollToBottom()
}

const clearChat = () => {
  if (selectedChat.value) {
    messagesByAgent.value[selectedChat.value.id] = []
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedChat.value || loadingByAgent.value[selectedChat.value.id]) return

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

    // Увеличиваем счетчик непрочитанных, если чат не активен
    if (selectedChat.value?.id !== agentId) {
      unreadCount.value[agentId] = (unreadCount.value[agentId] || 0) + 1
    }
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

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Автоматическая прокрутка при новых сообщениях
watch(currentMessages, () => {
  scrollToBottom()
})

onMounted(() => {
  getAgents()
})
</script>

<style scoped>
.typing-indicator::after {
  content: '.';
  animation: typing 1.4s infinite;
}

@keyframes typing {
  0% { content: '.'; }
  33% { content: '..'; }
  66% { content: '...'; }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(51, 101, 138, 0.3);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(51, 101, 138, 0.5);
}

.messages-container {
  scroll-behavior: smooth;
}

/* Дополнительные стили для markdown */
:deep(.hljs) {
  padding: 1rem;
  margin: 0.5rem 0;
  border-radius: 0.5rem;
}

:deep(pre) {
  overflow-x: auto;
}

:deep(code) {
  font-family: 'Fira Code', monospace;
}
</style>