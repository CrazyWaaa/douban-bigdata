<template>
  <div>
    <h2>影片详情</h2>
    <div v-if="data" class="card">
      <div class="movie-head">
        <img v-if="data.poster_url" :src="data.poster_url" class="poster" alt="封面">
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
          <img v-for="(src, i) in relatedPics" :key="i" :src="src" alt="剧照">
        </div>
      </div>
    </div>
    <div v-else class="muted">加载中...</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'

const data = ref(null)
const route = useRoute()

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
})
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
.pics-grid img { width: 100%; height: 100px; object-fit: cover; border-radius: 6px; }
</style>
