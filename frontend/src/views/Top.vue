<template>
  <div class="top-page">
    <header class="page-head fade-up">
      <div>
        <h1 class="page-title">高分榜单</h1>
        <p class="page-sub">可按 评分 / 评价人数 / 年份 片名 灵活筛选与排序。</p>
      </div>
      <div v-if="!loading" class="muted">共 {{ total }} 部</div>
    </header>

    <UiCard class="fade-up-stagger" style="--i: 1; margin-bottom: 14px;">
      <div class="filters">
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
          <span>年起</span>
          <input v-model.number="yearFrom" type="number" placeholder="1990" />
        </label>
        <label>
          <span>年止</span>
          <input v-model.number="yearTo" type="number" placeholder="2025" />
        </label>
        <UiButton size="sm" @click="apply">应用</UiButton>
        <UiButton size="sm" variant="ghost" @click="reset">重置</UiButton>
      </div>
    </UiCard>

    <div v-if="error" class="top-page__error fade-up" role="alert">
      <span>榜单加载失败:{{ error }}</span>
      <UiButton size="sm" variant="outline" @click="apply">重试</UiButton>
    </div>

    <UiCard :body-style="{ padding: 0 }" class="fade-up-stagger" style="--i: 2" v-else>
      <div v-if="loading" class="loading-row">加载中…</div>
      <UiEmptyState v-else-if="!items.length" title="没有符合条件的影片" desc="试试调整筛选条件" />
      <div v-else class="top-table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width:60px;">#</th>
              <th>片名</th>
              <th style="width:140px;">导演</th>
              <th style="width:60px;">年份</th>
              <th style="width:80px;">类型</th>
              <th style="width:80px;">评分</th>
              <th style="width:100px;">评价人数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(m, i) in items" :key="m.douban_id" class="data-table__row" :style="{ animationDelay: (i * 20) + 'ms' }">
              <td class="data-table__rank">{{ (page - 1) * size + i + 1 }}</td>
              <td>
                <router-link :to="`/movie/${m.douban_id}`" class="data-table__title">{{ m.title || '-' }}</router-link>
                <div v-if="m.quote" class="data-table__quote">"{{ m.quote || '-' }}"</div>
              </td>
              <td class="data-table__meta">{{ m.director || '-' }}</td>
              <td>{{ m.year || '-' }}</td>
              <td class="data-table__meta">{{ m.genre || '-' }}</td>
              <td class="data-table__rating">{{ formatRating(m.rating) }}</td>
              <td class="data-table__meta">{{ formatRatingCount(m.rating_count) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </UiCard>

    <div v-if="totalPages > 1" class="pagination fade-up-stagger" style="--i: 3">
      <UiButton size="sm" variant="ghost" :disabled="page <= 1" @click="goto(1)">首页</UiButton>
      <UiButton size="sm" variant="ghost" :disabled="page <= 1" @click="goto(page - 1)">上一页</UiButton>
      <span class="muted">第 {{ page }} / {{ totalPages }} 页</span>
      <UiButton size="sm" variant="ghost" :disabled="page >= totalPages" @click="goto(page + 1)">下一页</UiButton>
      <UiButton size="sm" variant="ghost" :disabled="page >= totalPages" @click="goto(totalPages)">末页</UiButton>
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
/**
 * Top.vue - 重写
 * - 任意字段异常容错(顶部错误条 + retry)
 * - 过滤/分页/排序 URL 同步(to={...query:{...}}),可分享/回退
 * - 行间错位(missing 字段)兜底为 '-'
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import UiCard from '../components/ui/UiCard.vue'
import UiButton from '../components/ui/UiButton.vue'
import UiEmptyState from '../components/ui/UiEmptyState.vue'

import { api } from '../api'
import { invalidate } from '../composables/useApiQuery'
import { formatRating, formatRatingCount } from '../utils/format'

const route = useRoute()
const router = useRouter()

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
const error = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil((total.value || 0) / size.value)))

async function apply() {
  loading.value = true
  error.value = ''
  const query = { page: page.value, size: size.value, sort: sort.value, order: order.value }
  if (genre.value) query.genre = genre.value
  if (country.value) query.country = country.value
  if (yearFrom.value) query.year_from = yearFrom.value
  if (yearTo.value) query.year_to = yearTo.value
  router.replace({ path: '/top', query })
  try {
    const res = await api.paged(query)
    items.value = Array.isArray(res?.items) ? res.items : []
    total.value = Number(res?.total ?? 0)
  } catch (e) {
    error.value = e?.response?.data?.message || e?.message || String(e)
    items.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function goto(p) {
  page.value = Math.max(1, Math.min(totalPages.value, p))
  apply()
}

function reset() {
  page.value = 1
  sort.value = 'rating'
  order.value = 'desc'
  genre.value = ''
  country.value = ''
  yearFrom.value = null
  yearTo.value = null
  invalidate('movies:paged:')
  apply()
}

// 从 URL 初始化
function syncFromQuery() {
  const q = route.query
  page.value = Number(q.page) || 1
  size.value = Number(q.size) || 20
  sort.value = String(q.sort || 'rating')
  order.value = String(q.order || 'desc')
  genre.value = q.genre ? String(q.genre) : ''
  country.value = q.country ? String(q.country) : ''
  yearFrom.value = q.year_from ? Number(q.year_from) : null
  yearTo.value = q.year_to ? Number(q.year_to) : null
}

watch(() => route.query, () => { syncFromQuery(); apply() }, { deep: true })

onMounted(() => { syncFromQuery(); apply() })
</script>

<style scoped>
.top-page { display: flex; flex-direction: column; gap: 16px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px; }
.page-title { margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }
.page-sub { margin: 4px 0 0; color: var(--c-muted); font-size: 13px; }

.filters {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px;
  align-items: center;
}
@media (max-width: 800px) {
  .filters { grid-template-columns: repeat(2, 1fr); }
}
.filters label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--c-muted); }
.filters input, .filters select {
  background: var(--c-bg); color: var(--c-text);
  border: 1px solid var(--c-border); border-radius: var(--r-sm);
  padding: 6px 10px;
  transition: border-color var(--t-fast) var(--ease-out);
}
.filters input:focus, .filters select:focus { outline: none; border-color: var(--c-primary); }

.top-page__error {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; border-radius: var(--r);
  background: color-mix(in srgb, var(--c-danger) 14%, transparent);
  border: 1px solid color-mix(in srgb, var(--c-danger) 50%, transparent);
}

.loading-row {
  padding: 32px; text-align: center;
  color: var(--c-muted);
  background: linear-gradient(90deg, var(--c-surface-2) 0%, var(--c-border) 50%, var(--c-surface-2) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}

.top-table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--c-border);
  text-align: left;
  font-size: 13px;
}
.data-table th {
  position: sticky; top: 0;
  background: var(--c-surface-2);
  color: var(--c-muted);
  font-weight: 600;
}
.data-table__row { transition: background var(--t-fast) var(--ease-out); }
.data-table__row:hover { background: var(--c-surface-2); }
.data-table__rank { color: var(--c-primary); font-weight: 700; font-variant-numeric: tabular-nums; }
.data-table__title { font-weight: 600; color: var(--c-text); }
.data-table__title:hover { color: var(--c-primary); }
.data-table__quote {
  font-size: 12px; color: var(--c-muted);
  font-style: italic;
  margin-top: 2px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  max-width: 480px;
}
.data-table__meta { color: var(--c-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 220px; }
.data-table__rating { color: var(--c-warning); font-weight: 700; font-variant-numeric: tabular-nums; }

.pagination { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pagination select {
  background: var(--c-surface); color: var(--c-text);
  border: 1px solid var(--c-border); border-radius: 6px;
  padding: 4px 8px;
}
</style>