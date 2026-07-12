<template>
  <div>
    <h2>按地区分布</h2>
    <div v-if="loading" class="muted">加载中…</div>
    <div v-else class="grid-2">
      <div class="card">
        <h3>地区 Top{{ topN }}</h3>
        <EChart :option="pieOption" height="400px" />
      </div>
      <div class="card" style="padding:0;">
        <table class="data-table">
          <thead>
            <tr>
              <th>地区</th>
              <th style="width:80px;">数量</th>
              <th style="width:80px;">平均分</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in byAvg" :key="c.name">
              <td>{{ c.name }}</td>
              <td>{{ c.count }}</td>
              <td class="rating">{{ c.avg_rating?.toFixed?.(2) ?? '-' }}</td>
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

const byAvg = ref([])
const topN = ref(20)
const loading = ref(true)

onMounted(async () => {
  try {
    byAvg.value = (await api.byAvg('country', topN.value))?.data || []
  } finally {
    loading.value = false
  }
})

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 部 ({d}%)' },
  legend: { type: 'scroll', orient: 'vertical', right: 10, top: 'middle', textStyle: { color: '#cbd5e1' } },
  series: [{
    type: 'pie', radius: ['40%', '70%'], center: ['38%', '50%'],
    avoidLabelOverlap: true,
    data: byAvg.value.map(i => ({ name: i.name, value: i.count })),
    label: { color: '#cbd5e1' },
  }],
}))
</script>

<style scoped>
.grid-2 { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 10px; background: #1f2937; color: var(--muted); position: sticky; top: 0; }
.data-table td { padding: 10px; border-top: 1px solid #1f2937; }
.rating { color: var(--primary); font-weight: bold; }
@media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
</style>