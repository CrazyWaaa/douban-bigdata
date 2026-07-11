<template>
  <div>
    <h2>按类型分布</h2>
    <div v-if="loading" class="muted">加载中...</div>
    <div v-else>
      <EChart :option="option" height="420px" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import EChart from '../components/EChart.vue'
import { api } from '../api'

const items = ref([])
const loading = ref(true)
onMounted(async () => {
  try { items.value = (await api.byGenre()).data || [] } finally { loading.value = false }
})

const option = computed(() => ({
  tooltip: {},
  xAxis: { type: 'category', data: items.value.map(i => i.name) },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: items.value.map(i => i.count) }]
}))
</script>