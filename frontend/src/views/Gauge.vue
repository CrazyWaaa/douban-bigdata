<template>
  <PageScaffold
    title="品质仪表盘"
    subtitle="多指针仪表 + 类型雷达,一屏看完整体品质"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <span class="muted">基于 {{ summaryExt?.total ?? 0 }} 部影片</span>
    </template>

    <UiChartCard title="核心指标 · 指针仪表" sub="均分 / 最高分 / TOP200 入榜率 / 年代覆盖" class="fade-up">
      <EChart :option="gaugeOption" height="320px" />
    </UiChartCard>

    <div class="gauge-grid">
      <UiChartCard title="评价数水位(单部均评)" class="fade-up" style="animation-delay: 60ms">
        <EChart :option="liquidOption" height="280px" />
      </UiChartCard>
      <UiChartCard title="类型均分雷达" class="fade-up" style="animation-delay: 120ms">
        <EChart :option="radarOption" height="280px" />
      </UiChartCard>
    </div>
  </PageScaffold>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PageScaffold from '../components/PageScaffold.vue'
import EChart from '../components/EChart.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import { buildGaugeOption, buildRadarOption } from '../echarts/options'
import { useDashboardStore } from '../stores/dashboard'

const store = useDashboardStore()
const loading = ref(false)
const error = ref('')

const summary = computed(() => store.summary || {})
const summaryExt = computed(() => store.summaryExt || {})
const avgByGenre = computed(() => store.avgByGenre || [])

const gaugeItems = computed(() => {
  const ext = summaryExt.value
  const total = ext.total || 0
  const top200 = ext.top200_count || ext.top200 || 0
  const yearSpan = ext.year_span || 0
  const maxRating = ext.max_rating || 10
  return [
    { name: '均分',     value: Number((ext.avg_rating || 0).toFixed(1)), max: 10, color: '#38bdf8' },
    { name: '最高分',   value: Number(maxRating.toFixed(1)),              max: 10, color: '#f59e0b' },
    { name: 'TOP200',   value: total ? Math.round((top200 / total) * 100) : 0, max: 100, color: '#34d399' },
    { name: '年代覆盖', value: Math.min(100, yearSpan),                    max: 100, color: '#a78bfa' },
  ]
})

const gaugeOption = computed(() => buildGaugeOption(gaugeItems.value))

// 自定义"水位"图:用 liquidFill 不在当前模块里(避免引入),改用条形进度环替代,效果更可控
const liquidOption = computed(() => {
  const avgCount = Number(summaryExt.value.avg_rating_count || 0)
  // 评价数归一化到 0-1 区间(以 1M 为满量程)
  const ratio = Math.min(1, Math.log10(Math.max(10, avgCount)) / 6)
  const total = Math.round(ratio * 100)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 30, right: 16, top: 30, bottom: 30, containLabel: true },
    xAxis: {
      type: 'value', max: 100,
      axisLine: { show: false }, axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,.1)' } },
      axisLabel: { color: '#94a3b8', formatter: '{value}%' },
    },
    yAxis: {
      type: 'category', data: ['单部均评'],
      axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#cbd5e1', fontSize: 13 },
    },
    series: [{
      type: 'bar',
      data: [total],
      barWidth: 32,
      itemStyle: {
        borderRadius: [0, 16, 16, 0],
        color: {
          type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [
            { offset: 0, color: 'rgba(56,189,248,.15)' },
            { offset: 0.5, color: '#38bdf8' },
            { offset: 1, color: '#a78bfa' },
          ],
        },
      },
      label: {
        show: true, position: 'right', color: '#38bdf8', fontWeight: 700, fontSize: 18,
        formatter: () => `${avgCount.toLocaleString()} 人 / 部`,
      },
    }],
  }
})

const radarItems = computed(() => avgByGenre.value.slice(0, 6).map((d) => ({
  name: d.name,
  values: [
    Number(d.avg_rating || 0),
    Number(d.avg_rating || 0) * 0.95,
    Number(d.avg_rating || 0) * 0.9,
    Number(d.avg_rating || 0) * 0.95,
    Number(d.avg_rating || 0) * 0.92,
  ],
})))
const radarOption = computed(() => buildRadarOption(radarItems.value))

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (!store.summaryExt) await store.loadAll()
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.gauge-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 14px;
}
@media (max-width: 1000px) { .gauge-grid { grid-template-columns: 1fr; } }
</style>
