<template>
  <div>
    <div class="header">
      <h2>豆瓣电影数据大屏</h2>
      <div class="header-meta">
        <span v-if="lastLoadedAt" class="muted">
          上次更新: {{ formatTime(lastLoadedAt) }}
        </span>
        <button class="btn" :disabled="loading" @click="refresh">
          {{ loading ? '刷新中…' : '刷新' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>

    <!-- 顶部 6 个指标卡 -->
    <section class="metrics">
      <div class="metric-card" v-for="m in metricCards" :key="m.key">
        <div class="metric-label">{{ m.label }}</div>
        <div class="metric-value">{{ m.value }}</div>
        <div v-if="m.sub" class="metric-sub">{{ m.sub }}</div>
      </div>
    </section>

    <!-- 第一行:3 个双轴图(类型/地区/年份 数量+均分) -->
    <section class="grid-3">
      <div class="card chart-card">
        <h3>类型分布 Top10 <span class="muted">(柱=数量 / 折线=均分)</span></h3>
        <EChart :option="genreOption" height="300px" />
      </div>
      <div class="card chart-card">
        <h3>地区分布 Top10 <span class="muted">(柱=数量 / 折线=均分)</span></h3>
        <EChart :option="countryOption" height="300px" />
      </div>
      <div class="card chart-card">
        <h3>年代趋势 <span class="muted">(柱=数量 / 折线=均分)</span></h3>
        <EChart :option="yearOption" height="300px" />
      </div>
    </section>

    <!-- 第二行:3 个分布直方图 + 1 个年代榜 -->
    <section class="grid-4">
      <div class="card chart-card">
        <h3>评分分布</h3>
        <EChart :option="ratingDistOption" height="260px" />
      </div>
      <div class="card chart-card">
        <h3>片长分布(分钟)</h3>
        <EChart :option="runtimeDistOption" height="260px" />
      </div>
      <div class="card chart-card">
        <h3>导演榜 Top10</h3>
        <EChart :option="directorOption" height="260px" />
      </div>
      <div class="card chart-card">
        <h3>语言榜 Top10</h3>
        <EChart :option="languageOption" height="260px" />
      </div>
    </section>

    <!-- 第三行:高分榜(左宽) + 年代汇总(右窄) -->
    <section class="grid-2-1">
      <div class="card chart-card">
        <h3>高分榜 Top20</h3>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width:48px;">#</th>
                <th>片名</th>
                <th style="width:90px;">导演</th>
                <th style="width:60px;">年份</th>
                <th style="width:60px;">评分</th>
                <th style="width:90px;">评价数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in topRated" :key="m.douban_id">
                <td class="rank">{{ m.rank }}</td>
                <td>
                  <router-link :to="`/movie/${m.douban_id}`">{{ m.title }}</router-link>
                  <div v-if="m.quote" class="quote">"{{ m.quote }}"</div>
                </td>
                <td class="muted-cell">{{ m.director }}</td>
                <td>{{ m.year }}</td>
                <td class="rating">{{ m.rating?.toFixed?.(1) }}</td>
                <td class="muted-cell">{{ formatCount(m.rating_count) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card chart-card">
        <h3>年代汇总</h3>
        <EChart :option="decadeOption" height="320px" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import EChart from '../components/EChart.vue'
import { useDashboardStore } from '../stores/dashboard'
import { storeToRefs } from 'pinia'

const store = useDashboardStore()
const {
  summaryExt, genres, countries, years,
  avgByGenre, avgByCountry, avgByYear,
  directors, languages, decades,
  ratingDist, runtimeDist, topRated,
  loading, error, lastLoadedAt,
} = storeToRefs(store)

onMounted(() => store.loadAll())

function refresh() {
  store.loadAll()
}

function formatTime(ts) {
  const d = new Date(ts)
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}
function formatCount(n) {
  if (n == null) return '-'
  if (n >= 10000) return (n / 10000).toFixed(1) + ' 万'
  return n.toLocaleString()
}

const metricCards = computed(() => {
  const s = summaryExt.value || {}
  return [
    { key: 'total',    label: '影片总数',   value: s.total ?? '-', sub: '' },
    { key: 'avg',      label: '平均评分',   value: s.avg_rating?.toFixed?.(2) ?? '-', sub: '' },
    { key: 'max',      label: '最高分',     value: s.max_rating?.toFixed?.(1) ?? '-', sub: '' },
    { key: 'count',    label: '总评价数',   value: formatCount(s.total_rating_count), sub: '人次' },
    { key: 'genre',    label: '类型维度',   value: s.distinct_genre ?? '-', sub: '种' },
    { key: 'country',  label: '地区维度',   value: s.distinct_country ?? '-', sub: '个' },
  ]
})

// ============ 复合图:柱=数量 + 折线=均分 ============
function dualAxisOption(items, nameField = 'name') {
  const labels = items.map(i => i[nameField])
  const counts = items.map(i => i.count || 0)
  const avgs = items.map(i => i.avg_rating ?? null)
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: ['数量', '均分'], textStyle: { color: '#cbd5e1' } },
    grid: { left: 50, right: 60, top: 40, bottom: 70 },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 30, color: '#94a3b8' } },
    yAxis: [
      { type: 'value', name: '数量', position: 'left', axisLabel: { color: '#94a3b8' } },
      { type: 'value', name: '均分', position: 'right', min: 6, max: 10, axisLabel: { color: '#94a3b8' } },
    ],
    series: [
      {
        name: '数量', type: 'bar', data: counts,
        itemStyle: { color: '#38bdf8' },
        label: { show: true, position: 'top', color: '#94a3b8', fontSize: 11 },
      },
      {
        name: '均分', type: 'line', yAxisIndex: 1, data: avgs,
        smooth: true, symbolSize: 6,
        itemStyle: { color: '#f59e0b' },
        lineStyle: { width: 2 },
      },
    ],
  }
}

