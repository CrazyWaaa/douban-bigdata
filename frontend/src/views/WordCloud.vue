<template>
  <PageScaffold title="词云分析" subtitle="类型、导演与演员出现频次" :loading="loading" :error="error" @retry="load">
    <template #actions>
      <div class="tab-bar">
        <button v-for="tab in tabs" :key="tab.key" :class="['tab-bar__btn', { 'is-active': active === tab.key }]" @click="active = tab.key">
          {{ tab.label || '-' }}
        </button>
      </div>
    </template>

    <UiChartCard :title="`${currentTab.label}词云`" :sub="`${currentList.length} 个关键词，点击可筛选`" class="fade-up">
      <div class="word-cloud" role="list" :aria-label="`${currentTab.label}词云`">
        <button
          v-for="(word, index) in currentList"
          :key="word.name"
          class="word-cloud__item"
          :style="wordStyle(word, index)"
          :title="`${word.name}：${word.value} 次`"
          role="listitem"
          @click="openWord(word.name)"
        >{{ word.name || '-' }}</button>
      </div>
    </UiChartCard>

    <UiChartCard :title="`${currentTab.label} TOP 12`" class="fade-up">
      <ul class="cloud-list">
        <li v-for="(item, index) in topList" :key="item.name" class="cloud-list__row" @click="openWord(item.name)">
          <span class="cloud-list__rank">{{ index + 1 }}</span>
          <span class="cloud-list__name">{{ item.name || '-' }}</span>
          <div class="cloud-list__bar"><div class="cloud-list__fill" :style="{ width: percent(item.value) + '%' }"></div></div>
          <span class="cloud-list__val">{{ item.value || '-' }}</span>
        </li>
      </ul>
    </UiChartCard>
  </PageScaffold>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageScaffold from '../components/PageScaffold.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import { api } from '../api'
import { useDrillNav } from '../composables/useDrillNav'
import { splitMultiValue, splitPeople } from '../utils/movieFields'

const { go: drill } = useDrillNav()
const tabs = [{ key: 'genre', label: '类型' }, { key: 'director', label: '导演' }, { key: 'actors', label: '演员' }]
const active = ref('genre')
const loading = ref(false)
const error = ref('')
const maps = ref({ genre: new Map(), director: new Map(), actors: new Map() })
const palette = ['#38bdf8', '#f59e0b', '#34d399', '#a78bfa', '#f472b6', '#22d3ee', '#fb923c']

const currentTab = computed(() => tabs.find((tab) => tab.key === active.value) || tabs[0])
const currentList = computed(() => [...maps.value[active.value].entries()].map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value).slice(0, 48))
const topList = computed(() => currentList.value.slice(0, 12))
const maxValue = computed(() => Math.max(1, ...currentList.value.map((item) => item.value)))
const minValue = computed(() => Math.min(...currentList.value.map((item) => item.value), maxValue.value))

function percent(value) { return Math.max(3, value / maxValue.value * 100) }
function wordStyle(word, index) {
  const ratio = (word.value - minValue.value) / Math.max(1, maxValue.value - minValue.value)
  return {
    '--word-color': palette[index % palette.length],
    '--word-size': `${14 + ratio * 32}px`,
    '--word-rotate': `${[-8, 0, 6, 0, -4][index % 5]}deg`,
    order: (index * 17) % 47,
  }
}
function openWord(name) {
  if (active.value === 'genre') drill('genre', name)
  else drill('director', name, active.value === 'actors' ? { target: '/top' } : undefined)
}
function add(map, terms) { for (const term of terms) map.set(term, (map.get(term) || 0) + 1) }

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.paged({ page: 1, size: 100, sort: 'rating', order: 'desc' })
    const next = { genre: new Map(), director: new Map(), actors: new Map() }
    for (const movie of response?.items || []) {
      add(next.genre, splitMultiValue(movie.genre))
      add(next.director, splitPeople(movie.director))
      add(next.actors, splitPeople(movie.actors).slice(0, 8))
    }
    maps.value = next
    if (!currentList.value.length) throw new Error('没有可用于词云的影片字段')
  } catch (exception) {
    error.value = exception?.message || String(exception)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.tab-bar { display: inline-flex; border: 1px solid var(--c-border); border-radius: var(--r-sm); overflow: hidden; }
.tab-bar__btn { padding: 5px 14px; border: 0; background: transparent; color: var(--c-muted); cursor: pointer; }
.tab-bar__btn + .tab-bar__btn { border-left: 1px solid var(--c-border); }
.tab-bar__btn.is-active { color: var(--c-primary); background: var(--c-primary-tint); }
.word-cloud { min-height: 480px; display: flex; flex-wrap: wrap; align-content: center; align-items: center; justify-content: center; gap: 10px 16px; padding: 32px; overflow: hidden; background: radial-gradient(circle, var(--c-primary-tint), transparent 65%); }
.word-cloud__item { color: var(--word-color); font-size: var(--word-size); transform: rotate(var(--word-rotate)); font-weight: 750; line-height: 1; border: 0; padding: 5px 7px; background: transparent; cursor: pointer; text-shadow: 0 2px 16px color-mix(in srgb, var(--word-color) 25%, transparent); transition: transform .18s ease, filter .18s ease; }
.word-cloud__item:hover { transform: rotate(0deg) scale(1.12); filter: brightness(1.2); }
.cloud-list { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px 16px; }
.cloud-list__row { display: grid; grid-template-columns: 28px minmax(80px, 140px) 1fr 32px; align-items: center; gap: 10px; padding: 8px 10px; border-radius: var(--r-sm); cursor: pointer; }
.cloud-list__row:hover { background: var(--c-primary-tint); }
.cloud-list__rank, .cloud-list__val { color: var(--c-muted); font-variant-numeric: tabular-nums; }
.cloud-list__name { color: var(--c-text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cloud-list__bar { height: 7px; overflow: hidden; border-radius: 4px; background: var(--c-surface-2); }
.cloud-list__fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--c-primary), var(--c-info)); }
@media (max-width: 720px) { .word-cloud { min-height: 380px; padding: 18px; } .cloud-list { grid-template-columns: 1fr; } }
</style>