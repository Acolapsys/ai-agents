import ApiService from '../ApiService'

class DashboardService extends ApiService {
  constructor() {
    super() // использует базовый URL из ApiService (gateway)
  }

  async getDashboard() {
    const { data } = await this.get('/dashboard')
    return data
  }
}

export default new DashboardService()