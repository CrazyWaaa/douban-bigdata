<template>
  <div>
    <div class="header">
      <h2>搜索</h2>
      <div class="muted" v-if="store.q">
        关键词: <b>{{ store.q }}</b>
        <span v-if="!store.loading"> · 命中 {{ store.results.length }} 条</span>
      </div>
    </div>

    <div class="search-bar card">
      <input
        v-model="kw"
        @keyup.enter="run"
        placeholder="输入片名 / 导演 / 演员,回车搜索"
        autofocus
      />
      <button class="btn" @click="run">搜索</button>
      <button class="btn ghost" @click="clear">清空</button>
    </div>

    <div v-if="store.loading" class="muted">搜索中…</div>
    <div v-else-if="store.error" class="error-banner">{{ store.error }}</div>
    <div v-else-if="!store.q" class="muted">输入关键词开始搜索</div>
    <div v-else-if="!store.results.length" class="muted">没有匹配的影片</div>
    <div v-else class="results">
      <router-link
        v-for="m in store.results"
        :key="m.douban_id"
        :to="`/movie/${m.douban_id}`"
        class="result-card"
      >
        <img
          v-if="m.poster_url"
          :src="imgSrc(m.poster_url)"
          :alt="m.title"
          referrerpolicy="no-referrer"
          loading="lazy"
          @error="onImgError($event)"
        />
        <div class="result-info">
          <div class="result-title">{{ m.title }}</div>
          <div class="result-meta">
            <span v-if="m.year">{{ m.year }}</span>
            <span v-if="m.director"> · {{ m.director }}</span>
            <span v-if="m.actors"> · {{ m.actors.split('/')[0] }}</span>
          </div>
          <div class="result-rating">
            <span class="rating">{{ m.rating?.toFixed?.(1) ?? '-' }}</span>
            <span class="muted" v-if="m.rating_count">{{ formatCount(m.rating_count) }} 人评价</span>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSearchStore } from '../stores/search'

const store = useSearchStore()
const route = useRoute()
const router = useRouter()
const kw = ref('')

function formatCount(n) {
  if (n == null) return '-'
  if (n >= 10000) return (n / 10000).toFixed(1) + ' 万'
  return n.toLocaleString()
}

// 图片兜底(同 Movie.vue)
const IMG_PROXY = '/img-proxy?url='
function imgSrc(url) {
  if (!url) return ''
  if (url.startsWith('/')) return url
  if (/doubanio\.com|douban\.com/i.test(url)) return IMG_PROXY + encodeURIComponent(url)
  return url
}
function onImgError(e) {
  const el = e.target
  if (!el || el.dataset.fallback) return
  el.dataset.fallback = '1'
  const original = el.getAttribute('src') || ''
  if (original.includes(IMG_PROXY)) return
  const m = original.match(/[?&]url=([^&]+)/)
  const raw = m ? decodeURIComponent(m[1]) : original
  el.src = IMG_PROXY + encodeURIComponent(raw)
}

function run() {
  const q = kw.value.trim()
  router.replace({ path: '/search', query: q ? { q } : {} })
}
function clear() {
  kw.value = ''
  store.run('')
  router.replace({ path: '/search' })
}

watch(() => route.query.q, (q) => {
  if (typeof q === 'string' && q) {
    kw.value = q
    store.run(q)
  }
}, { immediate: true })

onMounted(() => {
  const q = route.query.q
  if (typeof q === 'string') {
    kw.value = q
    store.run(q)
  }
})
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }
.search-bar {
  display: flex; gap: 10px; align-items: center; padding: 12px 14px;
  margin-bottom: 16px;
}
.search-bar input {
  flex: 1; background: var(--bg); color: var(--text);
  border: 1px solid #1f2937; border-radius: 4px;
  padding: 8px 12px; font-size: 14px;
}
.search-bar input:focus { outline: none; border-color: var(--primary); }
.btn {
  padding: 8px 16px; border-radius: 4px; border: 1px solid var(--primary);
  background: var(--primary); color: #0f172a; cursor: pointer; font-weight: 500;
}
.btn.ghost { background: transparent; color: var(--text); border-color: #1f2937; }
.error-banner {
  padding: 10px 14px; border-radius: 6px;
  background: #7f1d1d33; color: #fca5a5; border: 1px solid #b91c1c;
}
.results {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px;
}
.result-card {
  display: flex; gap: 10px;
  background: var(--surface); border: 1px solid #1f2937; border-radius: 6px;
  padding: 10px; text-decoration: none; color: var(--text);
  transition: transform 0.15s, border-color 0.15s;
}
.result-card:hover { transform: translateY(-2px); border-color: var(--primary); }
.result-card img {
  width: 70px; height: 100px; object-fit: cover; border-radius: 4px;
  flex-shrink: 0; background: #1f2937;
}
.result-info { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: space-between; }
.result-title { font-weight: 500; font-size: 14px; line-height: 1.3; }
.result-meta { font-size: 11px; color: var(--muted); margin-top: 4px; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; }
.result-rating { font-size: 12px; margin-top: 6px; }
.result-rating .rating { color: var(--primary); font-weight: bold; font-size: 16px; margin-right: 6px; }
</style>