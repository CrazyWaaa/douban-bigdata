<template>
  <div class="search">
    <header class="search__head fade-up">
      <div>
        <h1 class="search__title">搜影片</h1>
        <p class="search__sub">在 250 部里找你的下一部高分片</p>
      </div>
      <span v-if="store.q" class="muted">关键词：<strong class="search__kw">{{ store.q }}</strong></span>
    </header>

    <div class="search__bar fade-up-stagger" style="--i: 1">
      <span class="search__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="7"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
      </span>
      <input
        ref="inputRef"
        v-model="kw"
        type="search"
        placeholder="输入片名 / 导演 / 演员 / 类型,如 肖申克、诺兰、科幻"
        autocomplete="off"
        spellcheck="false"
        @keydown.enter="run"
      />
      <UiButton v-if="kw" size="sm" variant="ghost" @click="clear">清空</UiButton>
      <UiButton size="sm" :loading="store.loading" @click="run">搜索</UiButton>
    </div>

    <div v-if="store.error" class="search__error fade-up" role="alert">
      <span>加载失败:{{ store.error }}</span>
      <UiButton size="sm" variant="outline" @click="retry">重试</UiButton>
    </div>

    <section v-else-if="!store.q" class="search__hint fade-up" aria-label="搜索提示">
      <div class="search__hint-card">
        <h3>热门关键词</h3>
        <div class="search__chips">
          <button v-for="(w, i) in HOT_WORDS" :key="w" class="search__chip" :style="{ animationDelay: (i * 60) + 'ms' }" @click="useWord(w)">{{ w }}</button>
        </div>
      </div>
      <div class="search__hint-card">
        <h3>检索字段说明</h3>
        <ul class="search__doc">
          <li><b>片名</b>：完全 / 部分匹配,支持中英文</li>
          <li><b>导演 / 演员</b>：来自详情页 enrich 的字段</li>
          <li><b>类型 / 国家</b>：点击榜单页对应区块即可</li>
          <li><b>说明</b>：搜索结果来自 MySQL LIKE,不分大小写</li>
        </ul>
      </div>
    </section>

    <section v-else class="search__results fade-up">
      <div class="search__meta">
        <span class="muted">{{ store.results.length }} 条结果</span>
        <span class="muted">耗时 {{ store.took }} ms</span>
      </div>

      <div v-if="store.loading" class="search__list">
        <div v-for="i in 4" :key="i" class="search__skel">
          <div class="search__skel-poster" />
          <div class="search__skel-line" style="width: 70%" />
          <div class="search__skel-line" style="width: 50%; height: 10px;" />
        </div>
      </div>

      <UiEmptyState
        v-else-if="store.results.length === 0"
        title="没有匹配的影片"
        desc="试试更短或不同关键词"
      />

      <ul v-else class="search__list">
        <li
          v-for="(m, i) in store.results"
          :key="m.douban_id"
          class="search__item fade-up"
          :style="{ animationDelay: (i * 40) + 'ms' }"
          @click="open(m)"
        >
          <PosterImg class="search__poster" :src="m.poster_url" :alt="m.title" />
          <div class="search__info">
            <div class="search__row">
              <router-link :to="`/movie/${m.douban_id}`" class="search__name" v-html="highlight(m.title)" />
              <span class="search__year">{{ m.year || '—' }}</span>
            </div>
            <div class="search__director" v-if="m.director"><span class="muted">导演</span><span v-html="highlight(m.director)" /></div>
            <div class="search__actors" v-if="m.actors"><span class="muted">主演</span><span v-html="highlight(m.actors)" /></div>
            <div class="search__tags">
              <span v-if="m.country" class="search__tag">{{ firstCountry(m.country) }}</span>
              <span v-if="m.genre" class="search__tag">{{ firstGenre(m.genre) }}</span>
              <span v-if="m.rating_count" class="search__tag search__tag--soft">{{ formatRatingCount(m.rating_count) }} 人评</span>
            </div>
          </div>
          <div class="search__score">
            <div class="search__score-num">{{ formatRating(m.rating) }}</div>
            <div class="search__score-lbl muted">豆瓣评分</div>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
