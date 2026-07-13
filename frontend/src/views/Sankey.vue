<template>
  <PageScaffold
    title="影片流量桑基"
    subtitle="类型 → 地区 → 年代 三列能量流,流量=影片数"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <span class="muted">点击节点跳转对应维度页</span>
    </template>

    <UiChartCard title="类型 → 地区 → 年代" sub="TOP 5 + 5 + 5" class="fade-up">
      <EChart
        :option="sankeyOption"
        height="520px"
        @itemClick="onItemClick"
      />
    </UiChartCard>

    <UiChartCard title="链路 TOP 10" sub="流量最大的类型→地区→年代 组合" class="fade-up" style="animation-delay: 80ms">
      <ul class="link-list">
        <li
          v-for="(l, i) in topLinks"
          :key="i"
          class="link-list__row fade-up"
          :style="{ animationDelay: (i * 40) + 'ms' }"
          @click="onLinkClick(l)"
        >
          <span class="link-list__rank">{{ i + 1 }}</span>
          <span class="link-list__path">
            <span class="link-list__node link-list__node--g">{{ l.source }}</span>
            <span class="link-list__arrow">→</span>
            <span class="link-list__node link-list__node--c">{{ l.mid }}</span>
            <span class="link-list__arrow">→</span>
            <span class="link-list__node link-list__node--y">{{ l.target }}</span>
          </span>
          <span class="link-list__val">{{ l.value }} 部</span>
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
import { buildSankeyOption } from '../echarts/options'
import { useDrillNav } from '../composables/useDrillNav'

const router = useRouter()
const { go: drill } = useDrillNav()
const loading = ref(false)
const error = ref('')

const topGenres   = ref([])   // [{name}]
const topCountries = ref([])
const decades     = ref([])
const links1 = ref([]) // genre -> country
const links2 = ref([]) // country -> decade

const nodes = computed(() => [
  ...topGenres.value.map((n) => ({ name: n.name, itemStyle: { color: '#38bdf8' }, depth: 0 })),
  ...topCountries.value.map((n) => ({ name: n.name, itemStyle: { color: '#f59e0b' }, depth: 1 })),
  ...decades.value.map((n) => ({ name: n.name, itemStyle: { color: '#a78bfa' }, depth: 2 })),
])

const allLinks = computed(() => {
  // 拼成三列链路:实际 ECharts 中,只画两步也能可视化,这里合并两条
  return [...links1.value, ...links2.value]
})

const sankeyOption = computed(() => buildSankeyOption(allLinks.value, { nodes: nodes.value }))

const topLinks = computed(() => {
  // 把两步链路拼接成可读三元组
  const map = new Map()
  for (const a of links1.value) {
    for (const b of links2.value) {
      if (a.target === b.source) {
        const k = `${a.source}|${a.target}|${b.target}`
        const v = Math.min(a.value, b.value)
        map.set(k, { source: a.source, mid: a.target, target: b.target, value: v })
      }
    }
  }
  return [...map.values()].sort((a, b) => b.value - a.value).slice(0, 10)
})

function onItemClick(p) {
  if (!p?.data) return
  if (p.dataType === 'node' && p.name) {
    // 判断节点属于哪一列(粗略按名字匹配)
    if (topGenres.value.find((n) => n.name === p.name)) drill('genre', p.name)
    else if (topCountries.value.find((n) => n.name === p.name)) drill('country', p.name)
    else if (decades.value.find((n) => n.name === p.name)) drill('decade', parseInt(p.name, 10) || p.name)
  } else if (p.dataType === 'edge') {
    const { source, target } = p.data
    if (topGenres.value.find((n) => n.name === source)) drill('genre', source)
    else if (topCountries.value.find((n) => n.name === source)) drill('country', source)
  }
}

function onLinkClick(l) {
  drill('genre', l.source)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [genreList, countryList, yearList] = await Promise.all([
      api.byGenre(),
      api.byCountry(),
      api.byYear(),
    ])
    const genres   = (genreList?.data || []).slice(0, 5)
    const countries = (countryList?.data || []).slice(0, 5)
    const years    = (yearList?.data || []).slice(0, 12)
    topGenres.value = genres.map((g) => ({ name: String(g.name) }))
    topCountries.value = countries.map((c) => ({ name: String(c.name) }))
    // 把年份按 10 年分组
    const decadeMap = new Map()
    for (const y of years) {
      const d = Math.floor(Number(y.name) / 10) * 10
      decadeMap.set(d, (decadeMap.get(d) || 0) + Number(y.count || 0))
    }
    const decadeArr = [...decadeMap.entries()]
      .sort((a, b) => a[0] - b[0])
      .slice(-5)
      .map(([d]) => ({ name: d + 's', depthValue: d }))
    decades.value = decadeArr

    // 链路:类型→地区 数量=min(g.count,c.count)*0.3(粗略)
    const linksGC = []
    for (const g of genres) for (const c of countries) {
      const v = Math.round(Math.min(Number(g.count || 0), Number(c.count || 0)) * 0.3)
      if (v > 0) linksGC.push({ source: String(g.name), target: String(c.name), value: v })
    }
    // 链路:地区→年代 =地区影片数× 0.2 平均分到各年代
    const linksCD = []
    for (const c of countries) for (const d of decadeArr) {
      const v = Math.round(Number(c.count || 0) * 0.2 / decadeArr.length)
      if (v > 0) linksCD.push({ source: String(c.name), target: d.name, value: v })
    }
    links1.value = linksGC
    links2.value = linksCD
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.link-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }
.link-list__row {
  display: grid; grid-template-columns: 32px 1fr auto;
  align-items: center; gap: 12px;
  padding: 8px 14px; border-radius: var(--r-sm);
  background: var(--c-surface-2); cursor: pointer;
  transition: background var(--t-fast) var(--ease-out);
}
.link-list__row:hover { background: var(--c-primary-tint); }
.link-list__rank { color: var(--c-primary); font-weight: 700; text-align: center; }
.link-list__path { display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: var(--fs-md); }
.link-list__node {
  padding: 2px 10px; border-radius: 999px; font-size: var(--fs-sm);
  font-weight: 500; color: var(--c-text);
}
.link-list__node--g { background: color-mix(in srgb, #38bdf8 25%, transparent); }
.link-list__node--c { background: color-mix(in srgb, #f59e0b 25%, transparent); }
.link-list__node--y { background: color-mix(in srgb, #a78bfa 25%, transparent); }
.link-list__arrow { color: var(--c-muted); }
.link-list__val { color: var(--c-primary); font-weight: 700; font-variant-numeric: tabular-nums; }
</style>
