<template>
  <div class="dashboard">
    <header class="dashboard__head fade-up">
      <div class="dashboard__head-left">
        <h1 class="dashboard__title">
          <span class="dashboard__title-zh">豆瓣电影 TOP250 · 数据透视</span>
          <span class="dashboard__title-en">DOUDBAN · DATA OVERVIEW</span>
        </h1>
        <p class="dashboard__sub">实时聚合 · 多维度对比 · 一屏看懂 250 部高分影片</p>
      </div>
      <div class="dashboard__head-actions">
        <span v-if="lastLoadedLabel" class="muted">{{ lastLoadedLabel }}</span>
        <UiButton size="sm" variant="ghost" :loading="loading" @click="refresh">
          {{ loading ? '刷新中' : '刷新数据' }}
        </UiButton>
      </div>
    </header>

    <KpiBar :autoplay="false" :draggable="false">
      <div v-for="(m, i) in metricCards" :key="m.key" class="kpi-slot fade-up" :style="kpiCellStyle(i)">
        <template v-if="m.raw">
          <div class="ui-metric" :class="m.tone && `ui-metric--${m.tone}`">
            <div class="ui-metric__head">
              <span class="ui-metric__label">{{ m.label || '-' }}</span>
            </div>
            <div class="ui-metric__value">
              <span class="ui-metric__num ui-metric__num--text">{{ m.value || '-' }}</span>
            </div>
            <div v-if="m.sub" class="ui-metric__sub">{{ m.sub || '-' }}</div>
          </div>
        </template>
        <template v-else>
          <UiMetricCard
            :label="m.label"
            :value="m.value"
            :sub="m.sub"
            :unit="m.unit"
            :decimals="m.decimals"
            :tone="m.tone"
          />
        </template>
      </div>
    </KpiBar>

    <div v-if="errorSummary" class="dashboard__error fade-up" role="alert">
      <span>部分数据加载失败：{{ errorSummary }}</span>
      <UiButton size="sm" variant="outline" @click="refresh">重试</UiButton>
    </div>

    <div class="dashboard__grid">
      <section class="dashboard__col dashboard__col--left">
        <UiCard title="高分榜 Top10" glow>
          <template #actions><span class="muted">按豆瓣评分排序</span></template>
          <UiEmptyState v-if="!store.topRated.length" title="暂无榜单数据" />
          <ol v-else class="top-list">
            <li
              v-for="(m, i) in topRated"
              :key="m.douban_id"
              class="top-list__item"
              :style="topItemStyle(i)"
            >
              <span :class="['top-list__rank', topRankTone(i)]">{{ i + 1 }}</span>
              <PosterImg class="top-list__poster" :src="m.poster_url" :alt="m.title" />
              <div class="top-list__info">
                <router-link :to="`/movie/${m.douban_id}`" class="top-list__title">{{ m.title || '-' }}</router-link>
                <div class="top-list__meta">
                  <span>{{ m.year || '—' }}</span>
                  <span v-if="firstCountry(m.country)"> · {{ firstCountry(m.country) }}</span>
                  <span v-if="firstGenre(m.genre)"> · {{ firstGenre(m.genre) }}</span>
                </div>
                <div class="top-list__bar">
                  <KindProgress :label="formatRating(m.rating)" :percent="ratingPercent(m.rating)" :color="ratingTone(m.rating)" />
                </div>
              </div>
              <div class="top-list__tail">
                <div class="top-list__score">{{ formatRating(m.rating) }}</div>
                <div class="top-list__count muted">{{ formatRatingCount(m.rating_count) }} 人</div>
              </div>
            </li>
          </ol>
        </UiCard>
      </section>

      <section class="dashboard__col dashboard__col--mid">
        <UiCard title="类型分布 · 数量与均分">
          <template #actions>
            <span class="muted">片单引用 · 平均分</span>
          </template>
          <UiChartCard v-if="loading && !genreOption" title="类型分布" sub="加载中" :loading="true" />
          <EChart v-else :option="genreOption" height="320px" @item-click="onGenreClick" />
          <div class="dashboard__legend">
            <span class="dashboard__legend-dot" style="background: var(--c-primary)"></span>
            <span class="muted">左轴：片单引用</span>
            <span class="dashboard__legend-dot" style="background: var(--c-warning); margin-left: 12px"></span>
            <span class="muted">右轴：平均分</span>
          </div>
        </UiCard>
      </section>

      <section class="dashboard__col dashboard__col--right">
        <UiCard title="年代趋势 · 近 20 年">
          <template #actions><span class="muted">片数 · 均分</span></template>
          <UiChartCard v-if="loading && !yearOption" title="年代趋势" sub="加载中" :loading="true" />
          <EChart v-else :option="yearOption" height="320px" @item-click="onYearClick" />
        </UiCard>
      </section>
    </div>

    <div class="dashboard__row--3">
      <UiCard title="评分分布">
        <template #actions><span class="muted">整体打分构成</span></template>
        <UiChartCard v-if="loading && !ratingOption" title="评分分布" sub="加载中" :loading="true" />
        <EChart v-else :option="ratingOption" height="280px" />
      </UiCard>

      <UiCard title="国家 Top10">
        <template #actions><span class="muted">出品国家</span></template>
        <UiChartCard v-if="loading && !countryOption" title="国家 Top10" sub="加载中" :loading="true" />
        <EChart v-else :option="countryOption" height="280px" @item-click="onCountryClick" />
      </UiCard>

      <UiCard title="最受关注" glow>
        <template #actions><span class="muted">评价人数之最</span></template>
        <div v-if="topFocus" class="focus">
          <PosterImg class="focus__poster" :src="topFocus.poster" :alt="topFocus.title" />
          <div class="focus__info">
            <div class="focus__title">{{ topFocus.title || '-' }}</div>
            <div class="focus__meta">
              <span>导演：{{ topFocus.director || '—' }}</span>
              <span v-if="topFocus.year">· {{ topFocus.year || '-' }}</span>
            </div>
            <div class="focus__metric">
              <div class="focus__metric-num">{{ formatRatingCount(topFocus.ratingCount) }}</div>
              <div class="focus__metric-lbl muted">评价人数</div>
            </div>
          </div>
        </div>
        <UiEmptyState v-else title="暂无最受关注影片" />
      </UiCard>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'

