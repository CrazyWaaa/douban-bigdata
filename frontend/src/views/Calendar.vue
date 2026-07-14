<template>
  <div class="cal">
    <header class="page-head fade-up">
      <div>
        <h1 class="page-title">发行日历 · 热力</h1>
        <p class="page-sub">按片单 release_date 解析到月,越深色越多片。可切换年份。</p>
      </div>
      <div class="cal__controls">
        <UiButton size="sm" variant="ghost" @click="prev">← 上年</UiButton>
        <span class="cal__year">{{ year || '-' }}</span>
        <UiButton size="sm" variant="ghost" @click="next">下年 →</UiButton>
      </div>
    </header>

    <UiChartCard :loading="loading" :error="error" title="年度发行热力" sub="每年一张热力图" class="fade-up" @retry="load">
      <EChart :option="option" height="320px" v-if="hasData" :key="year" />
      <UiEmptyState v-else title="这一年没有数据" :desc="`${year} 年没有可解析的 release_date`" />
    </UiChartCard>

    <div v-if="monthlyStats.length" class="cal__months fade-up-stagger" style="--i: 1">
      <div class="cal__month-grid">
        <div
          v-for="(m, i) in monthlyStats"
          :key="m.month"
          class="cal__month"
          :style="{ animationDelay: (i * 25) + 'ms' }"
        >
          <div class="cal__month-num">{{ m.month || '-' }}</div>
          <div class="cal__month-val">{{ m.count || '-' }}</div>
          <div class="cal__month-lbl muted">部</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Calendar.vue
 * - 数据:/api/calendar/monthly?year=YYYY
 * - 控件:上下年按钮
 * - 月度小卡片汇总
 */
import { ref, computed, watch, onMounted } from 'vue'
import EChart from '../components/EChart.vue'
import UiChartCard from '../components/ui/UiChartCard.vue'
import UiButton from '../components/ui/UiButton.vue'
import UiEmptyState from '../components/ui/UiEmptyState.vue'
import { api } from '../api'
import { buildCalendarOption } from '../echarts/options'

const loading = ref(false)
const error = ref('')
const year = ref(new Date().getFullYear())
const points = ref([])
const availableYears = ref([])

const hasData = computed(() => points.value.length > 0)

const option = computed(() => buildCalendarOption(points.value, year.value))

const monthlyStats = computed(() => {
  const buckets = new Array(12).fill(0)
  for (const p of points.value) {
    const mo = Number(String(p.date).slice(5, 7))
    if (mo >= 1 && mo <= 12) buckets[mo - 1] += Number(p.value || 0)
  }
  return buckets.map((c, i) => ({ month: i + 1, count: c })).filter((x) => x.count > 0)
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.calendarMonthly(year.value)
    if (res && typeof res === 'object') {
      if (Array.isArray(res.points)) {
        points.value = res.points.filter((p) => Number(String(p.date).slice(0, 4)) === year.value)
      } else {
        points.value = []
      }
      if (Array.isArray(res.years) && res.years.length) {
        availableYears.value = res.years
        if (!res.years.includes(year.value)) {
          year.value = res.years[res.years.length - 1]
        }
      }
    } else {
      points.value = []
    }
  } catch (e) {
    error.value = e?.response?.data?.message || e?.message || String(e)
    points.value = []
  } finally {
    loading.value = false
  }
}

function prev() { year.value -= 1; load() }
function next() { year.value += 1; load() }

watch(year, load)

onMounted(load)
</script>

<style scoped>
.cal { display: flex; flex-direction: column; gap: 14px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px; }
.page-title { margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }
.page-sub { margin: 4px 0 0; color: var(--c-muted); font-size: 13px; }

.cal__controls {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 6px 10px; border: 1px solid var(--c-border); border-radius: var(--r-sm);
  background: var(--c-surface);
}
.cal__year {
  font-weight: 700; font-variant-numeric: tabular-nums;
  min-width: 64px; text-align: center;
}

.cal__months { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r); padding: 14px; }
.cal__month-grid {
  display: grid; grid-template-columns: repeat(12, 1fr); gap: 8px;
}
@media (max-width: 900px) {
  .cal__month-grid { grid-template-columns: repeat(6, 1fr); }
}
@media (max-width: 600px) {
  .cal__month-grid { grid-template-columns: repeat(3, 1fr); }
}
.cal__month {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 8px 4px;
  background: var(--c-surface-2);
  border-radius: var(--r-sm);
  opacity: 0; transform: translateY(4px);
  animation: fadeUp .35s var(--ease-out) both;
}
.cal__month-num { color: var(--c-muted); font-size: 11px; }
.cal__month-val {
  color: var(--c-primary); font-weight: 700; font-size: 18px;
  font-variant-numeric: tabular-nums;
}
.cal__month-lbl { font-size: 10px; }
</style>