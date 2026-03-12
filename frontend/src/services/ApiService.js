import axios from 'axios'

class ApiService {
  constructor(baseURL) {
    this.client = axios.create({
      baseURL: baseURL || import.meta.env.VITE_API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  get(url, config) {
    return this.client.get(url, config)
  }

  post(url, data, config) {
    return this.client.post(url, data, config)
  }

  delete(url, config) {
    return this.client.delete(url, config)
  }

  put(url, config) {
    return this.client.put(url, config)
  }
}

export default ApiService