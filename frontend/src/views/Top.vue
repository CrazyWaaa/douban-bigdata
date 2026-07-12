<template>
  <div class="top-page">
    <header class="page-head fade-up">
      <div>
        <h1 class="page-title">高分榜单</h1>
        <p class="page-sub">按评分 / 评价数 / 年代 灵活筛选与排序</p>
      </div>
      <div class="muted" v-if="!loading">共 {{ total }} 部</div>
    </header>

    <UiCard class="fade-up" style="animation-delay: 60ms; margin-bottom: 14px;">
      <div class="filters">
        <label>
          <span>排序</span>
          <select v-model="sort">
            <option value="rating">评分</option>
            <option value="rating_count">评价数</option>
            <option value="year">年代</option>
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

    <UiCard :body-style="{ padding: 0 }" class="fade-up" style="animation-delay: 120ms">
      <div v-if="loading" class="loading-row">加载中…</div>
      <UiEmptyState v-else-if="!items.length" title="没有符合条件的影片" desc="试试调整筛选条件" />
      <div v-else class="top-table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width:60px;">#</th>
              <th>片名</th>
              <th style="width:140px;">导演</th>
              <th style="width:60px;">年代</th>
              <th style="width:80px;">类型</th>
              <th style="width:80px;">评分</th>
              <th style="width:100px;">评价数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(m, i) in items" :key="m.douban_id" class="data-table__row" :style="{ animationDelay: (i * 20) + 'ms' }">
              <td class="data-table__rank">{{ (page - 1) * size + i + 1 }}</td>
              <td>
                <router-link :to="`/movie/${m.douban_id}`" class="data-table__title">{{ m.title }}</router-link>
                <div v-if="m.quote" class="data-table__quote">"{{ m.quote }}"</div>
              </td>
              <td class="data-table__meta">{{ m.director }}</td>
              <td>{{ m.year }}</td>
              <td class="data-table__meta">{{ m.genre }}</td>
              <td class="data-table__rating">{{ m.rating?.toFixed?.(1) ?? '-' }}</td>
              <td class="data-table__meta">{{ formatCount(m.rating_count) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </UiCard>

    <div v-if="totalPages > 1" class="pagination fade-up" style="animation-delay: 180ms">
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
import { ref, computed, onMounted } from 'vue';
import { api } from '../api';
import UiCard from '../components/ui/UiCard.vue';
import UiButton from '../components/ui/UiButton.vue';
import UiEmptyState from '../components/ui/UiEmptyState.vue';

const items = ref([]);
const total = ref(0);
const page = ref(1);
const size = ref(20);
const sort = ref('rating');
const order = ref('desc');
const genre = ref('');
const country = ref('');
const yearFrom = ref(null);
const yearTo = ref(null);
const loading = ref(false);

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / size.value)));

function formatCount(n) {
  if (n == null) return '-';
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w';
  return n.toLocaleString();
}

async function fetchPage() {
  loading.value = true;
  try {
    const params = {
      page: page.value, size: size.value, sort: sort.value, order: order.value,
      genre: genre.value || undefined, country: country.value || undefined,
      year_from: yearFrom.value || undefined, year_to: yearTo.value || undefined,
    };
    const data = await api.paged(params);
    items.value = data?.data?.items || [];
    total.value = data?.data?.total || 0;
  } finally { loading.value = false; }
}

function goto(p) {
  page.value = Math.max(1, Math.min(p, totalPages.value));
  fetchPage();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function apply() { page.value = 1; fetchPage(); }
function reset() { genre.value = ''; country.value = ''; yearFrom.value = null; yearTo.value = null; sort.value = 'rating'; order.value = 'desc'; page.value = 1; fetchPage(); }
onMounted(fetchPage);
</script>

<style scoped>
.top-page { display: flex; flex-direction: column; gap: 14px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px; }
.page-title { margin: 0; font-size: var(--fs-2xl); font-weight: 700; }
.page-sub { margin: 4px 0 0; color: var(--c-muted); font-size: var(--fs-sm); }

.filters { display: flex; gap: 12px; align-items: flex-end; flex-wrap: wrap; }
.filters label { display: flex; flex-direction: column; gap: 4px; min-width: 100px; }
.filters span { color: var(--c-muted); font-size: var(--fs-xs); }
.filters input, .filters select {
  background: var(--c-bg); color: var(--c-text);
  border: 1px solid var(--c-border); border-radius: var(--r-sm);
  padding: 6px 10px; font-size: var(--fs-sm); min-width: 120px;
  transition: border-color var(--t-fast) var(--ease-out);
}
.filters input:focus, .filters select:focus { outline: none; border-color: var(--c-primary); }

.top-table-wrap { max-height: 70vh; overflow-y: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: var(--fs-md); }
.data-table th {
  text-align: left; padding: 10px 12px;
  background: var(--c-surface-2); color: var(--c-muted);
  font-weight: 500; position: sticky; top: 0; font-size: var(--fs-sm);
}
.data-table td { padding: 10px 12px; border-top: 1px solid var(--c-border); vertical-align: top; }
.data-table__row {
  opacity: 0; transform: translateY(4px);
  animation: fadeUp .35s var(--ease-out) both;
  transition: background var(--t-fast) var(--ease-out);
}
.data-table__row:hover { background: var(--c-surface-2); }
.data-table__rank { color: var(--c-primary); font-weight: 700; }
.data-table__title { color: var(--c-text); font-weight: 500; }
.data-table__title:hover { color: var(--c-primary); }
.data-table__quote { color: var(--c-muted); font-size: 11px; margin-top: 2px; font-style: italic; }
.data-table__meta { color: var(--c-muted); font-size: var(--fs-sm); }
.data-table__rating { color: var(--c-primary); font-weight: 700; }

.loading-row { padding: 48px; text-align: center; color: var(--c-muted); }

.pagination { display: flex; align-items: center; gap: 8px; justify-content: center; padding: 10px 0; }
.pagination select { background: var(--c-bg); color: var(--c-text); border: 1px solid var(--c-border); border-radius: var(--r-sm); padding: 4px 8px; font-size: var(--fs-sm); }
</style>