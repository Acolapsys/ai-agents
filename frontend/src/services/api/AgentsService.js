import ApiService from '../ApiService'
import logger from '../Logger'

class AgentsService extends ApiService {
  constructor() {
    super()
  }

  async sendMessage(agentId, message, userId = 'web_user', chatId = 'web') {
    const { data } = await this.post(`/chat/${agentId}`, {
      message,
      user_id: userId,
      chat_id: chatId,
    })
    return data
  }

  async getHistory(agentId, chatId = 'web', limit = 50) {
    try {
      const { data } = await this.get(`/history/${agentId}`, {
        params: { chat_id: chatId, limit }
      })
      return data
    } catch (e) {
      logger.error('Failed to load chat history', e)
      return []
    }
  }

  async getAgents() {
    // пока мок, потом заменим на реальный вызов
    return [
      { id: 'designer', name: 'Дизайнер' },
      { id: 'mentor', name: 'Ментор' },
      { id: 'secretary', name: 'Секретарь' },
      { id: 'family', name: 'Семейный советник' },
      { id: 'architect', name: 'Архитектор' },
      { id: 'english_mentor', name: 'Учитель английского' },
    ]
  }
}

export default new AgentsService()