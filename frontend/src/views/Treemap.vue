<template>
  <PageScaffold
    title="类型×地区 矩阵"
    subtitle="嵌套方块 = 影片数,点击方块可跳转到对应维度页"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <span class="muted">合计 {{ totalCount }} 部影片 · {{ treemapData.length }} 个类型</span>
    </template>

    <div class="treemap-layout">
      <UiChartCard title="类型 × 地区 嵌套树" sub="hover 高亮,click 钻取" class="fade-up">
        <EChart
          :option="treemapOption"
          height="560px"
          @itemClick="onItemClick"
        />
      </UiChartCard>

      <UiChartCard title="类型 TOP 10 详情" class="fade-up" style="animation-delay: 80ms">
        <ul class="treemap-list">
          <li
            v-for="(g, i) in topGenres"
            :key="g.name"
            class="treemap-list__row fade-up"
            :style="{ animationDelay: (i * 40) + 'ms' }"
            @click="goGenre(g.name)"
          >
            <span class="treemap-list__rank">{{ i + 1 }}</span>
            <div class="treemap-list__bar">
              <div
                class="treemap-list__fill"
                :style="{ width: pctOf(g.count) + '%', background: barColor(i) }"
              ></div>
            </div>
            <span class="treemap-list__name">{{ g.name }}</span>
            <span class="treemap-list__count">{{ g.count }} 部</span>
          </li>
        </ul>
      </UiChartCard>
    </div>
  </PageScaffold>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PageScaffold from '../components/PageScaffold.vue'
import EChart from '../components/EChart.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import { api } from '../api'
import { buildTreemapOption } from '../echarts/options'
import { useDrillNav } from '../composables/useDrillNav'

const { go: drill } = useDrillNav()
const loading = ref(false)
const error = ref('')

const topGenres = ref([])
const countryOfGenre = ref(new Map()) // genre -> { country: count }

const treemapData = computed(() => {
  return topGenres.value.map((g) => {
    const cMap = countryOfGenre.value.get(g.name) || new Map()
    const children = [...cMap.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([name, value]) => ({ name, value }))
    return { name: g.name, value: g.count, children }
  })
})

const totalCount = computed(() => topGenres.value.reduce((s, g) => s + (g.count || 0), 0))
const maxCount = computed(() => Math.max(1, ...topGenres.value.map((g) => g.count || 0)))

const treemapOption = computed(() => buildTreemapOption(treemapData.value))

function pctOf(n) { return Math.max(2, (n / maxCount.value) * 100) }
function barColor(i) {
  const palette = ['#38bdf8', '#a78bfa', '#f59e0b', '#34d399', '#f472b6', '#22d3ee', '#fb923c', '#a3e635', '#60a5fa', '#fb7185']
  return palette[i % palette.length]
}

function onItemClick(p) {
  if (!p?.data?.name) return
  // 数据节点:顶层 name=类型,二级 name=地区
  if (p.treePathInfo?.length >= 2) {
    // 二级(地区)
    const country = p.data.name
    const genre = p.treePathInfo[0]?.name
    drill('country', country, { from: genre })
  } else {
    drill('genre', p.data.name)
  }
}
function goGenre(name) { drill('genre', name) }

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [genreList, countryList, detailList] = await Promise.allSettled([
      api.byGenre(),
      api.byCountry(),
      api.paged({ page: 1, size: 100, sort: 'rating', order: 'desc' }),
    ])
    const genres = genreList.status === 'fulfilled' ? (genreList.value?.data || []) : []
    const countries = countryList.status === 'fulfilled' ? (countryList.value?.data || []) : []
    const movies = detailList.status === 'fulfilled' ? (detailList.value?.data || []) : []
    topGenres.value = genres.slice(0, 10)

    // 用 topRated 详情聚合 type × country
    const tmp = new Map()
    for (const m of movies) {
      const gs = String(m.genre || '').split('/').map((s) => s.trim()).filter(Boolean)
      const cs = String(m.country || '').split('/').map((s) => s.trim()).filter(Boolean)
      for (const g of gs) {
        if (!tmp.has(g)) tmp.set(g, new Map())
        for (const c of cs) {
          const cm = tmp.get(g)
          cm.set(c, (cm.get(c) || 0) + 1)
        }
      }
    }
    countryOfGenre.value = tmp
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.treemap-layout {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr);
  gap: 14px;
}
@media (max-width: 1000px) { .treemap-layout { grid-template-columns: 1fr; } }

.treemap-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.treemap-list__row {
  display: grid; grid-template-columns: 24px 1fr auto auto;
  align-items: center; gap: 10px;
  padding: 6px 10px; border-radius: var(--r-sm);
  cursor: pointer; transition: background var(--t-fast) var(--ease-out);
}
.treemap-list__row:hover { background: var(--c-primary-tint); }
.treemap-list__rank { color: var(--c-muted); font-weight: 700; text-align: center; font-size: var(--fs-sm); }
.treemap-list__bar { height: 8px; border-radius: 4px; background: var(--c-surface-2); overflow: hidden; }
.treemap-list__fill { height: 100%; transition: filter var(--t-fast) var(--ease-out); }
.treemap-list__row:hover .treemap-list__fill { filter: brightness(1.15); }
.treemap-list__name { color: var(--c-text); font-weight: 500; font-size: var(--fs-sm); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.treemap-list__count { color: var(--c-muted); font-size: var(--fs-xs); font-variant-numeric: tabular-nums; min-width: 40px; text-align: right; }
</style>
