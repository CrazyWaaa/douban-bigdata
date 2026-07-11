import { defineStore } from 'pinia'
import { api } from '../api'

/**Dashboard 大屏与首页聚合数据 store。
 * 5 个独立字段：summary / genres / countries / years / topRated
 * loadAll() 并发拉取 5 个接口；loadDashboard() 仅拉汇总（首页用）。
 */
export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    summary: null,
    genres: [],
    countries: [],
    years: [],
    topRated: [],
    loading: false,
    error: '',
    lastLoadedAt: 0,
  }),
  actions: {
    async loadDashboard() {
      this.loading = true
      this.error = ''
      try {
        this.summary = await api.dashboard()
      } catch (e) {
        this.error = e.message || String(e)
      } finally {
        this.loading = false
      }
    },
    async loadAll() {
      this.loading = true
      this.error = ''
      try {
        const [s, g, c, y, t] = await Promise.all([
          api.dashboard(),
          api.byGenre(),
          api.byCountry(),
          api.byYear(),
          api.topRated(10),
        ])
        this.summary = s
        this.genres = g || []
        this.countries = c || []
        this.years = y || []
        this.topRated = t || []
        this.lastLoadedAt = Date.now()
      } catch (e) {
        this.error = e.message || String(e)
      } finally {
        this.loading = false
      }
    },
  },
})