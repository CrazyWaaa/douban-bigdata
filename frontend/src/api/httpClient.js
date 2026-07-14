/**
 * 共享 axios 实例
 *  - 超时 15s
 *  - GET 自动重试 1 次(网络错 / 5xx),重试请求继续走 baseURL
 *  - 若 window.__API_KEY__ 存在,向后台透传(用于生产 DOUBAN_API_KEY 鉴权)
 */
import axios from 'axios'

export const httpClient = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截:透传 X-API-Key(若 window.__API_KEY__ 存在)
httpClient.interceptors.request.use((cfg) => {
  if (typeof window !== 'undefined' && window.__API_KEY__ && !cfg.headers['X-API-Key']) {
    cfg.headers['X-API-Key'] = String(window.__API_KEY__)
  }
  return cfg
})

httpClient.interceptors.response.use(
  (r) => r,
  async (err) => {
    const cfg = err.config || {}
    const retryable = !cfg.__retried && (cfg.method || 'get').toLowerCase() === 'get' && (
      err.code === 'ECONNABORTED' || !err.response || err.response.status >= 500
    )
    if (retryable) {
      cfg.__retried = true
      // 关键:用 httpClient.request 而非 axios.request,保留 baseURL
      try { return await httpClient.request(cfg) } catch (_) { /* fall through */ }
    }
    if (typeof console !== 'undefined') {
      console.error('[api]', err?.response?.status, cfg?.url, err?.message)
    }
    return Promise.reject(err)
  }
)

export default httpClient
