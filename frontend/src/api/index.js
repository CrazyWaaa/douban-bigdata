import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 简单重试:GET 类网络错误重试 1 次
client.interceptors.response.use(
  (r) => r.data,
  async (err) => {
    const cfg = err.config || {}
    const retryable = !cfg.__retried && cfg.method === 'get' && (
      err.code === 'ECONNABORTED' || !err.response || err.response.status >= 500
    )
    if (retryable) {
      cfg.__retried = true
      try { return (await axios(cfg)).data } catch (e) { /* fall through */ }
    }
    console.error('API error', err?.response?.status, cfg?.url, err?.message)
    return Promise.reject(err)
  }
)

function qs(params) {
  if (!params) return ''
  const usp = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '') return
    usp.append(k, v)
  })
  const s = usp.toString()
  return s ? `?${s}` : ''
}

export const api = {
  health: () => client.get('/health'),

  // 大屏聚合
  dashboard: () => client.get('/dashboard/summary'),
  dashboardExtended: () => client.get('/dashboard/summary_extended'),

  // 维度聚合
  byGenre: () => client.get('/movies/count_by_genre'),
  byCountry: () => client.get('/movies/count_by_country'),
  byYear: () => client.get('/movies/count_by_year'),
  byAvg: (dim = 'genre', limit = 10) => client.get(`/movies/count_by_avg${qs({ dim, limit })}`),
  byDirector: (limit = 10) => client.get(`/movies/count_by_director${qs({ limit })}`),
  byLanguage: (limit = 10) => client.get(`/movies/count_by_language${qs({ limit })}`),
  byDecade: (limit = 20) => client.get(`/movies/count_by_decade${qs({ limit })}`),

  // 分布
  ratingDistribution: () => client.get('/movies/rating_distribution'),
  runtimeDistribution: () => client.get('/movies/runtime_distribution'),

  // 榜单 / 详情
  topRated: (limit = 50) => client.get(`/movies/top_rated${qs({ limit })}`),
  detail: (id) => client.get(`/movies/${id}`),
  related: (id, limit = 10) => client.get(`/movies/${id}/related${qs({ limit })}`),
  neighbors: (id) => client.get(`/movies/${id}/neighbors`),

  // 分页 / 搜索
  paged: (params = {}) => client.get(`/movies/paged${qs(params)}`),
  search: (q, limit = 20) => client.get(`/movies/search${qs({ q, limit })}`),
}

export default client