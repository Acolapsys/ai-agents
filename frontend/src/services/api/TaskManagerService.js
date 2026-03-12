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
}

export default new TaskManagerService()