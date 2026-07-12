import { defineStore } from 'pinia'
import { api } from '../api'

/**
 * Dashboard 大屏 store
 * - summaryExtended:总数/均分/最高分/总评价数/维度数
 * - genres / countries / years:三个主维度(已有)
 * - byAvg(genre/country/year):每个维度 topN + 均分,双轴图用
 * - directors / languages / decades:扩展维度榜
 * - ratingDist / runtimeDist:分布直方图
 * - topRated:大屏右上的高分榜(默认 10)
 */
export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    summary: null,         // 基础 summary
    summaryExt: null,      // 扩展 summary
    genres: [],
    countries: [],
    years: [],
    topRated: [],
    avgByGenre: [],
    avgByCountry: [],
    avgByYear: [],
    directors: [],
    languages: [],
    decades: [],
    ratingDist: [],
    runtimeDist: [],
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
        this.error = e?.message || String(e)
      } finally {
        this.loading = false
      }
    },
    async loadAll() {
      this.loading = true
      this.error = ''
      try {
        const results = await Promise.allSettled([
          api.dashboardExtended(),
          api.byGenre(),
          api.byCountry(),
          api.byYear(),
          api.byAvg('genre', 10),
          api.byAvg('country', 10),
          api.byAvg('year', 30),
          api.byDirector(10),
          api.byLanguage(10),
          api.byDecade(20),
          api.ratingDistribution(),
          api.runtimeDistribution(),
          api.topRated(20),
        ])
        const get = (i) => results[i].status === 'fulfilled' ? results[i].value : null
        this.summaryExt = get(0)
        this.genres     = get(1)?.data || []
        this.countries  = get(2)?.data || []
        this.years      = get(3)?.data || []
        this.avgByGenre   = get(4)?.data || []
        this.avgByCountry = get(5)?.data || []
        this.avgByYear    = get(6)?.data || []
        this.directors    = get(7)?.data || []
        this.languages    = get(8)?.data || []
        this.decades      = get(9)?.data || []
        this.ratingDist   = get(10)?.data || []
        this.runtimeDist  = get(11)?.data || []
        this.topRated     = get(12)?.data || []
        this.lastLoadedAt = Date.now()
        const failed = results.filter(r => r.status === 'rejected')
        if (failed.length) this.error = `${failed.length} 个接口失败`
      } catch (e) {
        this.error = e?.message || String(e)
      } finally {
        this.loading = false
      }
    },
  },
})