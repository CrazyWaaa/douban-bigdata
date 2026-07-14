/**
 * Dashboard Store(重写)
 * - 字段按"展示分组"管理,便于在视图层按需取用
 * - 每个 group 独立的 load 方法,失败不阻塞其他分组
 * - errors[] 归集各分组错误,便于 UI 分卡降级
 * - 全局计时 + TTL 由 useApiQuery 统一控制
 *
 * 对应真实接口:
 *   GET /api/dashboard/summary
 *   GET /api/dashboard/summary_extended
 *   GET /api/movies/count_by_genre
 *   GET /api/movies/count_by_country
 *   GET /api/movies/count_by_year
 *   GET /api/movies/count_by_avg?dim={genre|country|year}&limit=*
 *   GET /api/movies/count_by_director
 *   GET /api/movies/count_by_language
 *   GET /api/movies/count_by_decade
 *   GET /api/movies/rating_distribution
 *   GET /api/movies/runtime_distribution
 *   GET /api/movies/top_rated?limit=20
 */
import { defineStore } from 'pinia'
import { api } from '../api'
import { invalidate, prefetchQueries } from '../composables/useApiQuery'

const TTL = 60_000

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    summary: null,
    summaryExt: null,
    genres: [],
    countries: [],
    years: [],
    avgByGenre: [],
    avgByCountry: [],
    avgByYear: [],
    directors: [],
    languages: [],
    decades: [],
    ratingDist: [],
    runtimeDist: [],
    topRated: [],
    groupLoading: {
      core: false, secondary: false, distribution: false, topRated: false,
    },
    errors: {},
    lastLoadedAt: 0,
  }),
  getters: {
    /** 维度合计有效类型桶(去掉 ETL 错放的年份/国家) */
    validGenres(state) {
      // 动态 import 避免循环依赖(在 getter 里用 lazy 引)
      const isGeoOrYear = (name) => {
        if (!name) return true
        const s = String(name).trim()
        if (/^\d{4}$/.test(s)) return true
        if (/^\d{4}\(/.test(s)) return true
        if (/(中国大陆|中国香港|中国台湾|美国|日本|英国|韩国|法国|德国|意大利|西班牙|加拿大|澳大利亚|泰国|俄罗斯|印度|新加坡|马来西亚)/.test(s)) return true
        return false
      }
      return state.genres.filter((g) => g && !isGeoOrYear(g.name))
    },
    /** KPI 卡的"最受关注"对象(若后端返回) */
    topFocus(state) {
      const s = state.summaryExt
      if (!s || !s.top_rating_count || !s.top_rating_count_title) return null
      return { title: s.top_rating_count_title, ratingCount: s.top_rating_count }
    },
  },
  actions: {
    markLoading(group, on) {
      this.groupLoading[group] = on
    },
    setError(group, e) {
      if (e) this.errors[group] = (e?.response?.data?.message || e?.message || String(e))
      else delete this.errors[group]
    },
    async loadCore() {
      this.markLoading('core', true)
      try {
        const [sum, ext] = await Promise.allSettled([api.dashboard(), api.dashboardExtended()])
        this.summary  = sum.status  === 'fulfilled' ? sum.value  : null
        this.summaryExt = ext.status === 'fulfilled' ? ext.value : null
        this.setError('summary', sum.status  === 'rejected' ? sum.reason  : null)
        this.setError('summaryExt', ext.status === 'rejected' ? ext.reason : null)
      } finally {
        this.markLoading('core', false)
      }
    },
    async loadSecondary() {
      this.markLoading('secondary', true)
      try {
        const tasks = await Promise.allSettled([
          api.byGenre(),
          api.byCountry(),
          api.byYear(),
          api.byAvg('genre', 10),
          api.byAvg('country', 10),
          api.byAvg('year', 30),
          api.byDirector(10),
          api.byLanguage(10),
          api.byDecade(20),
        ])
        const list = [
          ['genres', 0], ['countries', 1], ['years', 2],
          ['avgByGenre', 3], ['avgByCountry', 4], ['avgByYear', 5],
          ['directors', 6], ['languages', 7], ['decades', 8],
        ]
        list.forEach(([field, idx], i) => {
          const t = tasks[i]
          if (t.status === 'fulfilled') {
            this[field] = Array.isArray(t.value) ? t.value : []
            this.setError(field, null)
          } else {
            this.setError(field, t.reason)
          }
        })
      } finally {
        this.markLoading('secondary', false)
      }
    },
    async loadDistribution() {
      this.markLoading('distribution', true)
      try {
        const tasks = await Promise.allSettled([
          api.ratingDistribution(),
          api.runtimeDistribution(),
        ])
        if (tasks[0].status === 'fulfilled') { this.ratingDist = tasks[0].value; this.setError('ratingDist', null) }
        else this.setError('ratingDist', tasks[0].reason)
        if (tasks[1].status === 'fulfilled') { this.runtimeDist = tasks[1].value; this.setError('runtimeDist', null) }
        else this.setError('runtimeDist', tasks[1].reason)
      } finally {
        this.markLoading('distribution', false)
      }
    },
    async loadTopRated() {
      this.markLoading('topRated', true)
      try {
        const data = await api.topRated(20)
        this.topRated = Array.isArray(data) ? data : []
        this.setError('topRated', null)
      } catch (e) {
        this.setError('topRated', e)
        this.topRated = []
      } finally {
        this.markLoading('topRated', false)
      }
    },
    /** 首屏优先:core(摘要)+ topRated(右侧名次)+ ratingDist(评分分布);其余后台进入 */
    async loadAll() {
      this.lastLoadedAt = 0
      await Promise.allSettled([
        this.loadCore(),
        this.loadTopRated(),
        this.loadDistribution(),
      ])
      this.lastLoadedAt = Date.now()
      // 二级聚合在主屏显示后再后台请求
      this.loadSecondary().then(() => { /* 后台 */ })
    },
    /** 手动刷新:清缓存后整体重拉 */
    refresh() {
      invalidate('dashboard:')
      invalidate('topRated:')
      invalidate('dist:')
      return this.loadAll()
    },
    /** 进入大屏前预热接口(尤其在切换路由时加速首屏) */
    prefetch() {
      return prefetchQueries([
        ['dashboard:summary', () => api.dashboard()],
        ['dashboard:summaryExt', () => api.dashboardExtended()],
        ['dashboard:topRated', () => api.topRated(10)],
        ['dist:rating', () => api.ratingDistribution()],
        ['dist:runtime', () => api.runtimeDistribution()],
      ], TTL)
    },
  },
})