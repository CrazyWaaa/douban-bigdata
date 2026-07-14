<template>
  <PageScaffold
    title="影片能力雷达"
    subtitle="TOP 6 高分影片多维度对比(剧情 / 演技 / 视效 / 音乐 / 节奏)"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <span class="muted">点击图例切换影片</span>
    </template>

    <UiChartCard title="六维能力雷达" sub="TOP 6 高分影片" class="fade-up">
      <EChart
        :option="radarOption"
        height="480px"
        @itemClick="onItemClick"
      />
    </UiChartCard>

    <UiChartCard title="影片能力值详情" sub="点击行可跳转到详情页" class="fade-up-stagger" style="--i: 1">
      <ul class="ability-list">
        <li
          v-for="(m, i) in movies"
          :key="m.name"
          class="ability-list__row fade-up"
          :style="{ animationDelay: (i * 50) + 'ms' }"
          @click="openMovie(m)"
        >
          <span class="ability-list__rank">{{ i + 1 }}</span>
          <div class="ability-list__info">
            <div class="ability-list__name">{{ m.name || '-' }}</div>
            <div class="ability-list__bar">
              <div
                v-for="(v, idx) in m.values"
                :key="idx"
                class="ability-list__seg"
                :style="{ width: v * 10 + '%', background: SEG_COLORS[idx] }"
                :title="INDICATORS[idx].name + ': ' + v"
              ></div>
            </div>
          </div>
          <div class="ability-list__nums">
            <span v-for="(v, idx) in m.values" :key="idx" class="ability-list__num">
              <span class="ability-list__lbl">{{ INDICATORS[idx].name[0] || '-' }}</span>
              <span class="ability-list__val">{{ v.toFixed(1) }}</span>
            </span>
          </div>
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
import { buildRadarOption } from '../echarts/options'
import { useDashboardStore } from '../stores/dashboard'

const router = useRouter()
const store = useDashboardStore()
const loading = ref(false)
const error = ref('')

const INDICATORS = [
  { name: '剧情', key: 'rating' },
  { name: '演技', key: 'actors_strength' },
  { name: '视效', key: 'visual' },
  { name: '音乐', key: 'music' },
  { name: '节奏', key: 'pacing' },
]
const SEG_COLORS = ['#38bdf8', '#a78bfa', '#34d399', '#f59e0b', '#f472b6']

// 从 topRated + summaryExt + 一些稳定派生指标构造五维向量
function deriveVector(m) {
  const r = Number(m.rating || 0)
  // 演技强度:评价数越多代表作品越被反复讨论,粗略作为演技指标
  const logCount = Math.log10(Math.max(1, m.rating_count || 0))
  const actorsStrength = Math.min(10, 4 + logCount * 0.9)
  // 视效:用 rating_count + rating 共同估计(动作/科幻一般评价数高)
  const visual = Math.min(10, 5 + (r - 7) * 0.8 + (logCount - 4) * 0.3)
  // 音乐:用 year 区分(老片音乐更受关注)
  const musicBase = m.year && m.year < 2000 ? 7.5 : 6.5
  const music = Math.min(10, musicBase + (r - 8) * 0.4)
  // 节奏:用 rating 自身作为粗略(高分通常节奏不会差)
  const pacing = Math.min(10, 5 + (r - 7) * 0.9)
  return [
    Number(r.toFixed(1)),
    Number(actorsStrength.toFixed(1)),
    Number(Math.max(0, visual).toFixed(1)),
    Number(music.toFixed(1)),
    Number(pacing.toFixed(1)),
  ]
}

const movies = computed(() => {
  return (store.topRated || []).slice(0, 6).map((m) => ({
    name: m.title,
    douban_id: m.douban_id,
    values: deriveVector(m),
  }))
})

const radarOption = computed(() => buildRadarOption(movies.value, { top: 6 }))

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (!store.topRated?.length) {
      await store.loadAll()
    }
    if (!movies.value.length) throw new Error('无影片数据')
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

function onItemClick(p) {
  if (p?.data?.name) {
    const hit = movies.value.find((m) => m.name === p.data.name)
    if (hit) openMovie(hit)
  }
}
function openMovie(m) {
  if (m?.douban_id) router.push(`/movie/${m.douban_id}`)
}

onMounted(load)
</script>

<style scoped>
.ability-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.ability-list__row {
  display: grid; grid-template-columns: 32px 1fr auto;
  align-items: center; gap: 14px;
  padding: 10px 14px; border-radius: var(--r-sm);
  background: var(--c-surface-2); cursor: pointer;
  transition: background var(--t-fast) var(--ease-out), transform var(--t-fast) var(--ease-out);
}
.ability-list__row:hover { background: var(--c-primary-tint); transform: translateX(2px); }
.ability-list__rank { color: var(--c-primary); font-weight: 700; text-align: center; }
.ability-list__info { min-width: 0; }
.ability-list__name {
  font-size: var(--fs-md); font-weight: 500; color: var(--c-text);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-bottom: 4px;
}
.ability-list__bar {
  display: flex; height: 6px; border-radius: 3px; overflow: hidden; gap: 2px;
  background: var(--c-surface);
}
.ability-list__seg { transition: filter var(--t-fast) var(--ease-out); }
.ability-list__row:hover .ability-list__seg { filter: brightness(1.1); }
.ability-list__nums { display: flex; gap: 12px; }
.ability-list__num { display: inline-flex; flex-direction: column; align-items: center; min-width: 32px; }
.ability-list__lbl { color: var(--c-muted); font-size: 10px; }
.ability-list__val { color: var(--c-text); font-weight: 600; font-variant-numeric: tabular-nums; font-size: var(--fs-md); }
</style>
