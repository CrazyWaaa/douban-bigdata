<template>
  <PageScaffold
    title="词云三连"
    subtitle="类型 / 导演 / 演员 出现频次,点击词语跳转维度页"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <div class="tab-bar">
        <button
          v-for="t in tabs"
          :key="t.key"
          :class="['tab-bar__btn', { 'is-active': active === t.key }]"
          @click="active = t.key"
        >{{ t.label }}</button>
      </div>
    </template>

    <UiChartCard :title="`${currentTab.label} 词云`" :sub="`基于 ${itemCount} 个项目`" class="fade-up">
      <EChart
        :option="wordOption"
        height="520px"
        @itemClick="onItemClick"
      />
    </UiChartCard>

    <UiChartCard :title="`${currentTab.label} TOP 12`" class="fade-up" style="animation-delay: 80ms">
      <ul class="cloud-list">
        <li
          v-for="(d, i) in topList"
          :key="d.name + i"
          class="cloud-list__row fade-up"
          :style="{ animationDelay: (i * 30) + 'ms' }"
          @click="onItemClick({ data: d })"
        >
          <span class="cloud-list__rank">{{ i + 1 }}</span>
          <span class="cloud-list__name">{{ d.name }}</span>
          <div class="cloud-list__bar">
            <div class="cloud-list__fill" :style="{ width: pctOf(d.value) + '%' }"></div>
          </div>
          <span class="cloud-list__val">{{ d.value }}</span>
        </li>
      </ul>
    </UiChartCard>
  </PageScaffold>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PageScaffold from '../components/PageScaffold.vue'
import EChart from '../components/EChart.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import { api } from '../api'
import { buildWordCloudOption } from '../echarts/options'
import { useDrillNav } from '../composables/useDrillNav'

const { go: drill } = useDrillNav()
const loading = ref(false)
const error = ref('')

const tabs = [
  { key: 'genre',    label: '类型' },
  { key: 'director', label: '导演' },
  { key: 'actors',   label: '演员' },
]
const active = ref('genre')

const genreMap    = ref(new Map())
const directorMap = ref(new Map())
const actorMap    = ref(new Map())

const currentTab = computed(() => tabs.find((t) => t.key === active.value) || tabs[0])
const currentMap = computed(() => {
  if (active.value === 'genre') return genreMap.value
  if (active.value === 'director') return directorMap.value
  return actorMap.value
})
const currentList = computed(() => {
  return [...currentMap.value.entries()]
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 60)
})
const topList = computed(() => currentList.value.slice(0, 12))
const itemCount = computed(() => currentList.value.length)
const maxVal = computed(() => Math.max(1, ...currentList.value.map((d) => d.value)))

const wordOption = computed(() => buildWordCloudOption(currentList.value))

function pctOf(v) { return Math.max(2, (v / maxVal.value) * 100) }

function onItemClick(p) {
  if (!p?.data?.name) return
  if (active.value === 'genre') drill('genre', p.data.name)
  else if (active.value === 'director') drill('director', p.data.name)
  else drill('director', p.data.name, { target: '/top' })
}

function splitTerms(s, sep = '/') {
  if (!s) return []
  return String(s).split(sep).map((t) => t.trim()).filter(Boolean)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.paged({ page: 1, size: 200, sort: 'rating', order: 'desc' })
    const list = res?.data || []
    const gM = new Map(), dM = new Map(), aM = new Map()
    for (const m of list) {
      for (const g of splitTerms(m.genre)) gM.set(g, (gM.get(g) || 0) + 1)
      for (const d of splitTerms(m.director)) dM.set(d, (dM.get(d) || 0) + 1)
      for (const a of splitTerms(m.actors, '/').slice(0, 6)) aM.set(a, (aM.get(a) || 0) + 1)
    }
    genreMap.value = gM
    directorMap.value = dM
    actorMap.value = aM
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

.cloud-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }
.cloud-list__row {
  display: grid; grid-template-columns: 28px 100px 1fr 60px;
  align-items: center; gap: 10px;
  padding: 6px 10px; border-radius: var(--r-sm); cursor: pointer;
  transition: background var(--t-fast) var(--ease-out);
}
.cloud-list__row:hover { background: var(--c-primary-tint); }
.cloud-list__rank { color: var(--c-muted); font-weight: 700; text-align: center; font-size: var(--fs-sm); }
.cloud-list__name { color: var(--c-text); font-weight: 500; font-size: var(--fs-sm); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cloud-list__bar { height: 6px; border-radius: 3px; background: var(--c-surface-2); overflow: hidden; }
.cloud-list__fill {
  height: 100%;
  background: linear-gradient(90deg, var(--c-primary), var(--c-info));
  transition: filter var(--t-fast) var(--ease-out);
}
.cloud-list__row:hover .cloud-list__fill { filter: brightness(1.2); }
.cloud-list__val { color: var(--c-primary); font-weight: 600; font-size: var(--fs-sm); text-align: right; font-variant-numeric: tabular-nums; }
</style>