import UiCard from '../components/ui/UiCard.vue'
import UiButton from '../components/ui/UiButton.vue'
import UiMetricCard from '../components/ui/UiMetricCard.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import UiEmptyState from '../components/ui/UiEmptyState.vue'
import PosterImg from '../components/common/PosterImg.vue'
import KindProgress from '../components/common/KindProgress.vue'
import KpiBar from '../components/dashboard/KpiBar.vue'
import EChart from '../components/EChart.vue'

import {
  buildGenreDualOption,
  buildYearTrendOption,
  buildRatingRingOption,
  buildCountryBarOption,
} from '../echarts/dashboardOptions'

import { useDashboardStore } from '../stores/dashboard'
import {
  formatRating,
  formatRatingCount,
  splitCountries,
  splitMulti,
} from '../utils/format'

const store = useDashboardStore()
const router = useRouter()

const loading = computed(() =>
  store.groupLoading.core
  || store.groupLoading.topRated
  || store.groupLoading.distribution
  || store.groupLoading.secondary
)

const lastLoadedLabel = computed(() => {
  if (!store.lastLoadedAt) return ''
  const d = new Date(store.lastLoadedAt)
  const pad = (n) => String(n).padStart(2, '0')
  return `最近更新 ${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
})

const errorSummary = computed(() => {
  const errs = store.errors || {}
  const keys = Object.keys(errs)
  if (!keys.length) return ''
  return keys.slice(0, 3).map((k) => `${k}: ${errs[k]}`).join('；')
})

const metricCards = computed(() => {
  const ext = store.summaryExt || {}
  const base = store.summary || {}
  return [
    {
      key: 'total', label: '片单收录', value: base.total || 0,
      sub: '豆瓣 TOP250', tone: 'primary', decimals: 0,
    },
    {
      key: 'avg', label: '平均评分', value: Number(ext.avg_rating || 0) || 0,
      sub: `最高 ${formatRating(ext.max_rating)}`, tone: 'warning', decimals: 2,
    },
    {
      key: 'geo', label: '类型 / 国家',
      value: `${base.distinct_genre || 0} / ${base.distinct_country || 0}`,
      sub: `跨度 ${base.distinct_year || 0} 年`, tone: 'success', decimals: 0, raw: true,
    },
    {
      key: 'comments', label: '总评价人数',
      value: Number(ext.avg_rating_count || 0) || 0,
      sub: '累计观众评价', tone: 'info', decimals: 0,
    },
    {
      key: 'top', label: '最受关注',
      value: ext.top_rating_count_title || '—',
      sub: ext.top_rating_count ? `${formatRatingCount(ext.top_rating_count)} 人` : '—',
      tone: 'primary', decimals: 0, raw: true,
    },
  ]
})

function kpiCellStyle(i) { return { animationDelay: `${i * 50}ms` } }

const topRated = computed(() => store.topRated.slice(0, 10))
function topItemStyle(i) { return { animationDelay: `${i * 40}ms` } }
function topRankTone(i) {
  if (i === 0) return 'is-gold'
  if (i === 1) return 'is-silver'
  if (i === 2) return 'is-bronze'
  return ''
}
function firstCountry(raw) {
  const arr = splitCountries(raw)
  return arr[0] || ''
}
function firstGenre(raw) {
  const arr = splitMulti(raw)
  return arr[0] || ''
}
function ratingTone(rating) {
  const n = Number(rating || 0)
  if (n >= 9.2) return '#22c55e'
  if (n >= 8.8) return '#34d399'
  if (n >= 8.4) return '#22d3ee'
  if (n >= 8.0) return '#f59e0b'
  return '#94a3b8'
}
function ratingPercent(rating) {
  const n = Number(rating || 0)
  if (!Number.isFinite(n)) return 0
  return Math.max(0, Math.min(100, (n / 10) * 100))
}

const genreOption = computed(() => buildGenreDualOption(store.validGenres, { limit: 12 }))
const yearOption = computed(() => buildYearTrendOption(store.avgByYear, { limit: 20 }))
const ratingOption = computed(() => buildRatingRingOption(store.ratingDist))
const countryOption = computed(() => buildCountryBarOption(store.countries, { limit: 10 }))

const topFocus = computed(() => {
  const title = store.summaryExt?.top_rating_count_title
  if (!title || !store.topRated.length) return null
  const m = store.topRated.find((x) => x.title === title)
  if (!m) return null
  return {
    title: m.title,
    poster: m.poster_url,
    director: m.director,
    year: m.year,
    ratingCount: store.summaryExt.top_rating_count,
  }
})

function onGenreClick(params) {
  const idx = params?.dataIndex
  if (idx == null) return
  const genre = store.validGenres[idx]
  if (genre?.name) router.push({ path: '/top', query: { genre: genre.name } })
}
function onCountryClick(params) {
  const idx = params?.dataIndex
  if (idx == null) return
  const items = (store.countries || []).slice(0, 10).reverse()
  const item = items[idx]
  if (item?.name) router.push({ path: '/top', query: { country: item.name } })
}
function onYearClick(params) {
  const idx = params?.dataIndex
  if (idx == null) return
  const items = (store.avgByYear || []).slice(0, 20)
  const it = items[idx]
  const year = it?.year ?? it?.name
  if (year) router.push({ path: '/top', query: { yearFrom: year, yearTo: year } })
}

async function refresh() { await store.refresh() }

onMounted(() => { store.loadAll() })
onActivated(() => { if (!store.lastLoadedAt) store.loadAll() })
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 10px; }
.dashboard__head { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px; }
.dashboard__title { margin: 0; font-size: 26px; letter-spacing: -0.5px; display: flex; flex-direction: column; }
.dashboard__title-zh { font-weight: 700; }
.dashboard__title-en { font-size: 11px; letter-spacing: 4px; color: var(--c-muted); margin-top: 4px; }
.dashboard__sub { margin: 6px 0 0; color: var(--c-muted); font-size: var(--fs-sm); }
.dashboard__head-actions { display: flex; gap: 8px; align-items: center; }
.dashboard__error {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  background: color-mix(in srgb, var(--c-danger) 14%, transparent);
  border: 1px solid color-mix(in srgb, var(--c-danger) 50%, transparent);
  border-radius: var(--r);
  color: var(--c-text);
}
.kpi-slot { min-width: 168px; flex-shrink: 0; }

.dashboard__grid {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 6fr) minmax(0, 5fr);
  gap: 10px;
}
.dashboard__col { min-width: 0; }
.dashboard__row--3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
@media (max-width: 1280px) {
  .dashboard__grid { grid-template-columns: 1fr 1fr; }
  .dashboard__col--left { grid-column: 1 / -1; }
}
@media (max-width: 900px) {
  .dashboard__grid, .dashboard__row--3 { grid-template-columns: 1fr; }
}

.top-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
.top-list__item {
  display: grid;
  grid-template-columns: 26px 48px 1fr auto;
  gap: 12px; align-items: center;
  padding: 8px 10px;
  border-radius: var(--r-sm);
  transition: background var(--t-fast) var(--ease-out);
  opacity: 0; transform: translateY(6px);
  animation: fadeUp .4s var(--ease-out) both;
}
.top-list__item:hover { background: var(--c-surface-2); }
.top-list__rank {
  width: 26px; height: 26px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--c-surface-2); color: var(--c-text-soft);
  font-weight: 600; font-size: 12px;
}
.top-list__rank.is-gold   { background: linear-gradient(135deg, #fbbf24, #b45309); color: #1f1500; }
.top-list__rank.is-silver { background: linear-gradient(135deg, #cbd5e1, #475569); color: #0b1020; }
.top-list__rank.is-bronze { background: linear-gradient(135deg, #d97706, #78350f); color: #fff; }
.top-list__poster { width: 48px; border-radius: 6px; overflow: hidden; }
.top-list__info { display: flex; flex-direction: column; min-width: 0; gap: 2px; }
.top-list__title { font-weight: 600; color: var(--c-text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.top-list__title:hover { color: var(--c-primary); }
.top-list__meta { font-size: var(--fs-xs); color: var(--c-muted); }
.top-list__bar { margin-top: 4px; }
.top-list__tail { text-align: right; min-width: 70px; }
.top-list__score { font-size: 18px; font-weight: 700; color: var(--c-primary); font-variant-numeric: tabular-nums; }
.top-list__count { font-size: var(--fs-xs); }

.focus { display: flex; gap: 14px; align-items: center; }
.focus__poster { width: 88px; border-radius: 8px; overflow: hidden; flex-shrink: 0; }
.focus__info { min-width: 0; flex: 1; display: flex; flex-direction: column; gap: 4px; }
.focus__title { font-size: 16px; font-weight: 600; color: var(--c-text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.focus__meta { font-size: var(--fs-xs); color: var(--c-muted); }
.focus__metric { margin-top: 6px; display: flex; flex-direction: column; gap: 2px; }
.focus__metric-num { font-size: 22px; font-weight: 700; color: var(--c-warning); font-variant-numeric: tabular-nums; }
.focus__metric-lbl { font-size: var(--fs-xs); }

.dashboard__legend {
  display: flex; align-items: center; gap: 6px;
  font-size: var(--fs-xs); color: var(--c-muted);
  margin-top: 6px;
}
.dashboard__legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }

/* 在 raw KPI 槽复用 UiMetricCard 视觉 */
.kpi-slot .ui-metric {
  position: relative; overflow: hidden;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r);
  padding: 12px 14px;
  transition: transform var(--t) var(--ease-out), border-color var(--t) var(--ease-out), box-shadow var(--t) var(--ease-out);
}
.kpi-slot .ui-metric:hover { transform: translateY(-2px); border-color: var(--c-primary); box-shadow: var(--shadow); }
.kpi-slot .ui-metric__head { display: flex; align-items: center; justify-content: space-between; }
.kpi-slot .ui-metric__label { color: var(--c-muted); font-size: var(--fs-sm); }
.kpi-slot .ui-metric__value { display: flex; align-items: baseline; gap: 4px; margin-top: 6px; }
.kpi-slot .ui-metric__num {
  font-weight: 700; line-height: 1.1;
  color: var(--c-primary);
  font-variant-numeric: tabular-nums; letter-spacing: -0.5px;
}
.kpi-slot .ui-metric__num--text {
  font-size: 18px;
  font-weight: 600;
  color: var(--c-text);
  letter-spacing: 0;
}
.kpi-slot .ui-metric--success .ui-metric__num { color: var(--c-success); }
.kpi-slot .ui-metric--warning .ui-metric__num { color: var(--c-warning); }
.kpi-slot .ui-metric--info    .ui-metric__num { color: var(--c-info); }
.kpi-slot .ui-metric__sub { color: var(--c-muted); font-size: var(--fs-xs); margin-top: 4px; }
</style>