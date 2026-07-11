<template>
  <div>
    <h2>按地区分布</h2>
    <EChart :option="option" height="420px" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import EChart from '../components/EChart.vue'
import { api } from '../api'

const items = ref([])
onMounted(async () => { items.value = (await api.byCountry()).data || [] })

const option = computed(() => ({
  tooltip: {},
  series: [{
    type: 'pie',
    radius: '60%',
    data: items.value.map(i => ({ name: i.name, value: i.count }))
  }]
}))
</script>