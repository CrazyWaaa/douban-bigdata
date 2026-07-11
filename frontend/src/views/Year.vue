<template>
  <div>
    <h2>按年份分布</h2>
    <EChart :option="option" height="420px" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import EChart from '../components/EChart.vue'
import { api } from '../api'

const items = ref([])
onMounted(async () => { items.value = (await api.byYear()).data || [] })

const option = computed(() => ({
  tooltip: {},
  xAxis: { type: 'category', data: items.value.map(i => i.year) },
  yAxis: { type: 'value' },
  series: [{ type: 'line', smooth: true, areaStyle: {}, data: items.value.map(i => i.count) }]
}))
</script>