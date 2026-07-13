<template>
  <PageScaffold
    title="年代日历"
    subtitle="按年份 × 月份 看影片分布热力,深色=密集"
    :loading="loading"
    :error="error"
    @retry="load"
  >
    <template #actions>
      <select v-model.number="year" class="year-select" @change="onYearChange">
        <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
      </select>
    </template>

    <UiChartCard :title="`${year} 年 · 月度热力`" :sub="`共 ${yearTotal} 部`" class="fade-up">
      <EChart :option="calendarOption" height="220px" />
    </UiChartCard>

    <UiChartCard title="年代汇总" sub="TOP 12 年代影片数" class="fade-up" style="animation-delay: 80ms">
      <EChart :option="barOption" height="320px" @itemClick="onBarClick" />
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
import { buildCalendarOption, buildAreaLineOption } from '../echarts/options'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const year = ref(2010)
const yearOptions = ref([])
const yearDist = ref([]) // [{name:year, count}]
const yearMonthData = ref([]) // [{date:'YYYY-MM-DD', value: count}]

const yearTotal = computed(() => yearMonthData.value.reduce((s, d) => s + (d.value || 0), 0))
const calendarOption = computed(() => buildCalendarOption(yearMonthData.value, year.value))
const barOption = computed(() => buildAreaLineOption(yearDist.value.slice(-12).map((d) => ({ name: d.name, value: d.count })), { color: '#a78bfa', label: '影片数' }))

function onBarClick(p) {
  if (p?.name) router.push({ path: '/year', query: { dim: 'year', v: String(p.name) } })
}

function onYearChange() {
  // 切换年份:重新聚合 month 数据
  loadMonthData()
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [yearRes, paged] = await Promise.allSettled([
      api.byYear(),
      api.paged({ page: 1, size: 250, sort: 'rating', order: 'desc' }),
    ])
    const yd = yearRes.status === 'fulfilled' ? (yearRes.value?.data || []) : []
    yearDist.value = yd
    yearOptions.value = yd.map((y) => Number(y.name)).filter((n) => n > 1900).sort((a, b) => b - a).slice(0, 30)
    if (yearOptions.value.length && !yearOptions.value.includes(year.value)) {
      year.value = yearOptions.value[Math.min(2, yearOptions.value.length - 1)] || year.value
    }
    const movies = paged.status === 'fulfilled' ? (paged.value?.data || []) : []
    const monthMap = new Map()
    for (const m of movies) {
      const y = Number(m.year)
      if (y !== year.value) continue
      // 没有具体月份信息,粗略按均匀分布到 12 月(避免引入额外字段)
      // 实际可改用 release_date 字段(若后端有),这里用兜底
      const md = String(m.release_date || '')
      const monthMatch = md.match(/-(\d{2})-/)
      const month = monthMatch ? Number(monthMatch[1]) : ((movies.indexOf(m) % 12) + 1)
      const d = `${y}-${String(month).padStart(2, '0')}-15`
      monthMap.set(d, (monthMap.get(d) || 0) + 1)
    }
    // 补全 12 个月,空月份=0
    const arr = []
    for (let m = 1; m <= 12; m++) {
      const key = `${year.value}-${String(m).padStart(2, '0')}-15`
      arr.push({ date: key, value: monthMap.get(key) || 0 })
    }
    yearMonthData.value = arr
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

function loadMonthData() {
  // 年份切换:重新拉一次(简化)
  load()
}

onMounted(load)
</script>

<style scoped>
.year-select {
  background: var(--c-surface); color: var(--c-text);
  border: 1px solid var(--c-border); border-radius: var(--r-sm);
  padding: 4px 10px; font-size: var(--fs-sm);
  transition: border-color var(--t-fast) var(--ease-out);
}
.year-select:focus { outline: none; border-color: var(--c-primary); }
</style>
