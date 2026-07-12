import { defineStore } from 'pinia'
import { api } from '../api'

/** 影片详情 store:缓存最近访问的影片,避免重复请求。 */
export const useMoviesStore = defineStore('movies', {
  state: () => ({
    cache: {},         // douban_id -> movie dict
    relatedCache: {},  // douban_id -> movie[]
    neighborsCache: {},// douban_id -> {prev, next}
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
        this.error = e?.message || String(e)
        return null
      } finally {
        this.loadingId = ''
      }
    },
    async fetchRelated(doubanId, limit = 10) {
      if (this.relatedCache[doubanId]) return this.relatedCache[doubanId]
      try {
        const data = await api.related(doubanId, limit)
        this.relatedCache[doubanId] = Array.isArray(data) ? data : []
        return this.relatedCache[doubanId]
      } catch {
        return []
      }
    },
    async fetchNeighbors(doubanId) {
      if (this.neighborsCache[doubanId]) return this.neighborsCache[doubanId]
      try {
        const data = await api.neighbors(doubanId)
        this.neighborsCache[doubanId] = data && typeof data === 'object' ? data : { prev: null, next: null }
        return this.neighborsCache[doubanId]
      } catch {
        return { prev: null, next: null }
      }
    },
  },
})