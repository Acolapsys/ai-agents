import { defineStore } from 'pinia'
import gatewayService from '@/services/api/GatewayService'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messagesByChat: {}, // ключ: `${agentId}_${chatId}`
    loading: false,
    error: null
  }),

  actions: {
    // Загрузка истории
    async fetchHistory(agentId, chatId = 'web') {
      const key = `${agentId}_${chatId}`
      if (this.messagesByChat[key]) return // уже загружено

      this.loading = true
      this.error = null
      try {
        const history = await gatewayService.getHistory(agentId, chatId, 50)
        // Преобразуем в формат с isMine
        this.messagesByChat[key] = history.map(msg => ({
          ...msg,
          isMine: msg.role === 'user',
          id: msg.timestamp // можно использовать timestamp как временный id
        }))
      } catch (e) {
        this.error = e.message
        this.messagesByChat[key] = []
      } finally {
        this.loading = false
      }
    },

    // Добавить сообщение (оптимистичное добавление)
    addMessage(agentId, chatId, message) {
      const key = `${agentId}_${chatId}`
      if (!this.messagesByChat[key]) this.messagesByChat[key] = []
      this.messagesByChat[key].push(message)
    },

    // Отправка нового сообщения
    async sendMessage(agentId, text, chatId = 'web') {
      const key = `${agentId}_${chatId}`

      // Оптимистичное добавление сообщения пользователя
      const userMessage = {
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
        isMine: true,
        id: `user-${Date.now()}`
      }
      this.addMessage(agentId, chatId, userMessage)

      try {
        const response = await gatewayService.sendMessage(agentId, text, 'web_user', chatId)

        // Добавляем ответ ассистента
        const assistantMessage = {
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString(),
          isMine: false,
          id: `assistant-${Date.now()}`
        }
        this.addMessage(agentId, chatId, assistantMessage)

        return response
      } catch (e) {
        // В случае ошибки добавляем сообщение об ошибке
        const errorMessage = {
          role: 'assistant',
          content: `❌ Ошибка: ${e.message}`,
          timestamp: new Date().toISOString(),
          isMine: false,
          id: `error-${Date.now()}`
        }
        this.addMessage(agentId, chatId, errorMessage)
        throw e
      }
    },

    // Очистить историю для конкретного чата
    clearHistory(agentId, chatId = 'web') {
      const key = `${agentId}_${chatId}`
      delete this.messagesByChat[key]
    }
  },

  getters: {
    // Получить сообщения для конкретного чата
    getMessages: (state) => (agentId, chatId = 'web') => {
      const key = `${agentId}_${chatId}`
      return state.messagesByChat[key] || []
    }
  }
})