<template>
  <transition name="movie" mode="out-in">
    <div v-if="loading" key="loading" class="movie-loading fade-up" aria-live="polite" aria-busy="true">
      <div class="movie-loading__inner">
        <span class="movie-loading__spinner" aria-hidden="true"></span>
        <span class="movie-loading__text">正在载入影片…</span>
      </div>
    </div>

    <UiEmptyState v-else-if="error" key="error" :title="error" />

    <div v-else-if="data" key="data" class="movie-page">
      <section class="hero">
      <div class="hero__bg" :style="heroBgStyle"></div>
      <div class="hero__overlay"></div>
      <div class="hero__inner fade-up">
        <div class="hero__main">
          <img
            v-if="data.poster_url"
            :src="imgSrc(data.poster_url)"
            :alt="data.title"
            referrerpolicy="no-referrer"
            class="hero__poster"
            @error="onImgError"
          />
          <div class="hero__info">
            <h1 class="hero__title">{{ data.title || '-' }}
              <span v-if="data.year" class="hero__year">({{ data.year || '-' }})</span>
            </h1>
            <div class="hero__meta">
              <span v-if="data.director">{{ data.director.split('/')[0] }} 导演</span>
              <span v-for="(g, gi) in (data.genre || '').split('/').slice(0, 3).filter(x => x.trim())" :key="gi" class="hero__tag">{{ g.trim() }}</span>
              <span v-if="data.country">{{ data.country.split('/')[0] }}</span>
            </div>
            <div v-if="data.quote" class="hero__quote">"{{ data.quote || '-' }}"</div>
          </div>
          <div class="hero__rating" v-if="data.rating">
            <svg width="120" height="120" viewBox="0 0 120 120" class="rating-ring">
              <circle cx="60" cy="60" r="52" fill="none" stroke="var(--c-border)" stroke-width="8"/>
              <circle cx="60" cy="60" r="52" fill="none" stroke="var(--c-primary)" stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="`${(data.rating / 10) * 327} 327`"
                transform="rotate(-90 60 60)"
                class="rating-ring__bar"/>
              <text x="60" y="68" text-anchor="middle" font-size="32" font-weight="700" fill="var(--c-primary)">{{ data.rating.toFixed(1) }}</text>
            </svg>
            <div class="hero__rating-meta">
              <div class="muted" style="font-size: var(--fs-xs);">满分 10</div>
              <div class="muted" v-if="data.rating_count">{{ formatCount(data.rating_count) }} 人评价</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="content">
      <div class="content__grid">
        <div class="content__main">
          <UiCard title="剧情简介" class="fade-up-stagger" style="--i: 1">
            <p v-if="data.summary" class="summary">{{ data.summary || '-' }}</p>
            <UiEmptyState v-else title="暂无简介" />
          </UiCard>

          <UiCard title="演职员" class="fade-up-stagger" style="--i: 2">
            <div class="staff">
              <div class="staff__row">
                <span class="staff__label">导演</span>
                <span class="staff__val">{{ data.director || '-' }}</span>
              </div>
              <div class="staff__row">
                <span class="staff__label">主演</span>
                <span class="staff__val">{{ data.actors || '-' }}</span>
              </div>
              <div class="staff__row" v-if="data.languages">
                <span class="staff__label">语言</span>
                <span class="staff__val">{{ data.languages || '-' }}</span>
              </div>
              <div class="staff__row" v-if="data.runtime || data.runtime_minutes">
                <span class="staff__label">片长</span>
                <span class="staff__val">{{ data.runtime_minutes ? data.runtime_minutes + ' 分钟' : data.runtime }}</span>
              </div>
              <div class="staff__row" v-if="data.release_date">
                <span class="staff__label">上映</span>
                <span class="staff__val">{{ data.release_date || '-' }}</span>
              </div>
            </div>
          </UiCard>

          <UiCard v-if="ratingStarsArray && ratingStarsArray.length" title="评分构成" class="fade-up-stagger" style="--i: 3">
            <ul class="stars-list">
              <li v-for="(s, idx) in ratingStarsArray" :key="idx">
                <span class="stars-list__label">{{ idx + 1 }} 星</span>
                <div class="stars-list__bar">
                  <div class="stars-list__fill" :style="{ width: s + '%' }"></div>
                </div>
                <span class="stars-list__pct">{{ s || '-' }}%</span>
              </li>
            </ul>
          </UiCard>

          <UiCard v-if="relatedPics && relatedPics.length" title="剧照" class="fade-up-stagger" style="--i: 4">
            <div class="pics-grid">
              <img v-for="(p, i) in relatedPics" :key="i" :src="imgSrc(p)" :alt="'pic-' + i" referrerpolicy="no-referrer" loading="lazy" @error="onImgError" />
            </div>
          </UiCard>
        </div>

        <div class="content__side">
          <UiCard v-if="neighbors.prev || neighbors.next" title="榜单导航" class="fade-up-stagger" style="--i: 1">
            <div class="neighbors">
              <router-link v-if="neighbors.prev" class="neighbor" :to="'/movie/' + neighbors.prev.douban_id">
                <span class="muted">上一部</span>
                <span class="neighbor__title">{{ neighbors.prev.title || '-' }}</span>
              </router-link>
              <router-link v-if="neighbors.next" class="neighbor neighbor--right" :to="'/movie/' + neighbors.next.douban_id">
                <span class="muted">下一部</span>
                <span class="neighbor__title">{{ neighbors.next.title || '-' }}</span>
              </router-link>
            </div>
          </UiCard>

          <UiCard title="相关推荐" class="fade-up-stagger" style="--i: 2">
            <div v-if="related.length" class="related-grid">
              <router-link
                v-for="(m, i) in related"
                :key="m.douban_id"
                :to="'/movie/' + m.douban_id"
                class="related-card"
                :style="{ animationDelay: (i * 40) + 'ms' }"
              >
                <img v-if="m.poster_url" :src="imgSrc(m.poster_url)" :alt="m.title" referrerpolicy="no-referrer" loading="lazy" @error="onImgError" />
                <div v-else class="related-card__ph">NO IMAGE</div>
                <div class="related-card__info">
                  <div class="related-card__title">{{ m.title || '-' }}</div>
                  <div class="related-card__meta">
                    <span class="related-card__rating">{{ m.rating?.toFixed?.(1) ?? '-' }}</span>
                    <span class="muted">{{ m.year || '-' }}</span>
                  </div>
                </div>
              </router-link>
            </div>
            <UiEmptyState v-else title="暂无推荐" />
          </UiCard>
        </div>
      </div>
    </div>
  </div>
  </transition>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useMoviesStore } from '../stores/movies';