/**
 * Search.vue - 重写版
 * - 标题 + 搜索栏 + 热门词/说明卡 + 结果列表(海报卡)
 * - 数据走 stores/search.js;关键词变更 -> router.replace 同步 URL
 * - 整卡空态/错误/骨架全部覆盖
 */
import { onMounted, ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UiButton from '../components/ui/UiButton.vue'
import UiEmptyState from '../components/ui/UiEmptyState.vue'
import PosterImg from '../components/common/PosterImg.vue'
import { useSearchStore } from '../stores/search'
import {
  formatRating,
  formatRatingCount,
  splitCountries,
  splitMulti,
} from '../utils/format'

const store = useSearchStore()
const route = useRoute()
const router = useRouter()
const inputRef = ref(null)
const kw = ref('')

const HOT_WORDS = ['肖申克的救赎', '诺兰', '宫崎骏', '周星驰', '科幻', '爱情', '张艺谋']

function run() {
  const q = kw.value.trim()
  store.run(q)
  router.replace({ path: '/search', query: q ? { q } : {} })
}

function clear() {
  kw.value = ''
  store.run('')
  router.replace({ path: '/search' })
  nextTick(() => inputRef.value?.focus())
}

function useWord(w) {
  kw.value = w
  run()
}

function retry() {
  if (store.q) store.run(store.q)
}

function open(m) {
  router.push(`/movie/${encodeURIComponent(m.douban_id)}`)
}

function highlight(text) {
  if (!text || !store.q) return escapeHtml(text)
  const safe = escapeHtml(text)
  const q = escapeHtml(store.q).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return safe.replace(new RegExp(q, 'gi'), (match) => `<mark>${match}</mark>`)
}
function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}
function firstCountry(raw) {
  const arr = splitCountries(raw)
  return arr[0] || ''
}
function firstGenre(raw) {
  const arr = splitMulti(raw)
  return arr[0] || ''
}

watch(() => route.query.q, (q) => {
  if (typeof q === 'string' && q) {
    kw.value = q
    store.run(q)
  }
}, { immediate: true })

onMounted(() => {
  if (route.query.q) kw.value = String(route.query.q)
  inputRef.value?.focus()
})
</script>

<style scoped>
.search { display: flex; flex-direction: column; gap: 14px; }

.search__head {
  display: flex; justify-content: space-between; align-items: flex-end;
  flex-wrap: wrap; gap: 12px;
}
.search__title { margin: 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }
.search__sub { margin: 6px 0 0; color: var(--c-muted); font-size: 14px; }
.search__kw { color: var(--c-primary); font-weight: 600; }

.search__bar {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  transition: all var(--t-fast) var(--ease-out);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.search__bar:focus-within { 
  border-color: var(--c-primary); 
  box-shadow: 0 0 0 3px var(--c-primary-tint), 0 4px 16px rgba(56, 189, 248, 0.2);
}
.search__icon { color: var(--c-muted); display: inline-flex; flex-shrink: 0; }
.search__bar input {
  flex: 1; min-width: 0;
  background: transparent; color: var(--c-text);
  border: 0; outline: none;
  padding: 0; font-size: 16px;
}
.search__bar input::placeholder { color: var(--c-muted); }

/* 提示卡 */
.search__hint {
  display: grid; gap: 12px;
  grid-template-columns: 1.3fr 1fr;
}
@media (max-width: 800px) {
  .search__hint { grid-template-columns: 1fr; }
}
.search__hint-card {
  background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r);
  padding: 20px 22px;
  transition: border-color var(--t-fast) var(--ease-out);
}
.search__hint-card:hover { border-color: var(--c-primary-deep); }
.search__hint-card h3 { margin: 0 0 12px; font-size: 13px; color: var(--c-text-soft); letter-spacing: 1.5px; text-transform: uppercase; font-weight: 600; }
.search__chips { display: flex; flex-wrap: wrap; gap: 8px; }
.search__chip {
  border: 1px solid var(--c-border); background: var(--c-surface-2);
  color: var(--c-text-soft); padding: 7px 14px;
  border-radius: 999px; font-size: 13px; cursor: pointer;
  transition: all var(--t-fast) var(--ease-out);
  opacity: 0; transform: translateY(4px);
  animation: fadeUp .4s var(--ease-out) both;
}
.search__chip:hover { 
  background: var(--c-primary-tint); 
  border-color: var(--c-primary); 
  color: var(--c-primary);
  transform: translateY(-1px);
}

