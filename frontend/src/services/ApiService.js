import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

export default class ApiService {
  get(url, config) {
    return apiClient.get(url, config)
  }

  post(url, data, config) {
    return apiClient.post(url, data, config)
  }
}