<template>
  <div class="search-page">
    <header class="page-head fade-up">
      <div>
        <h1 class="page-title">搜索</h1>
        <p class="page-sub" v-if="store.q">关键词 <b style="color: var(--c-primary)">{{ store.q }}</b> · 命中 {{ store.results.length }} 部</p>
      </div>
    </header>

    <UiCard class="fade-up search-bar" style="animation-delay: 60ms">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="color: var(--c-muted)">
        <circle cx="11" cy="11" r="7"/>
        <path d="M21 21l-4.3-4.3"/>
      </svg>
      <input
        v-model="kw"
        @keyup.enter="run"
        placeholder="输入片名 / 导演 / 演员,回车搜索"
        autofocus
      />
      <UiButton size="sm" @click="run">搜索</UiButton>
      <UiButton size="sm" variant="ghost" @click="clear">清空</UiButton>
    </UiCard>

    <div v-if="store.loading" class="search-grid">
      <div v-for="i in 8" :key="i" class="search-card search-card--skel fade-up" :style="{ animationDelay: (i*30) + 'ms' }">
        <div class="search-card__poster skel-block"></div>
        <div class="search-card__info">
          <div class="skel-line" style="width: 70%"></div>
          <div class="skel-line" style="width: 40%; margin-top: 8px"></div>
          <div class="skel-line" style="width: 30%; margin-top: 12px"></div>
        </div>
      </div>
    </div>
    <div v-else-if="store.error" class="error-banner fade-up">{{ store.error }}</div>
    <div v-else-if="!store.q" class="fade-up"><UiEmptyState title="输入关键词开始搜索" desc="试试「霸王别姬」「诺兰」「宫崎骏」" /></div>
    <div v-else-if="!store.results.length" class="fade-up"><UiEmptyState title="没有匹配的影片" desc="换个关键词试试" /></div>
    <div v-else class="search-grid">
      <router-link
        v-for="(m, i) in store.results"
        :key="m.douban_id"
        :to="`/movie/${m.douban_id}`"
        class="search-card fade-up"
        :style="{ animationDelay: (i*30) + 'ms' }"
      >
        <img
          v-if="m.poster_url"
          :src="imgSrc(m.poster_url)"
          :alt="m.title"
          referrerpolicy="no-referrer"
          loading="lazy"
          class="search-card__poster"
          @error="onImgError"
        />
        <div v-else class="search-card__poster search-card__poster--ph">NO IMAGE</div>
        <div class="search-card__info">
          <div class="search-card__title" v-html="highlight(m.title)"></div>
          <div class="search-card__meta">
            <span v-if="m.year">{{ m.year }}</span>
            <span v-if="m.director"> · <span v-html="highlight(m.director)"></span></span>
            <span v-if="m.actors"> · <span v-html="highlight(m.actors.split('/')[0])"></span></span>
          </div>
          <div class="search-card__rating">
            <span class="search-card__score">{{ m.rating?.toFixed?.(1) ?? '-' }}</span>
            <span class="muted" v-if="m.rating_count">{{ formatCount(m.rating_count) }} 人评价</span>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useSearchStore } from '../stores/search';
import UiCard from '../components/ui/UiCard.vue';
import UiButton from '../components/ui/UiButton.vue';
import UiEmptyState from '../components/ui/UiEmptyState.vue';

const store = useSearchStore();
const route = useRoute();
const router = useRouter();
const kw = ref('');

function formatCount(n) {
  if (n == null) return '-';
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w';
  return n.toLocaleString();
}

