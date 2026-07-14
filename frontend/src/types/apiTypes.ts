/**
 * 豆瓣电影 TOP250 · 前端数据契约
 * 来源:
 *   - docs/schema.sql (MySQL 表结构)
 *   - backend/services/movies.py (序列化输出)
 *   - 实测 /api/dashboard/summary_extended 与 /api/movies/count_by_* 返回样本
 *
 * 仅做运行期校验/智能提示用,不做外部依赖。所有字段均可空,UI 需容错。
 */

/** 评分人数字典(后端 rating_stars JSON 字段)。键 1-5 字符串,值为百分比数字 */
export type Stars = { [star in '1' | '2' | '3' | '4' | '5']?: number }

/** 单部电影(Movie.vue / Top.vue 用) */
export interface Movie {
  rank?: number
  douban_id: string
  title: string
  director?: string | null
  actors?: string | null
  genre?: string | null                // "剧情,犯罪"
  country?: string | null              // "美国" / "中国大陆 / 中国香港"
  year?: number | null
  rating?: number | null               // 0-10,1 位小数
  rating_count?: number | null
  summary?: string | null
  poster_url?: string | null           // https 图片
  // 详情扩展字段(可选,/api/movies/<id> 返回)
  detail_url?: string | null
  languages?: string | null
  release_date?: string | null
  runtime?: string | null              // "142分钟"
  runtime_minutes?: number | null
  quote?: string | null
  better_than?: string | null
  also_know_as?: string | null
  imdb_id?: string | null
  official_sites?: string | null
  comment_short_count?: number | null
  comment_review_count?: number | null
  discussion_count?: number | null
  rating_stars?: Stars | null
  related_pics?: string[] | null
}

/** Dashboard 基础聚合(对应 GET /api/dashboard/summary) */
export interface Summary {
  total: number
  avg_rating: number | null
  distinct_genre: number
  distinct_country: number
  distinct_year: number
}

/** Dashboard 扩展聚合(对应 GET /api/dashboard/summary_extended) */
export interface SummaryExt extends Summary {
  avg_rating_count: number | null      // 全部评价总数
  max_rating: number | null            // 9.7
  top_rating_count: number | null      // 评价人数最多的那部
  top_rating_count_title: string | null
}

/** 维度聚合(name/count/avg_rating),用于 count_by_genre/country/decade/director/language */
export interface AggItem {
  name: string
  count: number
  avg_rating: number | null
}

/** 评分/时长分布桶 */
export interface BucketItem {
  bucket: string
  count: number
}

/** count_by_avg(dim=...) */
export type AvgItem = AggItem & { year?: number }

/** 分页响应 */
export interface Paged<T> {
  data: T[]
  total: number
  page: number
  size: number
}

/** 邻居翻页(详情页前后) */
export interface Neighbor {
  prev: { douban_id: string; title: string } | null
  next: { douban_id: string; title: string } | null
}

/** 安全格式化工具 */
export function safeNum(v: unknown, fallback = 0): number {
  if (v == null) return fallback
  const n = Number(v)
  return Number.isFinite(n) ? n : fallback
}