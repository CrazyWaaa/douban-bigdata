<template>
  <PageScaffold title="影人关系网络" subtitle="演员合作与导演—演员关系" :loading="loading" :error="error" @retry="load">
    <template #actions><div class="tab-bar"><button :class="{ active: mode === 'actors' }" @click="mode = 'actors'">演员合作</button><button :class="{ active: mode === 'mixed' }" @click="mode = 'mixed'">导演 × 演员</button></div></template>
    <UiChartCard :title="mode === 'actors' ? '演员合作网络' : '导演与演员网络'" :sub="`${graph.nodes.length} 个节点 · ${graph.links.length} 条关系`" class="fade-up">
      <EChart :option="option" height="620px" @itemClick="openPerson" />
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
import { splitPeople } from '../utils/movieFields'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const mode = ref('actors')
const movies = ref([])

function createGraph(selectedMode) {
  const edgeMap = new Map()
  const category = new Map()
  for (const movie of movies.value) {
    const actors = splitPeople(movie.actors).slice(0, 4)
    const directors = splitPeople(movie.director).slice(0, 2)
    const pairs = []
    if (selectedMode === 'actors') {
      for (let first = 0; first < actors.length; first += 1) for (let second = first + 1; second < actors.length; second += 1) pairs.push([actors[first], actors[second]])
      actors.forEach((name) => category.set(name, 0))
    } else {
      for (const director of directors) for (const actor of actors) pairs.push([director, actor])
      directors.forEach((name) => category.set(name, 0)); actors.forEach((name) => category.set(name, 1))
    }
    for (const [source, target] of pairs) {
      const key = [source, target].sort().join('\u0000')
      const edge = edgeMap.get(key) || { source, target, value: 0 }
      edge.value += 1; edgeMap.set(key, edge)
    }
  }
  const degree = new Map()
  for (const edge of edgeMap.values()) { degree.set(edge.source, (degree.get(edge.source) || 0) + edge.value); degree.set(edge.target, (degree.get(edge.target) || 0) + edge.value) }
  const keep = new Set([...degree.entries()].sort((a, b) => b[1] - a[1]).slice(0, 28).map(([name]) => name))
  const links = [...edgeMap.values()].filter((edge) => keep.has(edge.source) && keep.has(edge.target))
  const connected = new Set(links.flatMap((edge) => [edge.source, edge.target]))
  const nodes = [...connected].map((name) => ({ name, value: degree.get(name), category: category.get(name) || 0, symbolSize: Math.min(42, 12 + Math.sqrt(degree.get(name)) * 5) }))
  return { nodes, links }
}
const graph = computed(() => createGraph(mode.value))
const option = computed(() => ({
  tooltip: { formatter: (p) => p.dataType === 'edge' ? `${p.data.source} → ${p.data.target}<br/>合作 ${p.data.value} 次` : `${p.name}<br/>关系权重 ${p.value}` },
  legend: { bottom: 4, data: mode.value === 'actors' ? ['演员'] : ['导演', '演员'], textStyle: { color: '#94a3b8' } },
  series: [{ type: 'graph', layout: 'force', roam: true, draggable: true, data: graph.value.nodes, links: graph.value.links, categories: mode.value === 'actors' ? [{ name: '演员', itemStyle: { color: '#38bdf8' } }] : [{ name: '导演', itemStyle: { color: '#f59e0b' } }, { name: '演员', itemStyle: { color: '#38bdf8' } }], label: { show: true, color: '#cbd5e1', fontSize: 11, formatter: '{b}' }, labelLayout: { hideOverlap: true }, force: { initLayout: 'circular', repulsion: 520, edgeLength: [80, 170], gravity: .08, friction: .7 }, lineStyle: { color: 'source', opacity: .5, curveness: .12 }, emphasis: { focus: 'adjacency', lineStyle: { width: 3, opacity: 1 } } }],
}))
function openPerson(params) { if (params?.dataType === 'node' && params.name) router.push({ path: '/search', query: { q: params.name } }) }
async function load() {
  loading.value = true; error.value = ''
  try { const response = await api.paged({ page: 1, size: 100, sort: 'rating_count', order: 'desc' }); movies.value = response?.items || []; if (!movies.value.length) throw new Error('没有关系网络数据') }
  catch (exception) { error.value = exception?.message || String(exception) } finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.tab-bar { display: flex; border: 1px solid var(--c-border); border-radius: var(--r-sm); overflow: hidden; }
.tab-bar button { padding: 6px 13px; border: 0; color: var(--c-muted); background: transparent; cursor: pointer; }
.tab-bar button + button { border-left: 1px solid var(--c-border); }
.tab-bar button.active { color: var(--c-primary); background: var(--c-primary-tint); }
</style>