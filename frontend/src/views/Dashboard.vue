<template>
  <div>
    <h2>电影数据大屏</h2>
    <div v-if="loading" class="muted">加载中…</div>
    <div v-else-if="error" class="muted">暂无数据：{{ error }}</div>
    <div v-else class="dashboard-grid">
      <!-- 顶部 4 个指标卡 -->
      <section class="metrics">
        <div class="metric-card">
          <div class="metric-label">电影总数</div>
          <div class="metric-value">{{ summary?.total ?? '-' }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">平均评分</div>
          <div class="metric-value">{{ summary?.avg_rating?.toFixed?.(2) ?? '-' }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">类型数</div>
          <div class="metric-value">{{ summary?.distinct_genre ?? '-' }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">地区数</div>
          <div class="metric-value">{{ summary?.distinct_country ?? '-' }}</div>
        </div>
      </section>

      <!-- 类型 Top10 -->
      <section class="card chart-card">
        <h3>类型 Top10</h3>
        <EChart :option="genreOption" height="320px" />
      </section>

      <!-- 年份趋势 -->
      <section class="card chart-card">
        <h3>年份趋势</h3>
        <EChart :option="yearOption" height="320px" />
      </section>

      <!-- 国家分布 Top10 -->
      <section class="card chart-card wide">
        <h3>国家分布 Top10</h3>
        <EChart :option="countryOption" height="360px" />
      </section>

      <!-- 评分 Top10（来自 top_rated 接口） -->
      <section class="card chart-card wide">
        <h3>评分 Top10</h3>
        <EChart :option="topOption" height="360px" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import EChart from '../components/EChart.vue'
import { useDashboardStore } from '../stores/dashboard'
import { storeToRefs } from 'pinia'

const store = useDashboardStore()
const { summary, genres, countries, years, topRated, loading, error } = storeToRefs(store)
onMounted(() => store.loadAll())

const genreOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 20, bottom: 60 },
  xAxis: { type: 'category', data: genres.value.slice(0, 10).map(i => i.name), axisLabel: { rotate: 30 } },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: genres.value.slice(0, 10).map(i => i.count),
    itemStyle: { color: '#38bdf8' },
    label: { show: true, position: 'top', color: '#94a3b8' },
  }],
}))

const yearOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 50, right: 20, top: 20, bottom: 40 },
  xAxis: { type: 'category', data: years.value.map(i => i.year) },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    smooth: true,
    areaStyle: { opacity: 0.3 },
    data: years.value.map(i => i.count),
    itemStyle: { color: '#38bdf8' },
  }],
}))

const countryOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { type: 'scroll', orient: 'vertical', right: 10, top: 'middle', textStyle: { color: '#cbd5e1' } },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    center: ['38%', '50%'],
    avoidLabelOverlap: true,
    data: countries.value.slice(0, 10).map(i => ({ name: i.name, value: i.count })),
  }],
}))

const topOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 120, right: 30, top: 20, bottom: 30 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: topRated.value.slice().reverse().map(i => i.title), axisLabel: { color: '#cbd5e1' } },
  series: [{
    type: 'bar',
    data: topRated.value.slice().reverse().map(i => i.rating),
    itemStyle: { color: '#22d3ee' },
    label: { show: true, position: 'right', color: '#94a3b8' },
  }],
}))
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.metric-card {
  background: var(--surface);
  border: 1px solid #1f2937;
  border-radius: 8px;
  padding: 18px;
  text-align: center;
}
.metric-label { color: var(--muted); font-size: 13px; margin-bottom: 8px; }
.metric-value { color: var(--primary); font-size: 32px; font-weight: 700; }
.chart-card h3 { margin: 0 0 12px 0; color: var(--text); font-size: 15px; }
.chart-card.wide { /* 占整行 */ }
@media (min-width: 900px) {
  .chart-card.wide { grid-column: span 1; }
}
</style>