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