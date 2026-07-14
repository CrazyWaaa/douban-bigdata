/**
 * 数据格式化工具:数字、评分、时长、星级等。
 * 所有函数均容错:null/NaN/undefined/非数字 都会输出一个可读占位。
 */

/** 把任意输入归一为有限数字,否则 fallback */
export function toNum(v, fallback = 0) {
  if (v == null) return fallback
  const n = Number(v)
  return Number.isFinite(n) ? n : fallback
}

/** 1 位小数评分; 0-10 之外的输入返回 "-" */
export function formatRating(v, digits = 1) {
  const n = Number(v)
  if (!Number.isFinite(n) || n < 0 || n > 10) return '-'
  return n.toFixed(digits)
}

/** 评分人数: 1234 -> "1,234"; 650737 -> "65.1 万"; null -> "-" */
export function formatRatingCount(v) {
  const n = Number(v)
  if (!Number.isFinite(n) || n <= 0) return '-'
  if (n >= 100000) return (n / 10000).toFixed(1) + ' 万'
  if (n >= 10000)  return (n / 10000).toFixed(2) + ' 万'
  return n.toLocaleString()
}

/** 中文千分位 + 万:与 formatRatingCount 相似但返回精确值,用于 KPI */
export function formatInt(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '-'
  return Math.round(n).toLocaleString()
}

/** "142分钟" -> { value: 142, unit: '分钟' }; "1h52m" -> 112 */
export function parseRuntime(text) {
  if (!text) return null
  const t = String(text).trim()
  let m = t.match(/(\d+)\s*分钟/)
  if (m) return { value: Number(m[1]), unit: '分钟' }
  m = t.match(/(\d+)\s*h\s*(\d+)\s*m/i)
  if (m) return { value: Number(m[1]) * 60 + Number(m[2]), unit: '分钟' }
  m = t.match(/(\d+)/)
  if (m) return { value: Number(m[1]), unit: '' }
  return null
}

/** 派生星级条(1-5 百分比 → 5 段宽度) */
export function normalizeStars(stars) {
  if (!stars || typeof stars !== 'object') return null
  const arr = ['1', '2', '3', '4', '5'].map((k) => {
    const v = Number(stars[k])
    return Number.isFinite(v) ? Math.max(0, Math.min(100, v)) : 0
  })
  const sum = arr.reduce((a, b) => a + b, 0)
  return { segments: arr, total: sum }
}

/** 类型桶白名单:粗筛"看起来像片单类型"的;有些 csv 串进了国家/年份,被 ETL 错放到类型桶 */
const GENRE_BLACKLIST = new Set([
  '中国大陆', '中国香港', '中国台湾', '美国', '日本', '英国', '韩国',
  '法国', '德国', '意大利', '西班牙', '加拿大', '澳大利亚', '泰国',
  '俄罗斯', '印度', '新加坡', '马来西亚',
])
const YEAR_RE = /^(19|20)\d{2}/
export function isLikelyGenre(name) {
  if (!name) return false
  const s = String(name).trim()
  if (GENRE_BLACKLIST.has(s)) return false
  if (YEAR_RE.test(s)) return false
  if (s.length > 8) return false
  if (/^\d{4}\(/.test(s)) return false
  return true
}

/** 国家合并桶: "美国 / 日本" 这种会算多国,作为整体桶保留,但展开时再拆 */
export function splitCountries(raw) {
  if (!raw) return []
  return Array.from(new Set(String(raw).split(/\s*\/\s*/).map((s) => s.trim()).filter(Boolean)))
}

/** 拆分多值字段:类型/演员 */
export function splitMulti(field, sep = /[,/]/) {
  if (!field) return []
  return Array.from(new Set(String(field).split(sep).map((s) => s.trim()).filter(Boolean)))
}

/** 截断过长文本,保留首尾 */
export function clip(text, max = 60) {
  if (!text) return ''
  const s = String(text)
  return s.length > max ? s.slice(0, max - 1) + '…' : s
}

/** 时间格式化 */
export function formatTime(ts) {
  const d = new Date(ts)
  if (isNaN(d.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/** 影片海报代理 URL(走后端 img-proxy 解决豆瓣防盗链) */
export function posterUrl(absUrl) {
  if (!absUrl) return ''
  // 已经是相对路径就原样返回
  if (absUrl.startsWith('/')) return absUrl
  // http(s) 远程图,代理转一道
  return `/api/img-proxy?url=${encodeURIComponent(absUrl)}`
}