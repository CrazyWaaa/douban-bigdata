<template>
  <div>
    <div class="header">
      <h2>高分榜</h2>
      <div class="muted">共 {{ total }} 部</div>
    </div>

    <div class="filters card">
      <label>
        <span>排序</span>
        <select v-model="sort">
          <option value="rating">评分</option>
          <option value="rating_count">评价数</option>
          <option value="year">年份</option>
          <option value="title">片名</option>
        </select>
      </label>
      <label>
        <span>方向</span>
        <select v-model="order">
          <option value="desc">降序</option>
          <option value="asc">升序</option>
        </select>
      </label>
      <label>
        <span>类型</span>
        <input v-model="genre" placeholder="如 剧情" />
      </label>
      <label>
        <span>地区</span>
        <input v-model="country" placeholder="如 美国" />
      </label>
      <label>
        <span>年份起</span>
        <input v-model.number="yearFrom" type="number" placeholder="1990" />
      </label>
      <label>
        <span>年份止</span>
        <input v-model.number="yearTo" type="number" placeholder="2025" />
      </label>
      <button class="btn" @click="apply">应用</button>
      <button class="btn ghost" @click="reset">重置</button>
    </div>

    <div v-if="loading" class="muted">加载中…</div>
    <div v-else-if="!items.length" class="muted">没有符合条件的影片</div>
    <div v-else class="card" style="padding:0;">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width:60px;">#</th>
              <th>片名</th>
              <th style="width:140px;">导演</th>
              <th style="width:60px;">年份</th>
              <th style="width:80px;">类型</th>
              <th style="width:80px;">评分</th>
              <th style="width:100px;">评价数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(m, i) in items" :key="m.douban_id">
              <td class="rank">{{ (page - 1) * size + i + 1 }}</td>
              <td>
                <router-link :to="`/movie/${m.douban_id}`">{{ m.title }}</router-link>
                <div v-if="m.quote" class="quote">"{{ m.quote }}"</div>
              </td>
              <td class="muted-cell">{{ m.director }}</td>
              <td>{{ m.year }}</td>
              <td class="muted-cell">{{ m.genre }}</td>
              <td class="rating">{{ m.rating?.toFixed?.(1) ?? '-' }}</td>
              <td class="muted-cell">{{ formatCount(m.rating_count) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button class="btn" :disabled="page <= 1" @click="goto(1)">首页</button>
      <button class="btn" :disabled="page <= 1" @click="goto(page - 1)">上一页</button>
      <span class="muted">{{ page }} / {{ totalPages }}</span>
      <button class="btn" :disabled="page >= totalPages" @click="goto(page + 1)">下一页</button>
      <button class="btn" :disabled="page >= totalPages" @click="goto(totalPages)">末页</button>
      <select v-model.number="size" @change="goto(1)">
        <option :value="10">10 / 页</option>
        <option :value="20">20 / 页</option>
        <option :value="50">50 / 页</option>
        <option :value="100">100 / 页</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'

const items = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(20)
const sort = ref('rating')
const order = ref('desc')
const genre = ref('')
const country = ref('')
const yearFrom = ref(null)
const yearTo = ref(null)
const loading = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / size.value)))

function formatCount(n) {
  if (n == null) return '-'
  if (n >= 10000) return (n / 10000).toFixed(1) + ' 万'
  return n.toLocaleString()
}

async function fetchPage() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      size: size.value,
      sort: sort.value,
      order: order.value,
      genre: genre.value || undefined,
      country: country.value || undefined,
      year_from: yearFrom.value || undefined,
      year_to: yearTo.value || undefined,
    }
    const data = await api.paged(params)
    items.value = data?.data?.items || []
    total.value = data?.data?.total || 0
  } finally {
    loading.value = false
  }
}

function goto(p) {
  page.value = Math.max(1, Math.min(p, totalPages.value))
  fetchPage()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function apply() {
  page.value = 1
  fetchPage()
}

function reset() {
  sort.value = 'rating'
  order.value = 'desc'
  genre.value = ''
  country.value = ''
  yearFrom.value = null
  yearTo.value = null
  page.value = 1
  fetchPage()
}

watch([sort, order], () => { page.value = 1; fetchPage() })

onMounted(fetchPage)
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px; }
.filters {
  display: flex; flex-wrap: wrap; gap: 10px; align-items: center; padding: 12px 14px;
  margin-bottom: 12px;
}
.filters label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--muted); }
.filters input, .filters select {
  background: var(--bg); color: var(--text);
  border: 1px solid #1f2937; border-radius: 4px;
  padding: 4px 8px; min-width: 80px; font-size: 13px;
}
.filters input:focus, .filters select:focus { outline: none; border-color: var(--primary); }
.btn {
  padding: 6px 14px; border-radius: 4px; border: 1px solid var(--primary);
  background: var(--primary); color: #0f172a; cursor: pointer; font-weight: 500;
}
.btn.ghost { background: transparent; color: var(--text); border-color: #1f2937; }
.btn:hover:not(:disabled) { opacity: 0.85; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }

.table-wrap { max-height: 70vh; overflow-y: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  text-align: left; padding: 10px 8px; background: #1f2937;
  color: var(--muted); font-weight: 500; position: sticky; top: 0;
}
.data-table td { padding: 10px 8px; border-top: 1px solid #1f2937; vertical-align: top; }
.rank { color: var(--primary); font-weight: bold; }
.rating { color: var(--primary); font-weight: bold; }
.muted-cell { color: #94a3b8; font-size: 12px; }
.quote { color: #64748b; font-size: 11px; margin-top: 2px; font-style: italic; }

.pagination {
  display: flex; justify-content: center; align-items: center;
  gap: 8px; margin-top: 16px; padding: 12px;
}
.pagination select {
  background: var(--bg); color: var(--text); border: 1px solid #1f2937;
  border-radius: 4px; padding: 4px 8px;
}
</style>