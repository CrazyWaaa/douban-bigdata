import { useRouter } from 'vue-router'

/**
 * 新页面统一钻取入口:
 * - 节点点击 / 浮层筛选都通过 go() 路由到对应维度页
 * - dim ∈ { genre, country, director, year, decade, language, ratingBucket }
 * - target 不传则根据 dim 自动决定:genre→/genre, country→/country, year→/year, decade→/year, director→/top, ratingBucket→/top
 */
const DIM_TO_ROUTE = {
  genre:        '/genre',
  country:      '/country',
  year:         '/year',
  decade:       '/year',
  director:     '/top',
  language:     '/top',
  ratingBucket: '/top',
}

export function useDrillNav() {
  const router = useRouter()
  function go(dim, value, extra = {}) {
    const path = extra.target || DIM_TO_ROUTE[dim] || '/top'
    const query = { dim, v: String(value) }
    if (extra.q) query.q = extra.q
    if (extra.from) query.from = extra.from
    router.push({ path, query })
  }
  return { go }
}
