<template>
  <div>
    <h2>影片详情</h2>
    <div v-if="data" class="card">
      <div class="movie-head">
        <img v-if="data.poster_url" :src="imgSrc(data.poster_url)" class="poster" alt="封面" referrerpolicy="no-referrer" loading="lazy" @error="onImgError($event)">
        <div class="info">
          <h3>{{ data.title }}</h3>
          <div class="muted" style="margin:6px 0;">
            <span v-if="data.year">{{ data.year }}</span>
            <span v-if="data.country"> · {{ data.country }}</span>
            <span v-if="data.genre"> · {{ data.genre }}</span>
          </div>
          <div class="muted" style="margin-bottom:8px;">
            <span v-if="data.director">导演: {{ data.director }}</span>
          </div>
          <div class="muted" style="margin-bottom:8px;">
            <span v-if="data.actors">主演: {{ data.actors }}</span>
          </div>
          <div class="rating-box">
            <span class="rating">{{ data.rating ?? '—' }}</span>
            <span class="muted" v-if="data.rating_count"> · {{ data.rating_count }} 人评价</span>
          </div>
          <div v-if="data.quote" class="quote">"{{ data.quote }}"</div>
        </div>
      </div>

      <div class="divider"></div>

      <div class="extras grid-2">
        <div v-if="data.languages"><b>语言:</b> {{ data.languages }}</div>
        <div v-if="data.release_date"><b>上映日期:</b> {{ data.release_date }}</div>
        <div v-if="data.runtime"><b>片长:</b> {{ data.runtime }}</div>
        <div v-if="data.runtime_minutes"><b>分钟数:</b> {{ data.runtime_minutes }}</div>
        <div v-if="data.also_know_as"><b>又名:</b> {{ data.also_know_as }}</div>
        <div v-if="data.imdb_id"><b>IMDb:</b> {{ data.imdb_id }}</div>
        <div v-if="data.official_sites"><b>官方网站:</b> {{ data.official_sites }}</div>
        <div v-if="data.better_than"><b>好评概况:</b> {{ data.better_than }}</div>
      </div>

      <div v-if="data.comment_short_count || data.comment_review_count" class="grid-2" style="margin-top:12px;">
        <div v-if="data.comment_short_count"><b>短评数:</b> {{ data.comment_short_count }}</div>
        <div v-if="data.comment_review_count"><b>影评数:</b> {{ data.comment_review_count }}</div>
      </div>

      <div v-if="data.rating_stars && Object.keys(data.rating_stars).length" class="stars-box">
        <b>星级占比:</b>
        <ul class="stars-list">
          <li v-for="(pct, label, i) in ratingStarsArray" :key="i">
            <span class="label">{{ label }}</span>
            <div class="bar"><div class="fill" :style="{ width: Math.max(4, Number(pct)) + '%' }"></div></div>
            <span class="pct">{{ Number(pct).toFixed(1) }}%</span>
          </li>
        </ul>
      </div>

      <div v-if="data.summary" class="summary">
        <h4>剧情简介</h4>
        <p>{{ data.summary }}</p>
      </div>

      <div v-if="data.detail_url" class="muted">
        豆瓣详情: <a :href="data.detail_url" target="_blank" rel="noopener">{{ data.detail_url }}</a>
      </div>

      <div v-if="relatedPics.length" class="pics-box">
        <h4>相关图片</h4>
        <div class="pics-grid">
          <img v-for="(src, i) in relatedPics" :key="i" :src="imgSrc(src)" alt="剧照" referrerpolicy="no-referrer" loading="lazy" @error="onImgError($event)">
        </div>
      </div>

      <!-- 相关推荐 -->
          </div>
<div v-else class="muted">加载中...</div>

  <!-- 整卡片之外的:相关推荐 + 上下部 -->
  <div v-if="related.length" class="related-box">
        <h4>相关推荐</h4>
        <div class="related-grid">
          <router-link
            v-for="r in related"
            :key="r.douban_id"
            :to="`/movie/${r.douban_id}`"
            class="related-card"
          >
            <img
              v-if="r.poster_url"
              :src="imgSrc(r.poster_url)"
              :alt="r.title"
              referrerpolicy="no-referrer"
              loading="lazy"
              @error="onImgError($event)"
            />
            <div class="related-info">
              <div class="related-title">{{ r.title }}</div>
              <div class="related-meta">
                <span>{{ r.year || '-' }}</span>
                <span class="related-rating">{{ r.rating?.toFixed?.(1) ?? '-' }}</span>
              </div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- 上下部导航 -->
      <div v-if="neighbors.prev || neighbors.next" class="neighbors">
        <router-link
          v-if="neighbors.prev"
          :to="`/movie/${neighbors.prev.douban_id}`"
          class="neighbor-link prev"
        >
          ← 上一部:{{ neighbors.prev.title }}
        </router-link>
        <span v-else></span>
        <router-link
          v-if="neighbors.next"
          :to="`/movie/${neighbors.next.douban_id}`"
          class="neighbor-link next"
        >
          下一部:{{ neighbors.next.title }} →
        </router-link>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import { useMoviesStore } from '../stores/movies'

