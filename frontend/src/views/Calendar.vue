<template>
  <PageScaffold title="上映月份热力" subtitle="按年份观察影片上映月份分布" :loading="loading" :error="error" @retry="load">
    <template #actions><select v-model.number="selectedYear" class="year-select"><option v-for="year in years" :key="year" :value="year">{{ year }}</option></select></template>
    <UiChartCard :title="`${selectedYear} 年上映热力`" :sub="`${knownTotal} 部有明确月份数据`" class="fade-up">
      <EChart :option="heatmapOption" height="300px" />
    </UiChartCard>
    <UiChartCard title="年度影片数量" sub="最近 20 个有数据年份" class="fade-up">
      <EChart :option="yearOption" height="340px" @itemClick="openYear" />
    </UiChartCard>
  </PageScaffold>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageScaffold from '../components/PageScaffold.vue'
import EChart from '../components/EChart.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import { api } from '../api'
import { releaseMonth } from '../utils/movieFields'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const selectedYear = ref(new Date().getFullYear())
const yearDistribution = ref([])
const movies = ref([])
const years = computed(() => yearDistribution.value.map((item) => Number(item.name)).filter((year) => year > 1900).sort((a, b) => b - a))
const monthly = computed(() => {
  const counts = Array(12).fill(0)
  for (const movie of movies.value) {
    if (Number(movie.year) !== selectedYear.value) continue
    const month = releaseMonth(movie.release_date)
    if (month) counts[month - 1] += 1
  }
  return counts
})
const knownTotal = computed(() => monthly.value.reduce((sum, count) => sum + count, 0))
const heatmapOption = computed(() => ({
  grid: { left: 48, right: 24, top: 34, bottom: 52 },
  tooltip: { formatter: (p) => `${selectedYear.value} 年 ${p.value[0] + 1} 月<br/>上映影片：<b>${p.value[2]}</b>` },
  xAxis: { type: 'category', data: Array.from({ length: 12 }, (_, index) => `${index + 1}月`), splitArea: { show: true }, axisTick: { show: false } },
  yAxis: { type: 'category', data: ['上映数量'], splitArea: { show: true }, axisTick: { show: false } },
  visualMap: { min: 0, max: Math.max(1, ...monthly.value), calculable: false, orient: 'horizontal', left: 'center', bottom: 4, inRange: { color: ['#172554', '#0ea5e9', '#8b5cf6', '#ec4899'] }, text: ['多', '少'], textStyle: { color: '#94a3b8' } },
  series: [{ type: 'heatmap', data: monthly.value.map((value, month) => [month, 0, value]), label: { show: true, color: '#fff', fontWeight: 700 }, itemStyle: { borderColor: '#0f172a', borderWidth: 3 } }],
}))
const yearOption = computed(() => {
  const data = [...yearDistribution.value].sort((a, b) => Number(a.name) - Number(b.name)).slice(-20)
  return { grid: { left: 48, right: 24, top: 24, bottom: 50 }, tooltip: { trigger: 'axis' }, xAxis: { type: 'category', data: data.map((item) => item.name), axisLabel: { rotate: 38 } }, yAxis: { type: 'value', name: '影片数' }, series: [{ type: 'bar', data: data.map((item) => ({ value: item.count, name: item.name })), barMaxWidth: 26, itemStyle: { color: '#38bdf8', borderRadius: [5, 5, 0, 0] } }] }
})
function openYear(params) { if (params?.name) router.push({ path: '/year', query: { v: params.name } }) }
async function load() {
  loading.value = true; error.value = ''
  try {
    const [yearsResponse, moviesResponse] = await Promise.all([api.byYear(), api.paged({ page: 1, size: 100, sort: 'year', order: 'desc' })])
    yearDistribution.value = yearsResponse?.data || []
    movies.value = moviesResponse?.items || []
    if (years.value.length) selectedYear.value = years.value.find((year) => movies.value.some((movie) => Number(movie.year) === year && releaseMonth(movie.release_date))) || years.value[0]
  } catch (exception) { error.value = exception?.message || String(exception) } finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.year-select { min-width: 96px; padding: 6px 10px; color: var(--c-text); background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-sm); }
</style>