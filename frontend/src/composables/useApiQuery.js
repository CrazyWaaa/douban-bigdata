/**
 * useApiQuery: 数据访问通用层
 *  - 单飞(in-flight):同 key 并发请求只发一次
 *  - 内存缓存:默认 60s TTL,过期重拉
 *  - 显式 refresh()/invalidate() 控制
 *  - 数据归一化:服务端返回 { data: [...] } 的剥壳
 *
 * 用法:
 *   const { data, loading, error, refresh } = useApiQuery(
 *     'dashboard.summary',
 *     () => api.summary()
 *   )
 */
import { ref, shallowRef } from 'vue'

const inflight = new Map()  // key -> Promise
const cache = new Map()     // key -> { at: ts, ttl: ms, data: any }

function now() { return Date.now() }

function evictIfExpired(entry, max = 256) {
  // 简易 LRU 旁路:超过最大条数清空一半
  if (cache.size <= max) return
  const arr = [...cache.entries()].sort((a, b) => a[1].at - b[1].at)
  const drop = Math.floor(arr.length / 2)
  for (let i = 0; i < drop; i++) cache.delete(arr[i][0])
}

/** 暴露给上层用的全局失效接口 */
export function invalidate(keyPattern) {
  if (!keyPattern) { cache.clear(); return }
  for (const k of cache.keys()) {
    if (typeof keyPattern === 'string' ? k.startsWith(keyPattern) : keyPattern.test(k)) {
      cache.delete(k)
    }
  }
}

/**
 * 同步拿到当前缓存(若有),无副作用。
 */
export function peekCached(key) {
  const entry = cache.get(key)
  if (!entry) return undefined
  if (entry.at + entry.ttl < now()) {
    cache.delete(key)
    return undefined
  }
  return entry.data
}

export function useApiQuery(key, fetcher, opts = {}) {
  const ttl = opts.ttl ?? 60_000
  const immediate = opts.immediate ?? true
  const normalize = opts.normalize ?? ((d) => (d && Array.isArray(d.data)) ? d.data : d)

  const data = shallowRef(undefined)
  const error = ref('')
  const loading = ref(false)
  const lastLoadedAt = ref(0)
  const fromCache = ref(false)

  async function run(force = false) {
    if (!force) {
      const hit = cache.get(key)
      if (hit && hit.at + hit.ttl >= now()) {
        data.value = hit.data
        lastLoadedAt.value = hit.at
        fromCache.value = true
        return hit.data
      }
    }
    if (inflight.has(key)) {
      try {
        const r = await inflight.get(key)
        data.value = r
        return r
      } catch (e) {
        error.value = e?.message || String(e)
        throw e
      }
    }
    loading.value = true
    error.value = ''
    fromCache.value = false
    const p = (async () => {
      try {
        const raw = await fetcher()
        const v = normalize(raw)
        cache.set(key, { at: now(), ttl, data: v })
        evictIfExpired()
        data.value = v
        lastLoadedAt.value = now()
        return v
      } catch (e) {
        error.value = e?.response?.data?.message || e?.message || String(e)
        throw e
      } finally {
        inflight.delete(key)
        loading.value = false
      }
    })()
    inflight.set(key, p)
    try {
      return await p
    } catch (e) {
      throw e
    }
  }

  function refresh() { return run(true) }
  function invalidateKey() {
    cache.delete(key)
    inflight.delete(key)
  }

  if (immediate) {
    // 异步执行,不阻塞初始化
    run().catch(() => { /* 错误已写入 error */ })
  }

  return { data, loading, error, lastLoadedAt, fromCache, refresh, invalidateKey, run }
}

/** 一次性预热:并行 fetch 后写入缓存,常用于路由进入时 */
export async function prefetchQueries(items, ttl = 60_000) {
  const tasks = items.map(([key, fetcher]) =>
    useApiQuery(key, fetcher, { ttl, immediate: false }).run().catch(() => null)
  )
  await Promise.allSettled(tasks)
}