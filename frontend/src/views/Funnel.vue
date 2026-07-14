<template>
  <PageScaffold
    title="评分漏斗"
    subtitle="按评分段分层,看头部精品的留存率"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <span class="muted">基于 {{ summaryExt?.total ?? 0 }} 部影片</span>
    </template>

    <div class="funnel-grid">
      <UiChartCard title="评分漏斗" sub="全部 → 7+ → 8+ → 9+" class="fade-up">
        <EChart :option="funnelOption" height="460px" />
      </UiChartCard>

      <UiChartCard title="漏斗转化" class="fade-up-stagger" style="--i: 1">
        <ul class="funnel-list">
          <li
            v-for="(b, i) in buckets"
            :key="b.key"
            class="funnel-list__row fade-up"
            :style="{ animationDelay: (i * 60) + 'ms' }"
            @click="drill('ratingBucket', b.label)"
          >
            <span class="funnel-list__dot" :style="{ background: COLORS[i] }"></span>
            <span class="funnel-list__name">{{ b.label || '-' }}</span>
            <span class="funnel-list__count">{{ b.count || '-' }} 部</span>
            <span class="funnel-list__rate">{{ rateOf(i) }}%</span>
          </li>
        </ul>
        <div class="funnel-summary">
          <div class="funnel-summary__cell">
            <span class="muted">7+ 占比</span>
            <span class="funnel-summary__num">{{ rateOf(1) }}%</span>
          </div>
          <div class="funnel-summary__cell">
            <span class="muted">8+ 留存</span>
            <span class="funnel-summary__num">{{ rateOf(2) }}%</span>
          </div>
          <div class="funnel-summary__cell">
            <span class="muted">头部(9+)总量</span>
            <span class="funnel-summary__num">{{ buckets[3]?.count || 0 }}</span>
          </div>
        </div>
      </UiChartCard>
    </div>
  </PageScaffold>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PageScaffold from '../components/PageScaffold.vue'
import EChart from '../components/EChart.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import { buildFunnelOption } from '../echarts/options'
import { useDrillNav } from '../composables/useDrillNav'
import { useDashboardStore } from '../stores/dashboard'

const { go: drill } = useDrillNav()
const store = useDashboardStore()
const loading = ref(false)
const error = ref('')

const COLORS = ['#38bdf8', '#22d3ee', '#a78bfa', '#f472b6', '#fb923c']
const BUCKETS = [
  { key: '9+',   label: '9 分以上', min: 9,    max: 11 },
  { key: '8-9',  label: '8-9 分',   min: 8,    max: 9 },
  { key: '7-8',  label: '7-8 分',   min: 7,    max: 8 },
  { key: '<7',   label: '7 分以下', min: 0,    max: 7 },
]

const ratingDist = computed(() => store.ratingDist || [])
const total = computed(() => ratingDist.value.reduce((s, d) => s + (d.count || 0), 0))

const buckets = computed(() => {
  const dist = ratingDist.value
  const distMap = new Map(dist.map((d) => [d.bucket, d.count || 0]))
  
  const score9 = distMap.get('9以上') || 0
  const score8 = distMap.get('8-9') || 0
  const score7 = distMap.get('7-8') || 0
  const score6 = distMap.get('6以下') || 0
  
  return [
    { key: 'all', label: '全部影片', count: total.value },
    { key: '7+', label: '7 分以上', count: score7 + score8 + score9 },
    { key: '8+', label: '8 分以上', count: score8 + score9 },
    { key: '9+', label: '9 分以上', count: score9 },
  ]
})

const funnelOption = computed(() => buildFunnelOption(buckets.value.map((b) => ({ name: b.label, value: b.count }))))

function rateOf(i) {
  const cur = buckets.value[i]?.count || 0
  if (i === 0) return 100
  const prev = buckets.value[i - 1]?.count || 0
  return prev ? Math.round((cur / prev) * 100) : 0
}

const summaryExt = computed(() => store.summaryExt || {})

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (!store.ratingDist?.length) await store.loadAll()
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.funnel-grid { display: grid; grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr); gap: 14px; }
@media (max-width: 1000px) { .funnel-grid { grid-template-columns: 1fr; } }

.funnel-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.funnel-list__row {
  display: grid; grid-template-columns: 14px 1fr auto 60px;
  align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: var(--r-sm); cursor: pointer;
  background: var(--c-surface-2);
  transition: background var(--t-fast) var(--ease-out);
}
.funnel-list__row:hover { background: var(--c-primary-tint); }
.funnel-list__dot { width: 12px; height: 12px; border-radius: 50%; }
.funnel-list__name { color: var(--c-text); font-weight: 500; }
.funnel-list__count { color: var(--c-muted); font-size: var(--fs-sm); font-variant-numeric: tabular-nums; }
.funnel-list__rate { color: var(--c-primary); font-weight: 700; text-align: right; font-variant-numeric: tabular-nums; }

.funnel-summary {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
  margin-top: 14px; padding: 12px 14px;
  background: var(--c-surface-2); border-radius: var(--r-sm);
  border: 1px solid var(--c-border);
}
.funnel-summary__cell { display: flex; flex-direction: column; gap: 4px; align-items: center; }
.funnel-summary__num { color: var(--c-text); font-weight: 700; font-size: var(--fs-xl); font-variant-numeric: tabular-nums; }
</style>
