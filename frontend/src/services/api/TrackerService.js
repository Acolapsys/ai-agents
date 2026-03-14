import ApiService from '../ApiService'

class TrackerService extends ApiService {
  constructor() {
    const baseURL = import.meta.env.VITE_TRACKER_URL || 'http://localhost:8010'
    super(baseURL)
  }

  async getTasksDaily(days = 30) {
    const { data } = await this.get('/stats/tasks/daily')
    return data
  }

  async getChatByAgent() {
    const { data } = await this.get('/stats/chat/agents')
    return data
  }

  async getHourlyActivity() {
    const { data } = await this.get('/stats/activity/hourly')
    return data
  }

  async getWeekdayActivity() {
    const { data } = await this.get('/stats/activity/weekday')
    return data
  }
}

export default new TrackerService()