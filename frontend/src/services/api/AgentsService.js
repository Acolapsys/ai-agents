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
    const { data } = await this.get('/agents')
    return data // уже массив, как сформировали в gateway
  }
}

export default new AgentsService()