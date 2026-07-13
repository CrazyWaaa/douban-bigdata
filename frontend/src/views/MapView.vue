<template>
  <PageScaffold
    title="全球电影分布"
    subtitle="气泡大小 = 影片数,点击气泡跳转国家维度页"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <span class="muted">基于 {{ summaryExt?.total ?? 0 }} 部影片</span>
    </template>

    <UiChartCard title="世界地图 · 影片分布" sub="使用 ECharts 内置世界地图" class="fade-up">
      <EChart :option="mapOption" height="540px" @itemClick="onItemClick" />
    </UiChartCard>

    <UiChartCard title="地区 TOP 10" sub="按影片数排名" class="fade-up" style="animation-delay: 80ms">
      <ul class="map-list">
        <li
          v-for="(c, i) in topCountries"
          :key="c.name"
          class="map-list__row fade-up"
          :style="{ animationDelay: (i * 30) + 'ms' }"
          @click="goCountry(c.name)"
        >
          <span class="map-list__rank">{{ i + 1 }}</span>
          <span class="map-list__name">{{ c.name }}</span>
          <div class="map-list__bar">
            <div class="map-list__fill" :style="{ width: pctOf(c.count) + '%' }"></div>
          </div>
          <span class="map-list__count">{{ c.count }} 部</span>
        </li>
      </ul>
    </UiChartCard>
  </PageScaffold>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageScaffold from '../components/PageScaffold.vue'
import EChart from '../components/EChart.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import { api } from '../api'
import { buildMapOption } from '../echarts/options'
import { useDashboardStore } from '../stores/dashboard'

const router = useRouter()
const store = useDashboardStore()
const loading = ref(false)
const error = ref('')

const COUNTRY_COORDS = {
  '美国': [-98.5, 39.8], 'USA': [-98.5, 39.8], 'United States': [-98.5, 39.8],
  '英国': [-2, 54], 'UK': [-2, 54], 'United Kingdom': [-2, 54],
  '中国大陆': [104, 35], '中国': [104, 35], 'China': [104, 35], '香港': [114.1, 22.3], '台湾': [121, 23.7], 'Hong Kong': [114.1, 22.3], 'Taiwan': [121, 23.7],
  '日本': [138, 36], 'Japan': [138, 36],
  '韩国': [127, 36], 'South Korea': [127, 36], 'Korea': [127, 36],
  '法国': [2, 46], 'France': [2, 46],
  '德国': [10, 51], 'Germany': [10, 51],
  '意大利': [12, 42], 'Italy': [12, 42],
  '西班牙': [-4, 40], 'Spain': [-4, 40],
  '加拿大': [-100, 56], 'Canada': [-100, 56],
  '澳大利亚': [134, -25], 'Australia': [134, -25],
  '印度': [78, 21], 'India': [78, 21],
  '俄罗斯': [100, 62], 'Russia': [100, 62],
  '巴西': [-55, -10], 'Brazil': [-55, -10],
  '墨西哥': [-102, 23], 'Mexico': [-102, 23],
  '瑞典': [15, 62], 'Sweden': [15, 62],
  '丹麦': [10, 56], 'Denmark': [10, 56],
  '挪威': [9, 60], 'Norway': [9, 60],
  '波兰': [20, 52], 'Poland': [20, 52],
  '阿根廷': [-64, -34], 'Argentina': [-64, -34],
  '伊朗': [53, 32], 'Iran': [53, 32],
  '泰国': [101, 15], 'Thailand': [101, 15],
  '新加坡': [103.8, 1.3], 'Singapore': [103.8, 1.3],
  '新西兰': [172, -41], 'New Zealand': [172, -41],
}

const topCountries = computed(() => (store.countries || []).slice(0, 10))
const summaryExt = computed(() => store.summaryExt || {})

const mapItems = computed(() => {
  return (store.countries || [])
    .map((c) => {
      const coord = COUNTRY_COORDS[c.name]
      return coord ? { name: c.name, value: [...coord, c.count] } : null
    })
    .filter(Boolean)
})

const mapOption = computed(() => buildMapOption(mapItems.value))
const maxCount = computed(() => Math.max(1, ...topCountries.value.map((c) => c.count || 0)))
function pctOf(n) { return Math.max(2, (n / maxCount.value) * 100) }

function goCountry(name) {
  router.push({ path: '/country', query: { dim: 'country', v: name } })
}

function onItemClick(p) {
  if (p?.name) goCountry(p.name)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (!store.countries?.length) await store.loadAll()
    if (!mapItems.value.length) console.warn('[Map] 没有任何国家有坐标映射')
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.map-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }
.map-list__row {
  display: grid; grid-template-columns: 28px 100px 1fr 60px;
  align-items: center; gap: 10px;
  padding: 6px 10px; border-radius: var(--r-sm); cursor: pointer;
  transition: background var(--t-fast) var(--ease-out);
}
.map-list__row:hover { background: var(--c-primary-tint); }
.map-list__rank { color: var(--c-muted); font-weight: 700; text-align: center; font-size: var(--fs-sm); }
.map-list__name { color: var(--c-text); font-weight: 500; font-size: var(--fs-sm); }
.map-list__bar { height: 6px; border-radius: 3px; background: var(--c-surface-2); overflow: hidden; }
.map-list__fill {
  height: 100%;
  background: linear-gradient(90deg, var(--c-primary), var(--c-info));
  transition: filter var(--t-fast) var(--ease-out);
}
.map-list__row:hover .map-list__fill { filter: brightness(1.2); }
.map-list__count { color: var(--c-muted); font-size: var(--fs-xs); text-align: right; font-variant-numeric: tabular-nums; }
</style>
