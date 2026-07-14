import { defineStore } from 'pinia'
import { api } from '../api'
import { invalidate } from '../composables/useApiQuery'

/**
 * 搜索 store - 单一请求单飞,失败/空字符串都收敛到统一状态
 */
export const useSearchStore = defineStore('search', {
  state: () => ({
    q: '',
    results: [],
    loading: false,
    error: '',
    took: 0,
  }),
  actions: {
    async run(q) {
      const norm = String(q || '').trim()
      this.q = norm
      if (!norm) {
        this.results = []
        this.error = ''
        this.loading = false
        this.took = 0
        return
      }
      this.loading = true
      this.error = ''
      const start = performance.now()
      try {
        const data = await api.search(norm, 50)
        this.results = Array.isArray(data) ? data : []
        this.took = Math.round(performance.now() - start)
        invalidate('search:')
      } catch (e) {
        this.error = e?.response?.data?.message || e?.message || String(e)
        this.results = []
        this.took = Math.round(performance.now() - start)
      } finally {
        this.loading = false
      }
    },
  },
})