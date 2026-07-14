/**
 * 后端 API 入口(v3)
 *  - 共享 axios 实例(超时 15s,GET 自动重试 1 次)
 *  - 全部接口返回剥壳后的 data 字段(raw 字段名为 `.raw.data`)
 *  - 与 src/types/apiTypes.ts 中的契约一致
 */
import httpClient from './httpClient'

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

async function get(path, params) {
  const r = await httpClient.get(path + qs(params))
  const body = r.data
  return (body && Object.prototype.hasOwnProperty.call(body, 'data')) ? body.data : body
}

async function getRaw(path, params) {
  const r = await httpClient.get(path + qs(params))
  return r.data
}

export const api = {
  // ===== 基础 =====
  health: () => getRaw('/health'),

  // ===== 大屏聚合 =====
  dashboard: () => getRaw('/dashboard/summary'),
  dashboardExtended: () => getRaw('/dashboard/summary_extended'),

  // ===== 维度计数 =====
  byGenre: () => get('/movies/count_by_genre'),
  byCountry: () => get('/movies/count_by_country'),
  byYear: () => get('/movies/count_by_year'),
  byAvg: (dim = 'genre', limit = 10) => get('/movies/count_by_avg', { dim, limit }),
  byDirector: (limit = 10) => get('/movies/count_by_director', { limit }),
  byLanguage: (limit = 10) => get('/movies/count_by_language', { limit }),
  byDecade: (limit = 20) => get('/movies/count_by_decade', { limit }),

  // ===== 分布 =====
  ratingDistribution: () => get('/movies/rating_distribution'),
  runtimeDistribution: () => get('/movies/runtime_distribution'),

  // ===== 榜单/详情 =====
  topRated: (limit = 50) => get('/movies/top_rated', { limit }),
  detail: (id) => get(`/movies/${encodeURIComponent(id)}`),
  related: (id, limit = 10) => get(`/movies/${encodeURIComponent(id)}/related`, { limit }),
  neighbors: (id) => get(`/movies/${encodeURIComponent(id)}/neighbors`),

  // ===== 分页/搜索 =====
  paged: (params = {}) => get('/movies/paged', params),
  search: (q, limit = 20) => get('/movies/search', { q, limit }),

  // ===== 高级视图 =====
  sankeyFlow: (gTop = 6, cTop = 5, dTop = 5) =>
    get('/sankey/flow', { top: `${gTop},${cTop},${dTop}` }),
  treemapGenreCountry: () => get('/treemap/genre-country'),
  calendarMonthly: (year) => get('/calendar/monthly', year ? { year } : {}),
  networkCollaborations: (type = 'director', limit = 40) =>
    get('/network/collaborations', { type, limit }),
  mapCountries: () => get('/map/countries'),
}

export default api