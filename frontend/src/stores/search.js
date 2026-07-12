import { defineStore } from 'pinia'
import { api } from '../api'

/** 全局搜索 store:防抖由视图层控制,这里只管最近一次结果。 */
export const useSearchStore = defineStore('search', {
  state: () => ({
    q: '',
    results: [],
    loading: false,
    error: '',
  }),
  actions: {
    async run(q) {
      this.q = q
      this.error = ''
      if (!q || !q.trim()) {
        this.results = []
        return
      }
      this.loading = true
      try {
        this.results = (await api.search(q.trim(), 30))?.data || []
      } catch (e) {
        this.error = e?.message || String(e)
        this.results = []
      } finally {
        this.loading = false
      }
    },
  },
})