const IMG_PROXY = '/img-proxy?url=';
function imgSrc(url) {
  if (!url) return '';
  if (url.startsWith('/')) return url;
  if (/doubanio\.com|douban\.com/i.test(url)) return IMG_PROXY + encodeURIComponent(url);
  return url;
}
function onImgError(e) {
  const el = e.target;
  if (!el || el.dataset.fallback) return;
  el.dataset.fallback = '1';
  const original = el.getAttribute('src') || '';
  if (original.includes(IMG_PROXY)) return;
  const m = original.match(/[?&]url=([^&]+)/);
  const raw = m ? decodeURIComponent(m[1]) : original;
  el.src = IMG_PROXY + encodeURIComponent(raw);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
}
function highlight(text) {
  if (!text || !store.q) return escapeHtml(text);
  const safe = escapeHtml(text);
  const q = escapeHtml(store.q).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return safe.replace(new RegExp(q, 'gi'), m => `<mark>${m}</mark>`);
}

function run() {
  const q = kw.value.trim();
  router.replace({ path: '/search', query: q ? { q } : {} });
}
function clear() {
  kw.value = '';
  store.run('');
  router.replace({ path: '/search' });
}

watch(() => route.query.q, (q) => {
  if (typeof q === 'string' && q) { kw.value = q; store.run(q); }
}, { immediate: true });
onMounted(() => { if (route.query.q) { kw.value = String(route.query.q); store.run(String(route.query.q)); } });
</script>

<style scoped>
.search-page { display: flex; flex-direction: column; gap: 16px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px; }
.page-title { margin: 0; font-size: var(--fs-2xl); font-weight: 700; }
.page-sub { margin: 4px 0 0; color: var(--c-muted); font-size: var(--fs-sm); }

.search-bar { display: flex; align-items: center; gap: 10px; padding: 12px 16px; }
.search-bar input {
  flex: 1; background: var(--c-bg); color: var(--c-text);
  border: 1px solid var(--c-border); border-radius: var(--r-sm);
  padding: 8px 12px; font-size: var(--fs-md);
  transition: border-color var(--t-fast) var(--ease-out);
}
.search-bar input:focus { outline: none; border-color: var(--c-primary); }

.error-banner {
  padding: 10px 14px; border-radius: var(--r);
  background: color-mix(in srgb, var(--c-danger) 14%, transparent);
  color: var(--c-danger);
  border: 1px solid color-mix(in srgb, var(--c-danger) 30%, transparent);
}

.search-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px;
}
.search-card {
  display: flex; gap: 12px;
  background: var(--c-surface); border: 1px solid var(--c-border);
  border-radius: var(--r); padding: 12px;
  text-decoration: none; color: var(--c-text);
  transition: transform var(--t) var(--ease-out), border-color var(--t) var(--ease-out), box-shadow var(--t) var(--ease-out);
}
.search-card:hover { transform: translateY(-2px); border-color: var(--c-primary); box-shadow: var(--shadow); }
.search-card__poster {
  width: 70px; height: 100px; object-fit: cover;
  border-radius: 6px; flex-shrink: 0; background: var(--c-surface-2);
}
.search-card__poster--ph { display: flex; align-items: center; justify-content: center; font-size: 32px; }
.search-card__info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.search-card__title { font-weight: 600; font-size: var(--fs-md); line-height: 1.3; color: var(--c-text); }
.search-card__meta { font-size: var(--fs-xs); color: var(--c-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.search-card__rating { margin-top: auto; display: flex; align-items: baseline; gap: 6px; }
.search-card__score { color: var(--c-primary); font-weight: 700; font-size: var(--fs-xl); }
.search-card :deep(mark) { background: color-mix(in srgb, var(--c-warning) 35%, transparent); color: var(--c-text); border-radius: 3px; padding: 0 2px; }

.skel-block { background: linear-gradient(90deg, var(--c-surface-2) 0%, var(--c-border) 50%, var(--c-surface-2) 100%); background-size: 200% 100%; animation: shimmer 1.4s linear infinite; }
.skel-line { height: 12px; border-radius: 4px; background: linear-gradient(90deg, var(--c-surface-2) 0%, var(--c-border) 50%, var(--c-surface-2) 100%); background-size: 200% 100%; animation: shimmer 1.4s linear infinite; }
</style>