const data = ref(null)
const related = ref([])
const neighbors = ref({})
const route = useRoute()
const moviesStore = useMoviesStore()

const relatedPics = computed(() => {
  if (!data.value?.related_pics) return []
  try {
    const raw = data.value.related_pics
    if (Array.isArray(raw)) return raw
    if (typeof raw === 'string') {
      const parsed = JSON.parse(raw)
      return Array.isArray(parsed) ? parsed : []
    }
  } catch (e) {}
  return []
})

// rating_stars 兼容 dict 或 "5星:85.0,4星:10.0,..." 字符串
const ratingStarsArray = computed(() => {
  const raw = data.value?.rating_stars
  if (!raw) return []
  if (typeof raw === 'object') return raw
  if (typeof raw === 'string') {
    try {
      if (raw.startsWith('{')) return JSON.parse(raw)
      const obj = {}
      raw.split(',').forEach(part => {
        const [k, v] = part.split(':').map(s => s.trim())
        if (k && v) obj[k] = Number(v)
      })
      return obj
    } catch (e) { return [] }
  }
  return []
})

onMounted(async () => {
  data.value = (await api.detail(route.params.id)).data
  // 异步加载相关推荐 & 上下部,不阻塞主内容
  related.value = await moviesStore.fetchRelated(route.params.id, 12)
  neighbors.value = await moviesStore.fetchNeighbors(route.params.id)
})

// 图片兜底:豆瓣图床有防盗链,直接访问可能 403。
// 1) 强制走 no-referrer(模板已加)
// 2) 若失败回退到本地代理(/img-proxy?url=...),nginx 会代理到 doubanio.com
const IMG_PROXY = '/img-proxy?url='

function imgSrc(url) {
  if (!url) return ''
  // 已经是相对路径或代理路径就不动
  if (url.startsWith('/')) return url
  // 豆瓣图床走代理
  if (/doubanio\.com|douban\.com/i.test(url)) return IMG_PROXY + encodeURIComponent(url)
  return url
}

function onImgError(e) {
  const el = e.target
  if (!el || el.dataset.fallback) return
  el.dataset.fallback = '1'
  const original = el.getAttribute('src') || ''
  if (original.includes(IMG_PROXY)) return // 已经是代理,不再回退
  // 把当前 src 解析成原始 url 再走代理
  const m = original.match(/[?&]url=([^&]+)/)
  const raw = m ? decodeURIComponent(m[1]) : original
  el.src = IMG_PROXY + encodeURIComponent(raw)
}
</script>

<style scoped>
.movie-head { display: flex; gap: 16px; }
.poster { width: 140px; height: auto; border-radius: 6px; object-fit: cover; }
.info { flex: 1; }
.rating-box { margin: 6px 0; }
.rating { font-size: 28px; color: var(--primary); font-weight: bold; }
.quote { color: #c3ccd6; font-style: italic; margin-top: 6px; }
.divider { height: 1px; background: #1f2937; margin: 14px 0; }
.grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 8px; }
.summary { margin-top: 14px; }
.summary h4 { margin-bottom: 6px; }
.summary p { line-height: 1.7; color: #cbd5e1; }
.stars-box { margin-top: 12px; }
.stars-list { list-style: none; padding: 0; margin-top: 6px; }
.stars-list li { display: flex; align-items: center; gap: 8px; font-size: 13px; margin: 4px 0; }
.stars-list .label { width: 40px; color: #cbd5e1; }
.stars-list .bar { flex: 1; background: #1f2937; height: 8px; border-radius: 4px; overflow: hidden; }
.stars-list .fill { background: var(--primary); height: 100%; }
.stars-list .pct { width: 48px; text-align: right; color: #cbd5e1; }
.pics-box { margin-top: 16px; }
.pics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; margin-top: 8px; }
.pics-grid img { width: 100%; height: 100px; object-fit: cover; border-radius: 6px; background: #1f2937; }
img { background-color: #1f2937; }
img[data-fallback='1'] { opacity: 0.6; }

.related-box { margin-top: 16px; }
.related-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px; margin-top: 8px;
}
.related-card {
  background: #0b1220; border: 1px solid #1f2937; border-radius: 6px;
  overflow: hidden; text-decoration: none; color: var(--text);
  transition: transform 0.15s, border-color 0.15s;
}
.related-card:hover { transform: translateY(-2px); border-color: var(--primary); }
.related-card img { width: 100%; height: 160px; object-fit: cover; display: block; background: #1f2937; }
.related-info { padding: 8px; }
.related-title { font-size: 13px; font-weight: 500; line-height: 1.3; }
.related-meta { display: flex; justify-content: space-between; font-size: 11px; color: var(--muted); margin-top: 4px; }
.related-rating { color: var(--primary); font-weight: bold; }

.neighbors {
  display: flex; justify-content: space-between;
  margin-top: 16px; padding: 10px 14px;
  background: #0b1220; border: 1px solid #1f2937; border-radius: 6px;
}
.neighbor-link { color: var(--primary); font-size: 13px; max-width: 45%; }
.neighbor-link.prev { text-align: left; }
.neighbor-link.next { text-align: right; margin-left: auto; }
.neighbor-link:hover { text-decoration: underline; }</style>



