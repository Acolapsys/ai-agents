import ApiService from '../ApiService'
import logger from '../Logger'

class ProcessManagerService extends ApiService {
  constructor() {
    const baseURL = import.meta.env.VITE_PROCESS_MANAGER_URL
    super(baseURL)
  }

  async getAgents() {
    const { data } = await this.get('/agents')
    return data
  }

  async startAgent(agentId) {
    const { data } = await this.post(`/agents/${agentId}/start`, {})
    return data
  }

  async stopAgent(agentId) {
    const { data } = await this.post(`/agents/${agentId}/stop`, {})
    return data
  }

  async restartAgent(agentId) {
    const { data } = await this.post(`/agents/${agentId}/restart`, {})
    return data
  }
}

export default new ProcessManagerService()