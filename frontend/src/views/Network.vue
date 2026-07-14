<template>
  <div class="net">
    <header class="page-head fade-up">
      <div>
        <h1 class="page-title">合作网络</h1>
        <p class="page-sub">共同参演 / 共同导演电影数 ≥ 1 的人构成节点,边权 = 合作影片数。</p>
      </div>
      <div class="net__controls">
        <UiButton size="sm" :variant="type==='director' ? 'primary' : 'ghost'" @click="setType('director')">按导演</UiButton>
        <UiButton size="sm" :variant="type==='actor' ? 'primary' : 'ghost'" @click="setType('actor')">按演员</UiButton>
        <UiButton size="sm" :variant="type==='both' ? 'primary' : 'ghost'" @click="setType('both')">全部</UiButton>
      </div>
    </header>

    <UiChartCard :loading="loading" :error="error" title="合作图谱" :sub="subTitle" class="fade-up" @retry="load">
      <EChart :option="option" height="640px" v-if="hasData" :key="type" />
      <UiEmptyState v-else title="暂无网络数据" desc="字段 director / actors 缺失或无法解析" />
    </UiChartCard>

    <UiChartCard v-if="topPeople.length" title="核心节点 TOP 15" sub="作品数最多" class="fade-up-stagger" style="--i: 1">
      <ul class="top-list">
        <li v-for="(p, i) in topPeople" :key="p.name" class="top-list__row fade-up" :style="{ animationDelay: (i * 30) + 'ms' }">
          <span class="top-list__rank">{{ i + 1 }}</span>
          <span class="top-list__name">{{ p.name || '-' }}</span>
          <span class="top-list__count">{{ p.value || '-' }} 部</span>
        </li>
      </ul>
    </UiChartCard>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import EChart from '../components/EChart.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import UiButton from '../components/ui/UiButton.vue'
import UiEmptyState from '../components/ui/UiEmptyState.vue'
import { api } from '../api'
import { buildGraphOption } from '../echarts/options'

const loading = ref(false)
const error = ref('')
const type = ref('director')
const data = ref({ nodes: [], links: [] })

const subTitle = computed(() => {
  if (type.value === 'director') return '按导演构建合作网络'
  if (type.value === 'actor') return '按主演构建合作网络'
  return '导演 + 主演统一构建'
})

const hasData = computed(() => (data.value.nodes?.length || 0) > 0)
const option = computed(() => buildGraphOption(data.value))
const topPeople = computed(() =>
  [...(data.value.nodes || [])]
    .sort((a, b) => (b.value || 0) - (a.value || 0))
    .slice(0, 15)
)

function setType(t) {
  if (t === type.value) return
  type.value = t
  load()
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    data.value = (await api.networkCollaborations(type.value, 60)) || { nodes: [], links: [] }
  } catch (e) {
    error.value = e?.response?.data?.message || e?.message || String(e)
    data.value = { nodes: [], links: [] }
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.net { display: flex; flex-direction: column; gap: 14px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px; }
.page-title { margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }
.page-sub { margin: 4px 0 0; color: var(--c-muted); font-size: 13px; }

.net__controls { display: inline-flex; gap: 6px; }

.top-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
.top-list__row {
  display: grid; grid-template-columns: 28px 1fr auto;
  align-items: center; gap: 12px;
  padding: 6px 12px; border-radius: var(--r-sm);
  background: var(--c-surface-2);
  opacity: 0; transform: translateY(4px);
  animation: fadeUp .35s var(--ease-out) both;
}
.top-list__rank { color: var(--c-muted); font-variant-numeric: tabular-nums; text-align: center; }
.top-list__name { color: var(--c-text); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.top-list__count { color: var(--c-primary); font-weight: 700; font-variant-numeric: tabular-nums; }
</style>