import { defineStore } from 'pinia'
import gatewayService from '@/services/api/GatewayService'
import processManager from '@/services/api/ProcessManagerService'
import dashboardService from '@/services/api/DashboardService'

export const useServiceStatusStore = defineStore('serviceStatus', {
  state: () => ({
    gateway: { ok: false, lastCheck: null },
    processManager: { ok: false, lastCheck: null },
    taskManager: { ok: false, lastCheck: null },
    agents: [],
    tasks: [],
    importantEvents: []
  }),

  actions: {
    async checkAll() {
      const data = await dashboardService.getDashboard()
      this.gateway = { ok: data.gateway?.status === 'ok', lastCheck: new Date() }
      this.processManager = { ok: data.processManager?.status === 'ok', lastCheck: new Date() }
      this.taskManager = { ok: data.taskManager?.status === 'ok', lastCheck: new Date() }
      this.agents = data.agents || []
      this.tasks = data.tasks || []
      this.importantEvents = data.importantEvents || []
    },

    startAutoCheck(interval = 30000) {
      this.checkAll()
      this.interval = setInterval(() => this.checkAll(), interval)
    },

    stopAutoCheck() {
      if (this.interval) {
        clearInterval(this.interval)
        this.interval = null
      }
    },
  },
})