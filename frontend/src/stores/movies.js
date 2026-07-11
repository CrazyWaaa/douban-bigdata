import { defineStore } from 'pinia'
import { api } from '../api'

/**详情页 store：缓存最近访问过的电影详情，避免重复请求。*/
export const useMoviesStore = defineStore('movies', {
  state: () => ({
    cache: {}, // douban_id -> movie dict
    loadingId: '',
    error: '',
  }),
  actions: {
    async fetchDetail(doubanId) {
      if (this.cache[doubanId]) return this.cache[doubanId]
      this.loadingId = doubanId
      this.error = ''
      try {
        const data = await api.detail(doubanId)
        this.cache[doubanId] = data
        return data
      } catch (e) {
        this.error = e.message || String(e)
        return null
      } finally {
        this.loadingId = ''
      }
    },
  },
})