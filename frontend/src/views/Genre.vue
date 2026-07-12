<template>
  <div class="dim-page">
    <header class="page-head fade-up">
      <div>
        <h1 class="page-title">类型分布</h1>
        <p class="page-sub">按电影类型聚合,看头部集中度</p>
      </div>
    </header>
    <div v-if="loading" class="muted fade-up">加载中…</div>
    <div v-else class="dim-grid">
      <UiChartCard title="Top10 数量 + 均分" class="fade-up" style="animation-delay: 60ms">
        <EChart :option="dualOption" height="320px" />
      </UiChartCard>
      <UiChartCard title="数量气泡" class="fade-up" style="animation-delay: 120ms">
        <EChart :option="bubbleOption" height="320px" />
      </UiChartCard>
      <UiChartCard title="Top10 数量" class="fade-up dim-grid__full" style="animation-delay: 180ms">
        <div class="dim-list">
          <div v-for="(it, i) in items.slice(0, 10)" :key="it.name" class="dim-list__row" :style="{ animationDelay: (i * 40) + 'ms' }">
            <span class="dim-list__rank">{{ i + 1 }}</span>
            <span class="dim-list__name">{{ it.name }}</span>
            <span class="dim-list__count">{{ it.count }} 部</span>
            <span class="dim-list__rating">{{ Number(it.avg_rating).toFixed(1) }} 分</span>
          </div>
        </div>
      </UiChartCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import EChart from '../components/EChart.vue';
import UiChartCard from '../components/ui/UiChartCard.vue';
import { api } from '../api';

const props = defineProps({ dim: 'genre' });
const items = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const data = await api.byAvg(props.dim, 30);
    items.value = data?.data || [];
  } finally { loading.value = false; }
});

const dualOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 50, top: 30, bottom: 40 },
  legend: { textStyle: { color: '#94a3b8' }, top: 0, right: 0 },
  xAxis: { type: 'category', data: items.value.slice(0, 10).map(d => d.name), axisLabel: { color: '#94a3b8', rotate: 30 } },
  yAxis: [
    { type: 'value', name: '数量', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(148,163,184,.12)' } } },
    { type: 'value', name: '均分', min: 0, max: 10, axisLabel: { color: '#94a3b8' }, splitLine: { show: false } },
  ],
  series: [
    { name: '数量', type: 'bar', data: items.value.slice(0, 10).map(d => d.count),
      itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#38bdf8' }, { offset: 1, color: 'rgba(56,189,248,.15)' }] }, borderRadius: [4,4,0,0] } },
    { name: '均分', type: 'line', yAxisIndex: 1, data: items.value.slice(0, 10).map(d => Number(d.avg_rating)), smooth: true, lineStyle: { color: '#f59e0b', width: 2.5 }, itemStyle: { color: '#f59e0b' } },
  ],
}));

const bubbleOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: p => `${p.data[2]}<br/>数量: ${p.data[0]}<br/>均分: ${p.data[1]}` },
  grid: { left: 40, right: 20, top: 20, bottom: 40 },
  xAxis: { type: 'value', name: '数量', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(148,163,184,.12)' } } },
  yAxis: { type: 'value', name: '均分', min: 0, max: 10, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(148,163,184,.12)' } } },
  series: [{
    type: 'scatter', symbolSize: d => Math.max(12, Math.min(60, d[0] * 3)),
    data: items.value.map(d => [d.count, Number(d.avg_rating), d.name]),
    itemStyle: { color: 'rgba(56,189,248,.55)', borderColor: '#38bdf8', borderWidth: 1 },
    label: { show: true, formatter: p => p.data[2], position: 'right', color: '#94a3b8', fontSize: 11 },
  }],
}));
</script>

<style scoped>
.dim-page { display: flex; flex-direction: column; gap: 16px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px; }
.page-title { margin: 0; font-size: var(--fs-2xl); font-weight: 700; }
.page-sub { margin: 4px 0 0; color: var(--c-muted); font-size: var(--fs-sm); }

.dim-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.dim-grid__full { grid-column: 1 / -1; }

.dim-list { display: flex; flex-direction: column; gap: 4px; }
.dim-list__row {
  display: grid; grid-template-columns: 32px 1fr auto auto;
  align-items: center; gap: 12px;
  padding: 8px 12px; border-radius: var(--r-sm);
  background: var(--c-surface-2);
  opacity: 0; transform: translateY(4px);
  animation: fadeUp .35s var(--ease-out) both;
  transition: background var(--t-fast) var(--ease-out);
}
.dim-list__row:hover { background: var(--c-primary-tint); }
.dim-list__rank { color: var(--c-primary); font-weight: 700; text-align: center; }
.dim-list__name { color: var(--c-text); font-weight: 500; }
.dim-list__count { color: var(--c-muted); font-size: var(--fs-sm); font-variant-numeric: tabular-nums; }
.dim-list__rating { color: var(--c-primary); font-weight: 600; font-size: var(--fs-sm); font-variant-numeric: tabular-nums; }

@media (max-width: 800px) {
  .dim-grid { grid-template-columns: 1fr; }
}
</style>