import ApiService from '../ApiService'

class TaskManagerService extends ApiService {
  constructor() {
    const baseURL = import.meta.env.VITE_TASK_MANAGER_URL || 'http://localhost:8009'
    super(baseURL)
  }

  async getTasks(params = {}) {
    const { data } = await this.get('/tasks', { params })
    return data
  }

  async getTask(id) {
    const { data } = await this.get(`/tasks/${id}`)
    return data
  }

  async createTask(task) {
    const { data } = await this.post('/tasks', task)
    return data
  }

  async updateTask(id, task) {
    const { data } = await this.put(`/tasks/${id}`, task)
    return data
  }

  async deleteTask(id) {
    const { data } = await this.delete(`/tasks/${id}`)
    return data
  }

  async checkHealth() {
    try {
      const { data } = await this.get('/health')
      return { ok: true, data }
    } catch (e) {
      logger.error('TaskManager health check failed', e)
      return { ok: false, error: e.message }
    }
  }

  async getLastLogs(lines = 5) {
    try {
      const { data } = await this.get(`/logs/last?lines=${lines}`)
      return data.logs || []
    } catch (e) {
      logger.error('Failed to get last logs', e)
      return []
    }
  }
}

export default new TaskManagerService()