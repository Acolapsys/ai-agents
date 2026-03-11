import ApiService from '../ApiService'
import logger from '../Logger'

class GatewayService extends ApiService {
  constructor() {
    super()
   }

  async checkHealth() {
    try {
      const { data } = await this.get('/health')
      return { ok: true, data }
    } catch (e) {
      logger.error('Gateway health check failed', e)
      return { ok: false, error: e.message }
    }
  }
}

export default new GatewayService()