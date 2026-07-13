<template>
  <PageScaffold
    title="3D 散点矩阵"
    subtitle="评分 × 评价数(对数) × 年代 · 拖拽旋转,点击跳详情"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <span class="muted">蓝色=高分,红色=低分 · 球大小 ∝ 评价数</span>
    </template>

    <UiChartCard title="3D 散点" sub="可拖拽旋转视角" class="fade-up">
      <EChart
        :option="scatterOption"
        height="600px"
        @chartReady="onChartReady"
        @itemClick="onItemClick"
      />
    </UiChartCard>

    <UiChartCard title="TOP 10 评分" sub="点击行也可跳详情" class="fade-up" style="animation-delay: 80ms">
      <ul class="scatter-list">
        <li
          v-for="(m, i) in topList"
          :key="m.douban_id || m.name"
          class="scatter-list__row fade-up"
          :style="{ animationDelay: (i * 30) + 'ms' }"
          @click="goMovie(m)"
        >
          <span class="scatter-list__rank">{{ i + 1 }}</span>
          <span class="scatter-list__name">{{ m.name }}</span>
          <span class="scatter-list__year">{{ m.year || '-' }}</span>
          <span class="scatter-list__rating">{{ Number(m.rating).toFixed(1) }}</span>
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
import { buildScatter3DOption } from '../echarts/options'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const items = ref([])
let chartInstance = null

const scatterItems = computed(() =>
  items.value.map((m) => ({
    name: m.title,
    value: [
      Number(m.rating || 0),
      Math.log10(Math.max(1, m.rating_count || 0)),
      Number(m.year || 0),
    ],
    douban_id: m.douban_id,
  })),
)

const scatterOption = computed(() => buildScatter3DOption(scatterItems.value))
const topList = computed(() => items.value.slice(0, 10))

function onChartReady(chart) { chartInstance = chart }
function goMovie(m) { if (m?.douban_id) router.push(`/movie/${m.douban_id}`) }

function onItemClick(p) {
  const doubanId = p?.data?.douban_id
  if (doubanId) goMovie({ douban_id: doubanId })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.paged({ page: 1, size: 250, sort: 'rating', order: 'desc' })
    items.value = (res?.data || []).filter((m) => m.rating != null && m.year != null)
    if (!items.value.length) throw new Error('后端未返回影片数据')
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.scatter-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }
.scatter-list__row {
  display: grid; grid-template-columns: 28px 1fr 60px 60px;
  align-items: center; gap: 10px;
  padding: 8px 12px; border-radius: var(--r-sm); cursor: pointer;
  background: var(--c-surface-2);
  transition: background var(--t-fast) var(--ease-out), transform var(--t-fast) var(--ease-out);
}
.scatter-list__row:hover { background: var(--c-primary-tint); transform: translateX(2px); }
.scatter-list__rank { color: var(--c-muted); font-weight: 700; text-align: center; font-size: var(--fs-sm); }
.scatter-list__name { color: var(--c-text); font-weight: 500; font-size: var(--fs-md); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.scatter-list__year { color: var(--c-muted); font-size: var(--fs-sm); text-align: right; }
.scatter-list__rating { color: var(--c-primary); font-weight: 700; font-size: var(--fs-md); text-align: right; font-variant-numeric: tabular-nums; }
</style>
