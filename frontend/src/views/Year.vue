<template>
  <div>
    <h2>按年代分布</h2>
    <div v-if="loading" class="muted">加载中…</div>
    <div v-else class="grid-2">
      <div class="card">
        <h3>年代趋势 <span class="muted">(柱=数量 / 折线=均分)</span></h3>
        <EChart :option="dualOption" height="400px" />
      </div>
      <div class="card" style="padding:0;">
        <table class="data-table">
          <thead>
            <tr>
              <th>年份</th>
              <th style="width:80px;">数量</th>
              <th style="width:80px;">平均分</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="y in byYear" :key="y.name">
              <td>{{ y.name }}</td>
              <td>{{ y.count }}</td>
              <td class="rating">{{ y.avg_rating?.toFixed?.(2) ?? '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import EChart from '../components/EChart.vue'
import { api } from '../api'

const byYear = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    byYear.value = (await api.byAvg('year', 50))?.data || []
  } finally {
    loading.value = false
  }
})

const dualOption = computed(() => {
  const items = byYear.value
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { data: ['数量', '均分'], textStyle: { color: '#cbd5e1' } },
    grid: { left: 50, right: 60, top: 40, bottom: 70 },
    xAxis: { type: 'category', data: items.map(i => i.name), axisLabel: { rotate: 40, color: '#94a3b8' } },
    yAxis: [
      { type: 'value', name: '数量', axisLabel: { color: '#94a3b8' } },
      { type: 'value', name: '均分', min: 6, max: 10, axisLabel: { color: '#94a3b8' } },
    ],
    series: [
      { name: '数量', type: 'bar', data: items.map(i => i.count), itemStyle: { color: '#38bdf8' },
        label: { show: true, position: 'top', color: '#94a3b8' } },
      { name: '均分', type: 'line', yAxisIndex: 1, smooth: true,
        data: items.map(i => i.avg_rating), itemStyle: { color: '#f59e0b' } },
    ],
  }
})
</script>

<style scoped>
.grid-2 { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 10px; background: #1f2937; color: var(--muted); position: sticky; top: 0; }
.data-table td { padding: 10px; border-top: 1px solid #1f2937; }
.rating { color: var(--primary); font-weight: bold; }
@media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
</style>