import UiCard from '../components/ui/UiCard.vue';
import UiEmptyState from '../components/ui/UiEmptyState.vue';

const route = useRoute();
const moviesStore = useMoviesStore();
const data = ref(null);
const related = ref([]);
const neighbors = ref({});
const error = ref('');
const loading = ref(true);

const ratingStarsArray = computed(() => {
  const raw = data.value?.rating_stars;
  if (!raw) return [];
  if (typeof raw === 'object') return raw;
  if (typeof raw === 'string') {
    try {
      if (raw.startsWith('{')) return JSON.parse(raw);
      const obj = {};
      raw.split(',').forEach(part => {
        const [k, v] = part.split(':').map(s => s.trim());
        if (k && v) obj[k] = Number(v);
      });
      return obj;
    } catch (e) { return []; }
  }
  return [];
});

const relatedPics = computed(() => {
  const raw = data.value?.related_pics;
  if (!raw) return [];
  try {
    if (Array.isArray(raw)) return raw;
    if (typeof raw === 'string') {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    }
  } catch (e) {}
  return [];
});

const heroBgStyle = computed(() => {
  const url = data.value?.poster_url;
  if (!url) return { background: 'linear-gradient(135deg, var(--c-primary-tint), transparent)' };
  return { backgroundImage: `url(${imgSrc(url)})` };
});

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
function formatCount(n) {
  if (n == null) return '-';
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w';
  return n.toLocaleString();
}

async function load(id) {
  loading.value = true;
  error.value = '';
  data.value = null;
  related.value = [];
  neighbors.value = {};
  try {
    const detail = await moviesStore.fetchDetail(id);
    if (!detail) {
      error.value = '未找到该影片';
    } else {
      data.value = detail;
      related.value = await moviesStore.fetchRelated(id, 12);
      neighbors.value = await moviesStore.fetchNeighbors(id);
    }
  } catch (e) {
    error.value = '加载失败: ' + (e?.message || String(e));
  } finally {
    loading.value = false;
  }
}

onMounted(() => load(route.params.id));
watch(() => route.params.id, (newId) => { if (newId) load(newId); });
</script>

<style scoped>
.movie-page { position: relative; }

.hero {
  position: relative; border-radius: var(--r-lg);
  overflow: hidden; margin-bottom: 18px;
  min-height: 280px;
}
.hero__bg {
  position: absolute; inset: 0; background-size: cover; background-position: center;
  filter: blur(30px) saturate(1.2); transform: scale(1.2);
  transition: transform .6s var(--ease-out);
}
.hero:hover .hero__bg { transform: scale(1.1); }
.hero__overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, color-mix(in srgb, var(--c-bg) 60%, transparent) 0%, color-mix(in srgb, var(--c-bg) 90%, transparent) 100%);
}
.hero__inner { position: relative; padding: 32px 24px; }
.hero__main { display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }
.hero__poster {
  width: 160px; height: 220px; object-fit: cover;
  border-radius: var(--r); box-shadow: var(--shadow-lg);
  background: var(--c-surface-2);
  transition: transform var(--t) var(--ease-out);
}
.hero__poster:hover { transform: scale(1.03); }
.hero__info { flex: 1; min-width: 200px; }
.hero__title { margin: 0; font-size: var(--fs-3xl); font-weight: 700; color: var(--c-text); }
.hero__year { color: var(--c-muted); font-weight: 400; font-size: var(--fs-xl); }
.hero__meta { display: flex; flex-wrap: wrap; gap: 10px; margin: 12px 0 0; color: var(--c-text-soft); font-size: var(--fs-sm); }
.hero__tag {
  padding: 2px 10px;
  border: 1px solid var(--c-border);
  border-radius: 999px;
  font-size: var(--fs-xs);
  color: var(--c-text);
  background: var(--c-surface);
}
.hero__quote { color: var(--c-text-soft); font-style: italic; font-size: var(--fs-md); margin-top: 14px; }

