<template>
  <PageScaffold title="世界电影地图" subtitle="按制片国家与地区展示 Top 250 分布" :loading="loading" :error="error" @retry="load">
    <template #actions><span class="muted">已映射 {{ mapItems.length }} 个国家或地区</span></template>
    <UiChartCard title="全球影片分布" sub="真实国界与经纬度坐标，气泡大小代表影片数量" class="fade-up">
      <EChart :option="mapOption" height="620px" @itemClick="onMapClick" />
    </UiChartCard>
    <UiChartCard title="地区 TOP 12" class="fade-up">
      <div class="country-grid">
        <button v-for="item in topCountries" :key="item.name" @click="goCountry(item.name)"><span>{{ item.name }}</span><b>{{ item.count }}</b></button>
      </div>
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
import { splitMultiValue } from '../utils/movieFields'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const countries = ref([])

const countryMeta = {
  美国: { mapName: 'United States', coord: [-98.5, 39.8] },
  英国: { mapName: 'United Kingdom', coord: [-2, 54] },
  中国大陆: { mapName: 'China', coord: [104, 35] },
  中国: { mapName: 'China', coord: [104, 35] },
  中国香港: { mapName: 'China', coord: [114.1, 22.3] },
  香港: { mapName: 'China', coord: [114.1, 22.3] },
  中国台湾: { mapName: 'Taiwan', coord: [121, 23.7] },
  台湾: { mapName: 'Taiwan', coord: [121, 23.7] },
  日本: { mapName: 'Japan', coord: [138, 36] },
  韩国: { mapName: 'South Korea', coord: [127.8, 36.3] },
  法国: { mapName: 'France', coord: [2, 46] },
  德国: { mapName: 'Germany', coord: [10, 51] },
  意大利: { mapName: 'Italy', coord: [12.5, 42.5] },
  西班牙: { mapName: 'Spain', coord: [-4, 40] },
  加拿大: { mapName: 'Canada', coord: [-106, 56] },
  澳大利亚: { mapName: 'Australia', coord: [134, -25] },
  印度: { mapName: 'India', coord: [78, 21] },
  俄罗斯: { mapName: 'Russia', coord: [100, 62] },
  巴西: { mapName: 'Brazil', coord: [-52, -10] },
  墨西哥: { mapName: 'Mexico', coord: [-102, 23] },
  瑞典: { mapName: 'Sweden', coord: [15, 62] },
  丹麦: { mapName: 'Denmark', coord: [10, 56] },
  挪威: { mapName: 'Norway', coord: [9, 61] },
  波兰: { mapName: 'Poland', coord: [20, 52] },
  阿根廷: { mapName: 'Argentina', coord: [-64, -34] },
  伊朗: { mapName: 'Iran', coord: [53, 32] },
  泰国: { mapName: 'Thailand', coord: [101, 15] },
  新加坡: { mapName: 'Singapore', coord: [103.8, 1.3] },
  新西兰: { mapName: 'New Zealand', coord: [172, -41] },
  瑞士: { mapName: 'Switzerland', coord: [8.2, 46.8] },
  奥地利: { mapName: 'Austria', coord: [14.5, 47.5] },
  爱尔兰: { mapName: 'Ireland', coord: [-8, 53] },
  比利时: { mapName: 'Belgium', coord: [4.5, 50.8] },
  丹麦瑞典: { mapName: 'Denmark', coord: [11, 57] },
}

const mapItems = computed(() => {
  const merged = new Map()
  for (const row of countries.value) {
    for (const name of splitMultiValue(row.name)) {
      const meta = countryMeta[name]
      if (!meta) continue
      const current = merged.get(name) || { name, count: 0, ...meta }
      current.count += Number(row.count || 0)
      merged.set(name, current)
    }
  }
  return [...merged.values()].sort((first, second) => second.count - first.count)
})
const topCountries = computed(() => mapItems.value.slice(0, 12))
const maxCount = computed(() => Math.max(1, ...mapItems.value.map((item) => item.count)))
const mapOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    formatter: (params) => params.seriesType === 'effectScatter'
      ? `${params.data.name}<br/>影片数：<b>${params.data.count}</b>`
      : params.name,
  },
  geo: {
    map: 'world',
    roam: true,
    zoom: 1.08,
    center: [12, 22],
    layoutCenter: ['50%', '50%'],
    layoutSize: '102%',
    itemStyle: { areaColor: '#183b5b', borderColor: '#3b82a6', borderWidth: 0.7 },
    emphasis: { itemStyle: { areaColor: '#245b7d' }, label: { show: false } },
    select: { disabled: true },
    silent: false,
  },
  series: [
    {
      name: '影片数量',
      type: 'effectScatter',
      coordinateSystem: 'geo',
      zlevel: 2,
      data: mapItems.value.map((item) => ({ name: item.name, count: item.count, value: [...item.coord, item.count] })),
      symbolSize: (value) => 7 + Math.sqrt(Number(value[2]) / maxCount.value) * 28,
      rippleEffect: { brushType: 'stroke', scale: 2.4 },
      showEffectOn: 'emphasis',
      itemStyle: { color: '#38bdf8', shadowBlur: 12, shadowColor: '#38bdf8' },
      label: {
        show: true,
        position: 'right',
        formatter: (params) => `${params.data.name} ${params.data.count}`,
        color: '#e2e8f0',
        fontSize: 10,
        textBorderColor: '#071a33',
        textBorderWidth: 3,
      },
      labelLayout: { hideOverlap: true },
      emphasis: { scale: 1.3, itemStyle: { color: '#f59e0b' } },
    },
  ],
}))

function goCountry(name) { router.push({ path: '/country', query: { v: name } }) }
function onMapClick(params) { if (params?.seriesType === 'effectScatter' && params.data?.name) goCountry(params.data.name) }
async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.byCountry()
    countries.value = response?.data || []
    if (!mapItems.value.length) throw new Error('国家字段无法映射到世界地图')
  } catch (exception) {
    error.value = exception?.message || String(exception)
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<style scoped>
.country-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }
.country-grid button { display: flex; justify-content: space-between; padding: 10px 12px; color: var(--c-text); background: var(--c-surface-2); border: 1px solid var(--c-border); border-radius: var(--r-sm); cursor: pointer; }
.country-grid button:hover { border-color: var(--c-primary); background: var(--c-primary-tint); }
.country-grid b { color: var(--c-primary); }
@media (max-width: 760px) { .country-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>