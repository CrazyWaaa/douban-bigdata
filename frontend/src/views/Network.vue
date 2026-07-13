<template>
  <PageScaffold
    title="演员 / 导演 合作网络"
    subtitle="力导向图,节点=演员或导演,边=合作次数,可拖拽节点"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <div class="tab-bar">
        <button :class="['tab-bar__btn', { 'is-active': mode === 'actors' }]" @click="mode = 'actors'">演员</button>
        <button :class="['tab-bar__btn', { 'is-active': mode === 'director' }]" @click="mode = 'director'">导演×演员</button>
      </div>
    </template>

    <UiChartCard
      :title="mode === 'actors' ? '演员合作网络' : '导演 × 主演 网络'"
      :sub="`${nodeCount} 节点 · ${linkCount} 条合作链路`"
      class="fade-up"
    >
      <EChart
        :option="graphOption"
        height="620px"
        @itemClick="onItemClick"
      />
    </UiChartCard>

    <UiChartCard title="TOP 10 出度节点" sub="参与合作最多" class="fade-up" style="animation-delay: 80ms">
      <ul class="net-list">
        <li
          v-for="(n, i) in topNodes"
          :key="n.name"
          class="net-list__row fade-up"
          :style="{ animationDelay: (i * 30) + 'ms' }"
          @click="onItemClick({ data: n })"
        >
          <span class="net-list__rank">{{ i + 1 }}</span>
          <span class="net-list__name">{{ n.name }}</span>
          <span class="net-list__val">{{ n.value }} 次合作</span>
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
import { buildGraphOption } from '../echarts/options'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const mode = ref('actors')

const actorMap = ref(new Map())    // name -> { name, value, category, links: {other: count} }
const directorMap = ref(new Map()) // name -> { name, value, category, links: {other: count} }

function ensureNode(map, name, category) {
  if (!map.has(name)) map.set(name, { name, value: 0, category, links: new Map() })
  return map.get(name)
}

function splitTerms(s) {
  if (!s) return []
  return String(s).split('/').map((t) => t.trim()).filter(Boolean)
}

function buildGraphData(map, topN) {
  const arr = [...map.values()].sort((a, b) => b.value - a.value).slice(0, topN)
  // 同时把 topN 内有连接的节点之间建边
  const nameSet = new Set(arr.map((n) => n.name))
  const nodes = arr.map((n) => ({
    name: n.name,
    value: n.value,
    symbolSize: Math.max(10, Math.min(40, 8 + n.value * 1.5)),
    category: n.category,
  }))
  const links = []
  for (const a of arr) {
    for (const [b, v] of a.links) {
      if (nameSet.has(b) && a.name < b) {
        links.push({ source: a.name, target: b, value: v })
      }
    }
  }
  return { nodes, links }
}

const graphData = computed(() => {
  const m = mode.value === 'actors' ? actorMap.value : directorMap.value
  return buildGraphData(m, mode.value === 'actors' ? 25 : 20)
})
const graphOption = computed(() => {
  const cats = [...new Set(graphData.value.nodes.map((n) => n.category))]
  return buildGraphOption(graphData.value, { categories: cats.map((c) => ({ name: c })) })
})
const nodeCount = computed(() => graphData.value.nodes.length)
const linkCount = computed(() => graphData.value.links.length)
const topNodes = computed(() => {
  return [...graphData.value.nodes].sort((a, b) => b.value - a.value).slice(0, 10)
})

function onItemClick(p) {
  if (!p?.data?.name) return
  if (mode.value === 'actors') {
    router.push({ path: '/top', query: { dim: 'director', v: p.data.name, q: p.data.name } })
  } else {
    router.push({ path: '/top', query: { dim: 'director', v: p.data.name } })
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.paged({ page: 1, size: 250, sort: 'rating', order: 'desc' })
    const list = res?.data || []
    const aM = new Map()
    const dM = new Map()
    for (const m of list) {
      const actors = splitTerms(m.actors).slice(0, 6)
      const directors = splitTerms(m.director)
      // 演员合作网络:同一影片的所有主演两两相连
      for (let i = 0; i < actors.length; i++) {
        for (let j = i + 1; j < actors.length; j++) {
          const a = ensureNode(aM, actors[i], '演员')
          const b = ensureNode(aM, actors[j], '演员')
          a.value++
          b.value++
          a.links.set(b.name, (a.links.get(b.name) || 0) + 1)
          b.links.set(a.name, (b.links.get(a.name) || 0) + 1)
        }
      }
      // 导演×演员网络
      for (const d of directors) {
        const dn = ensureNode(dM, d, '导演')
        for (const a of actors) {
          const an = ensureNode(dM, a, '主演')
          dn.value++
          an.value++
          dn.links.set(an.name, (dn.links.get(an.name) || 0) + 1)
          an.links.set(dn.name, (an.links.get(dn.name) || 0) + 1)
        }
      }
    }
    actorMap.value = aM
    directorMap.value = dM
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.tab-bar { display: inline-flex; border: 1px solid var(--c-border); border-radius: var(--r-sm); overflow: hidden; }
.tab-bar__btn {
  padding: 4px 14px; font-size: var(--fs-sm); background: transparent;
  color: var(--c-muted); border: 0; cursor: pointer;
  transition: background var(--t-fast) var(--ease-out), color var(--t-fast) var(--ease-out);
}
.tab-bar__btn + .tab-bar__btn { border-left: 1px solid var(--c-border); }
.tab-bar__btn:hover { color: var(--c-text); background: var(--c-primary-tint); }
.tab-bar__btn.is-active { background: var(--c-primary-tint); color: var(--c-primary); }

.net-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }
.net-list__row {
  display: grid; grid-template-columns: 32px 1fr auto;
  align-items: center; gap: 10px;
  padding: 8px 14px; border-radius: var(--r-sm); cursor: pointer;
  background: var(--c-surface-2);
  transition: background var(--t-fast) var(--ease-out);
}
.net-list__row:hover { background: var(--c-primary-tint); }
.net-list__rank { color: var(--c-primary); font-weight: 700; text-align: center; }
.net-list__name { color: var(--c-text); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.net-list__val { color: var(--c-muted); font-size: var(--fs-sm); font-variant-numeric: tabular-nums; }
</style>