const genreOption   = computed(() => dualAxisOption(avgByGenre.value))
const countryOption = computed(() => dualAxisOption(avgByCountry.value))
const yearOption    = computed(() => dualAxisOption(avgByYear.value))

// ============ 直方图 ============
const ratingDistOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 30, bottom: 40 },
  xAxis: { type: 'category', data: ratingDist.value.map(d => d.bucket), axisLabel: { color: '#94a3b8' } },
  yAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
  series: [{
    type: 'bar', data: ratingDist.value.map(d => d.count),
    itemStyle: { color: '#22d3ee' },
    label: { show: true, position: 'top', color: '#94a3b8' },
  }],
}))

const runtimeDistOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 30, bottom: 40 },
  xAxis: { type: 'category', data: runtimeDist.value.map(d => d.bucket), axisLabel: { color: '#94a3b8' } },
  yAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
  series: [{
    type: 'bar', data: runtimeDist.value.map(d => d.count),
    itemStyle: { color: '#a78bfa' },
    label: { show: true, position: 'top', color: '#94a3b8' },
  }],
}))

// ============ 导演 / 语言 横向条形 ============
function hbarOption(items, valueField = 'count', labelField = 'name', top = 10) {
  const sliced = items.slice(0, top).slice().reverse()
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 100, right: 30, top: 10, bottom: 30 },
    xAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'category', data: sliced.map(i => i[labelField]), axisLabel: { color: '#cbd5e1' } },
    series: [{
      type: 'bar', data: sliced.map(i => i[valueField]),
      itemStyle: { color: '#34d399' },
      label: { show: true, position: 'right', color: '#94a3b8', fontSize: 11 },
    }],
  }
}
const directorOption = computed(() => hbarOption(directors.value, 'count', 'name', 10))
const languageOption = computed(() => hbarOption(languages.value, 'count', 'name', 10))

// ============ 年代汇总:柱+折线 ============
const decadeOption = computed(() => dualAxisOption(decades.value))
</script>

<style scoped>
.header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 14px;
}
.header-meta { display: flex; align-items: center; gap: 12px; }
.btn {
  padding: 6px 14px; border-radius: 6px; border: 1px solid #1f2937;
  background: var(--surface); color: var(--text); cursor: pointer;
}
.btn:hover:not(:disabled) { border-color: var(--primary); color: var(--primary); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.error-banner {
  padding: 10px 14px; border-radius: 6px; margin-bottom: 12px;
  background: #7f1d1d33; color: #fca5a5; border: 1px solid #b91c1c;
}

.metrics {
  display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 14px;
}
.metric-card {
  background: var(--surface); border: 1px solid #1f2937; border-radius: 8px;
  padding: 14px; text-align: center;
}
.metric-label { color: var(--muted); font-size: 12px; margin-bottom: 6px; }
.metric-value { color: var(--primary); font-size: 26px; font-weight: 700; }
.metric-sub { color: var(--muted); font-size: 11px; margin-top: 2px; }

.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 14px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 14px; }
.grid-2-1 { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; }

.chart-card h3 {
  margin: 0 0 10px 0; color: var(--text); font-size: 14px;
  display: flex; align-items: baseline; gap: 8px;
}
.chart-card h3 .muted { font-weight: normal; font-size: 12px; }

.table-wrap { max-height: 520px; overflow-y: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  text-align: left; padding: 8px; background: #1f2937;
  color: var(--muted); font-weight: 500; position: sticky; top: 0;
}
.data-table td { padding: 8px; border-top: 1px solid #1f2937; vertical-align: top; }
.data-table .rank { color: var(--primary); font-weight: bold; }
.data-table .rating { color: var(--primary); font-weight: bold; }
.data-table .muted-cell { color: #94a3b8; font-size: 12px; }
.data-table .quote { color: #64748b; font-size: 11px; margin-top: 2px; font-style: italic; }

@media (max-width: 1100px) {
  .metrics { grid-template-columns: repeat(3, 1fr); }
  .grid-3 { grid-template-columns: 1fr; }
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
  .grid-2-1 { grid-template-columns: 1fr; }
}
@media (max-width: 600px) {
  .metrics { grid-template-columns: repeat(2, 1fr); }
  .grid-4 { grid-template-columns: 1fr; }
}
</style>