.search__doc { margin: 0; padding-left: 20px; color: var(--c-muted); }
.search__doc li { padding: 5px 0; font-size: 13px; }
.search__doc b { color: var(--c-text); }

/* 结果 */
.search__meta {
  display: flex; justify-content: space-between;
  font-size: var(--fs-sm); color: var(--c-muted);
  padding: 6px 2px;
}
.search__list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.search__item {
  display: grid;
  grid-template-columns: 90px 1fr auto;
  gap: 16px; align-items: flex-start;
  padding: 14px 16px;
  background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r);
  cursor: pointer;
  transition: all var(--t-fast) var(--ease-out);
  opacity: 0; transform: translateY(6px);
  animation: fadeUp .35s var(--ease-out) both;
}
.search__item:hover { 
  transform: translateY(-2px); 
  border-color: var(--c-primary); 
  box-shadow: var(--shadow); 
}
.search__poster { width: 90px; border-radius: 8px; overflow: hidden; flex-shrink: 0; }
.search__info { min-width: 0; display: flex; flex-direction: column; gap: 5px; }
.search__row { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.search__name { font-size: 17px; font-weight: 700; color: var(--c-text); }
.search__name:hover { color: var(--c-primary); }
.search__year { font-size: var(--fs-sm); color: var(--c-muted); }
.search__director, .search__actors {
  font-size: 13px; color: var(--c-text-soft);
  display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical;
  overflow: hidden; text-overflow: ellipsis;
}
.search__director .muted, .search__actors .muted { color: var(--c-muted); margin-right: 8px; }
.search__tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.search__tag {
  font-size: 12px;
  background: var(--c-surface-2); color: var(--c-text-soft);
  padding: 3px 10px; border-radius: 999px; border: 1px solid var(--c-border);
  transition: all var(--t-fast) var(--ease-out);
}
.search__tag:hover { background: var(--c-primary-tint); border-color: var(--c-primary); color: var(--c-primary); }
.search__tag--soft { background: transparent; color: var(--c-muted); }

.search__score { text-align: right; min-width: 90px; flex-shrink: 0; }
.search__score-num { font-size: 26px; font-weight: 700; color: var(--c-warning); font-variant-numeric: tabular-nums; }
.search__score-lbl { font-size: 11px; color: var(--c-muted); }

.search__error {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; border-radius: var(--r);
  background: color-mix(in srgb, var(--c-danger) 14%, transparent);
  border: 1px solid color-mix(in srgb, var(--c-danger) 50%, transparent);
}

/* 骨架 */
.search__skel {
  display: grid; grid-template-columns: 90px 1fr; gap: 14px;
  padding: 14px; background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r);
}
.search__skel-poster {
  width: 90px; aspect-ratio: 2/3; border-radius: 8px;
  background: linear-gradient(90deg, var(--c-surface-2) 0%, var(--c-border) 50%, var(--c-surface-2) 100%);
  background-size: 200% 100%; animation: shimmer 1.4s linear infinite;
}
.search__skel-line {
  height: 16px; border-radius: 4px; margin: 8px 0;
  background: linear-gradient(90deg, var(--c-surface-2) 0%, var(--c-border) 50%, var(--c-surface-2) 100%);
  background-size: 200% 100%; animation: shimmer 1.4s linear infinite;
}
.search__skel-line:first-child { margin-top: 16px; }

:deep(mark) {
  background: color-mix(in srgb, var(--c-warning) 35%, transparent);
  color: var(--c-text);
  border-radius: 3px;
  padding: 0 3px;
}
</style>