.hero__rating { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.rating-ring { display: block; }
.rating-ring__bar { transition: stroke-dasharray 1.2s var(--ease-out); }
.hero__rating-meta { text-align: center; }

.content__grid { display: grid; grid-template-columns: 1fr 360px; gap: 18px; }
.content__main, .content__side { display: flex; flex-direction: column; gap: 14px; }

.summary { margin: 0; line-height: 1.8; color: var(--c-text-soft); }

.staff { display: flex; flex-direction: column; gap: 10px; }
.staff__row { display: flex; gap: 12px; font-size: var(--fs-md); }
.staff__label { width: 60px; color: var(--c-muted); flex-shrink: 0; }
.staff__val { flex: 1; color: var(--c-text-soft); }

.stars-list { list-style: none; padding: 0; margin: 0; }
.stars-list li { display: flex; align-items: center; gap: 10px; margin: 8px 0; font-size: var(--fs-sm); }
.stars-list__label { width: 60px; color: var(--c-text-soft); }
.stars-list__bar { flex: 1; height: 8px; background: var(--c-surface-2); border-radius: 4px; overflow: hidden; }
.stars-list__fill { height: 100%; background: linear-gradient(90deg, var(--c-warning), var(--c-primary)); transition: width 1.2s var(--ease-out); }
.stars-list__pct { width: 44px; text-align: right; color: var(--c-muted); font-variant-numeric: tabular-nums; }

.pics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; }
.pics-grid img { width: 100%; height: 100px; object-fit: cover; border-radius: 6px; background: var(--c-surface-2); transition: transform var(--t) var(--ease-out); }
.pics-grid img:hover { transform: scale(1.04); }

.neighbors { display: flex; gap: 12px; }
.neighbor {
  flex: 1; padding: 10px 12px; border-radius: var(--r-sm);
  background: var(--c-surface-2); cursor: pointer;
  text-decoration: none; display: flex; flex-direction: column; gap: 4px;
  transition: background var(--t-fast) var(--ease-out), border-color var(--t-fast) var(--ease-out);
  border: 1px solid transparent;
}
.neighbor:hover { background: var(--c-primary-tint); border-color: var(--c-primary); }
.neighbor--right { text-align: right; }
.neighbor__title { color: var(--c-text); font-size: var(--fs-sm); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.related-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.related-card {
  background: var(--c-surface-2); border: 1px solid var(--c-border);
  border-radius: var(--r-sm); overflow: hidden;
  text-decoration: none; color: var(--c-text);
  display: flex; flex-direction: column;
  opacity: 0; transform: translateY(4px);
  animation: fadeUp .35s var(--ease-out) both;
  transition: transform var(--t-fast) var(--ease-out), border-color var(--t-fast) var(--ease-out);
}
.related-card:hover { transform: translateY(-2px); border-color: var(--c-primary); }
.related-card img { width: 100%; height: 130px; object-fit: cover; background: var(--c-surface-2); display: block; }
.related-card__ph { height: 130px; display: flex; align-items: center; justify-content: center; font-size: 12px; color: var(--c-muted); letter-spacing: 2px; }
.related-card__info { padding: 8px 10px; }
.related-card__title { font-size: var(--fs-sm); font-weight: 500; line-height: 1.3; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.related-card__meta { display: flex; justify-content: space-between; font-size: 11px; margin-top: 4px; }
.related-card__rating { color: var(--c-primary); font-weight: 700; }

.movie-loading {
  display: flex; align-items: center; justify-content: center;
  min-height: 60vh;
}
.movie-loading__inner {
  display: flex; align-items: center; gap: 12px;
  color: var(--c-muted); font-size: var(--fs-sm);
}
.movie-loading__spinner {
  width: 18px; height: 18px; border-radius: 50%;
  border: 2px solid var(--c-border-strong); border-top-color: var(--c-primary);
  animation: spin .9s linear infinite;
}

/* <transition name="movie">：加载态切换 */
.movie-enter-active { transition: opacity var(--t-page) var(--ease-out), transform var(--t-page) var(--ease-out); }
.movie-leave-active { transition: opacity var(--t-fast) var(--ease-out); }
.movie-enter-from   { opacity: 0; transform: translateY(12px); }
.movie-leave-to     { opacity: 0; }

@media (max-width: 1024px) {
  .content__grid { grid-template-columns: 1fr; }
}
@media (max-width: 600px) {
  .hero__main { flex-direction: column; align-items: flex-start; }
  .hero__poster { width: 120px; height: 170px; }
  .related-grid { grid-template-columns: 1fr 1fr; }
}
</style>
