<template>
  <div class="dashboard">
    <header class="dashboard__head fade-up">
      <div class="dashboard__head-left">
        <h1 class="dashboard__title">
          <span class="dashboard__title-zh">豆瓣电影 TOP250 · 数据透视</span>
          <span class="dashboard__title-en">DOUBAN · DATA OVERVIEW</span>
        </h1>
        <p class="dashboard__sub">实时聚合 · 多维度对比 · 一屏看完 250 部高分影片</p>
      </div>
      <div class="dashboard__head-actions">
        <span v-if="lastLoadedAt" class="muted">最近更新：{{ formatTime(lastLoadedAt) }}</span>
        <span v-if="summaryExt" class="muted">数据集：{{ summaryExt.total ?? 0 }} 部</span>
        <UiButton size="sm" variant="ghost" :loading="loading" @click="refresh">刷新数据</UiButton>
      </div>
    </header>

    <div v-if="error" class="dashboard__error fade-up">
      <span>数据加载失败：{{ error }}</span>
      <UiButton size="sm" variant="outline" @click="refresh">重试</UiButton>
    </div>

    <!-- KPI 卡片区 -->
    <KpiBar :autoplay="false" :draggable="false">
      <UiMetricCard
        v-for="(m, i) in metricCards"
        :key="m.key"
        :label="m.label"
        :value="m.value"
        :sub="m.sub"
        :tone="m.tone"
        :decimals="m.decimals"
        :unit="m.unit"
        class="fade-up kpi-bar__cell"
        :style="kpiCellStyle(i)"
      />
    </KpiBar>

    <!-- 三区大屏：左 4 / 中 6 / 右 4 -->
    <div class="dashboard__grid">
      <!-- 左侧：高分榜 Top10 -->
      <section class="dashboard__col dashboard__col--left">
        <UiCard title="高分榜 Top10" glow>
          <template #actions><span class="muted">按评分排序</span></template>
          <ol class="live-list">
            <li
              v-for="(m, i) in topRated.slice(0, 10)"
              :key="m.douban_id"
              class="live-list__item fade-up"
              :style="liveItemStyle(i)"
            >
              <span :class="['live-list__rank', liveRankTone(i)]">{{ i + 1 }}</span>
              <div class="live-list__info">
                <router-link :to="`/movie/${m.douban_id}`" class="live-list__title">{{ m.title }}</router-link>
                <span class="live-list__meta">
                  <span>{{ m.year }}</span>
                  <span v-if="m.country">· {{ firstCountry(m.country) }}</span>
                </span>
              </div>
              <span class="live-list__rating">{{ m.rating?.toFixed?.(1) ?? '-' }}</span>
            </li>
          </ol>
        </UiCard>
      </section>

      <!-- 中区：类型分布 · 评分透视（双轴复合）；图表填满卡片高度 -->
      <section class="dashboard__col dashboard__col--mid">
        <UiCard title="类型分布 · 评分透视" elevated>
          <template #actions>
            <span class="muted">数量 / 均分</span>
            <span class="muted" style="margin-left:8px">点击柱子查看分布</span>
          </template>
          <div class="lens-grid">
            <div class="lens-grid__main">
              <EChart
                :option="genreLensOption"
                fill
                @itemClick="(p) => onChartClick('genre', p)"
              />
            </div>
            <div class="lens-grid__side">
              <div class="lens-summary">
                <div class="lens-summary__big">
                  <span class="lens-summary__num">{{ Number(summaryExt?.avg_rating ?? summary?.avg_rating ?? 0).toFixed(1) }}</span>
                  <span class="lens-summary__lbl">平均评分</span>
                </div>
                <div class="lens-summary__rings">
                  <div class="lens-ring lens-ring--primary">
                    <span class="lens-ring__num">{{ (summaryExt?.total ?? summary?.total ?? 0).toLocaleString() }}</span>
                    <span class="lens-ring__lbl">影片数</span>
                  </div>
                  <div class="lens-ring">
                    <span class="lens-ring__num">{{ formatCount(summaryExt?.avg_rating_count) }}</span>
                    <span class="lens-ring__lbl">单部均评</span>
                  </div>
                  <div class="lens-ring">
                    <span class="lens-ring__num">{{ Number(summaryExt?.max_rating ?? 0).toFixed(1) || '-' }}</span>
                    <span class="lens-ring__lbl">最高评分</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </UiCard>
      </section>

      <!-- 右侧：年代趋势 + 评分分布（两张图平分右侧高度） -->
      <section class="dashboard__col dashboard__col--right">
        <UiChartCard
          title="年代趋势"
          sub="渐变面积"
          :loading="!hasYear"
          :error="!hasYear && loaded.year === false"
          @retry="refresh"
          class="fade-up"
          style="animation-delay: 200ms; flex: 1 1 0; min-height: 220px;"
        >
          <EChart :option="yearOption" fill @itemClick="(p) => onChartClick('decade', p)" />
        </UiChartCard>
        <UiChartCard
          title="评分分布"
          sub="渐变柱状"
          :loading="!hasRatingDist"
          :error="!hasRatingDist && loaded.ratingDist === false"
          @retry="refresh"
          class="fade-up"
          style="animation-delay: 250ms; flex: 1 1 0; min-height: 220px;"
        >
          <EChart :option="ratingDistOption" fill @itemClick="(p) => onChartClick('ratingBucket', p)" />
        </UiChartCard>
      </section>
    </div>

    <!-- 第二排：分布图 3 列（去掉了语言 Top10） -->
    <section class="dashboard__row dashboard__row--3 fade-up" style="animation-delay: 320ms">
      <UiChartCard
        title="类型 Top10"
        sub="渐变面积"
        :loading="!hasGenre"
        :error="!hasGenre && loaded.genre === false"
        @retry="refresh"
      >
        <EChart :option="genreOption" height="260px" @itemClick="(p) => onChartClick('genre', p)" />
      </UiChartCard>
      <UiChartCard
        title="地区 Top10"
        sub="渐变面积"
        :loading="!hasCountry"
        :error="!hasCountry && loaded.country === false"
        @retry="refresh"
      >
        <EChart :option="countryOption" height="260px" @itemClick="(p) => onChartClick('country', p)" />
      </UiChartCard>
      <UiChartCard
        title="导演 Top10"
        :loading="!hasDirector"
        :error="!hasDirector && loaded.director === false"
        @retry="refresh"
      >
        <EChart :option="directorOption" height="260px" @itemClick="(p) => onChartClick('director', p)" />
      </UiChartCard>
    </section>

    <!-- 底部：TOP10 横向推荐（原 Top20 表格删除，与左上重复） -->
    <section v-if="topRated.length" class="dashboard__bottom fade-up" style="animation-delay: 380ms">
      <div class="dashboard__bottom-head">
        <span class="dashboard__bottom-title">TOP10 · 一键跳转详情</span>
        <span class="muted">点击卡片查看详情 · 点击类型/地区/年代图表可钻取更多分布</span>
      </div>
      <div class="bottom-grid">
        <router-link
          v-for="(m, i) in topRated.slice(0, 10)"
          :key="m.douban_id"
          :to="`/movie/${m.douban_id}`"
          class="bottom-card fade-up"
          :style="bottomCardStyle(i)"
        >
          <span class="bottom-card__rank">{{ i + 1 }}</span>
          <span class="bottom-card__title">{{ m.title }}</span>
          <span class="bottom-card__rating">{{ m.rating?.toFixed?.(1) }}</span>
        </router-link>
      </div>
    </section>

    <DrilldownPopover
      :visible="drill.visible"
      :pos="drill.pos"
      :dim="drill.dim"
      :value="drill.value"
      :title="drill.title"
      :movies="drillSource"
      @close="closeDrill"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { storeToRefs } from "pinia";
import { useDashboardStore } from "../stores/dashboard";
import EChart from "../components/EChart.vue";
import UiCard from "../components/ui/UiCard.vue";
import UiButton from "../components/ui/UiButton.vue";
import UiMetricCard from "../components/ui/UiMetricCard.vue";
import UiChartCard from "../components/ui/UiChartCard.vue";
import KpiBar from "../components/dashboard/KpiBar.vue";
import DrilldownPopover from "../components/DrilldownPopover.vue";
import {
  buildAreaLineOption, buildRankedBarOption, buildLensOption,
} from "../echarts/options";

const store = useDashboardStore();
const {
  summary, summaryExt,
  avgByGenre, avgByCountry, avgByYear,
  directors, decades,
  ratingDist, topRated,
  loading, error, lastLoadedAt,
} = storeToRefs(store);

const loaded = ref({ genre: null, country: null, year: null, ratingDist: null, director: null, topRated: null });
const hasGenre     = computed(() => (avgByGenre.value || []).length > 0 || loaded.value.genre === true);
const hasCountry   = computed(() => (avgByCountry.value || []).length > 0 || loaded.value.country === true);
const hasYear      = computed(() => (decades.value.length || (avgByYear.value?.length ?? 0)) > 0 || loaded.value.year === true);
const hasDirector  = computed(() => (directors.value || []).length > 0 || loaded.value.director === true);
const hasRatingDist   = computed(() => (ratingDist.value || []).length > 0 || loaded.value.ratingDist === true);
const hasTopRated     = computed(() => (topRated.value || []).length > 0 || loaded.value.topRated === true);

// 动画延迟样式（computed 形式，避免模板里 ` + 'ms' ` 引号转义）
function kpiCellStyle(i) {
  return { animationDelay: (i * 60) + 'ms' };
}
function liveItemStyle(i) {
  return { animationDelay: (i * 40) + 'ms' };
}
function bottomCardStyle(i) {
  return { animationDelay: (440 + i * 40) + 'ms' };
}

function firstCountry(s) {
  if (!s) return '';
  return String(s).split('/')[0]?.trim() ?? '';
}

// KPI 卡片
const metricCards = computed(() => {
  const s = summaryExt.value || {};
  const base = summary.value || {};
  const baseRating = s.avg_rating ?? base.avg_rating ?? 0;
  const total        = s.total ?? base.total ?? 0;
  const maxRating    = s.max_rating ?? 0;
  const avgCount     = s.avg_rating_count ?? null;
  const genreCount   = s.distinct_genre ?? base.distinct_genre ?? (avgByGenre.value?.length ?? 0);
  const countryCount = s.distinct_country ?? base.distinct_country ?? (avgByCountry.value?.length ?? 0);
  const cards = [
    { key: 'count',     label: '影片总数',   value: total,                       tone: 'primary', decimals: 0, unit: '部', sub: '数据规模' },
    { key: 'avg',       label: '平均评分',   value: Number(baseRating) || 0,     tone: 'success', decimals: 1,              sub: '加权均分' },
    { key: 'top',       label: '最高评分',   value: Number(maxRating) || 0,      tone: 'warning', decimals: 1,              sub: topRated.value[0]?.title || '' },
  ];
  if (avgCount != null) {
    cards.push({ key: 'ratecount', label: '单部均评', value: avgCount, tone: 'info', decimals: 0, unit: '人', sub: '平均每部评论人数' });
  }
  cards.push({ key: 'genre',   label: '类型数',   value: genreCount,   tone: 'primary', decimals: 0, unit: '类', sub: '覆盖范围' });
  cards.push({ key: 'country', label: '地区数',   value: countryCount, tone: 'success', decimals: 0, unit: '地', sub: '覆盖范围' });
  return cards;
});

// 图表配置
const genreLensOption = computed(() => buildLensOption(avgByGenre.value));
const yearOption      = computed(() => buildAreaLineOption(decades.value.length ? decades.value : avgByYear.value, { color: '#22d3ee', label: '年代' }));
const genreOption     = computed(() => buildAreaLineOption(avgByGenre.value, { color: '#38bdf8' }));
const countryOption   = computed(() => buildAreaLineOption(avgByCountry.value, { color: '#f472b6' }));

const ratingDistOption = computed(() => {
  const items = ratingDist.value || [];
  const maxIdx = items.reduce((p, d, i) => (d.count > (items[p]?.count ?? -1) ? i : p), 0);
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 8, right: 16, top: 16, bottom: 28, containLabel: true },
    xAxis: { type: 'category', data: items.map(d => d.bucket), axisLabel: { color: '#94a3b8', fontSize: 11 } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 11 }, splitLine: { lineStyle: { color: 'rgba(148,163,184,0.12)' } } },
    series: [{
      type: 'bar', barWidth: '55%',
      data: items.map((d, i) => ({
        value: d.count,
        itemStyle: {
          color: i === maxIdx
            ? { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#f59e0b' }, { offset: 1, color: 'rgba(245,158,11,0.25)' }] }
            : { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#a78bfa' }, { offset: 1, color: 'rgba(167,139,250,0.25)' }] },
          borderRadius: [6, 6, 0, 0],
        },
      })),
      label: { show: true, position: 'top', color: '#94a3b8', fontSize: 11 },
      animationDuration: 1200, animationEasing: 'cubicOut',
    }],
  };
});

const directorOption = computed(() => buildRankedBarOption(directors.value, { color: '#34d399' }));

// 钻取：点击图表柱子时浮窗
const drill = ref({ visible: false, pos: { x: 0, y: 0 }, dim: '', value: '', title: '' });
// 钻取源数据：topRated 字段不足以支持 distribution 时，暂时只能利用前 20（实际数据来自 topRated(20)）
const drillSource = computed(() => topRated.value || []);

function buildDrillTitle(dim, name) {
  if (dim === 'genre')        return `类型：${name}`;
  if (dim === 'country')      return `地区：${name}`;
  if (dim === 'director')     return `导演：${name}`;
  if (dim === 'decade')       return `年代：${name}s`;
  if (dim === 'ratingBucket') return `评分段：${name}`;
  return name;
}

function onChartClick(dim, params) {
  if (!params) return;
  const name = params.name;
  let value = name;
  // decade 维度是数字（70/80/90）
  if (dim === 'decade') {
    const n = Number(name);
    if (!Number.isNaN(n)) value = n;
  }
  // 浮窗定位在点击位置附近，避免被裁切
  const x = Math.min(window.innerWidth - 400, Math.max(8, (params.event?.offsetX || 200) + 40));
  const y = Math.min(window.innerHeight - 460, Math.max(8, (params.event?.offsetY || 200) + 40));
  drill.value = { visible: true, pos: { x, y }, dim, value, title: buildDrillTitle(dim, name) };
}
function closeDrill() {
  drill.value = Object.assign({}, drill.value, { visible: false });
}

function liveRankTone(i) {
  if (i === 0) return 'live-list__rank--gold';
  if (i === 1) return 'live-list__rank--silver';
  if (i === 2) return 'live-list__rank--bronze';
  return '';
}

function formatTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
function formatCount(n) {
  if (n == null) return '-';
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
  return n.toLocaleString();
}

async function refresh() {
  await store.loadDashboard();
  setTimeout(loadCharts, 0);
}
async function loadCharts() {
  try {
    await store.loadAll();
  } finally {
    loaded.value.genre       = (avgByGenre.value?.length ?? 0) > 0;
    loaded.value.country     = (avgByCountry.value?.length ?? 0) > 0;
    loaded.value.year        = (decades.value.length || (avgByYear.value?.length ?? 0) > 0);
    loaded.value.director    = (directors.value?.length ?? 0) > 0;
    loaded.value.ratingDist  = (ratingDist.value?.length ?? 0) > 0;
    loaded.value.topRated    = (topRated.value?.length ?? 0) > 0;
  }
}

onMounted(async () => {
  await refresh();
});
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 12px; }

.dashboard__head { display: flex; justify-content: space-between; align-items: flex-end; gap: 12px; flex-wrap: wrap; }
.dashboard__head-left { display: flex; flex-direction: column; gap: 4px; }
.dashboard__title { margin: 0; display: flex; align-items: baseline; gap: 12px; font-size: var(--fs-2xl); font-weight: 700; letter-spacing: 0.5px; }
.dashboard__title-zh { color: var(--c-text); }
.dashboard__title-en { font-size: 11px; color: var(--c-muted); letter-spacing: 2px; font-weight: 600; }
.dashboard__sub { margin: 0; color: var(--c-muted); font-size: var(--fs-sm); }
.dashboard__head-actions { display: flex; align-items: center; gap: 12px; }

.dashboard__error {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px; border-radius: var(--r);
  background: color-mix(in srgb, var(--c-danger) 14%, transparent);
  color: var(--c-danger);
  border: 1px solid color-mix(in srgb, var(--c-danger) 30%, transparent);
}

.kpi-bar__cell { flex: 1 1 0; min-width: 0; }

/* 主布局：三区，左榜 / 中图 + 右侧图（堆叠）；所有列等高 */
.dashboard__grid {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(420px, 2fr) minmax(280px, 1fr);
  gap: 12px;
  align-items: stretch;
  min-height: 440px; /* 保证三列有统一下限，避免中区不再显得拥挤 */
}
.dashboard__col { display: flex; flex-direction: column; gap: 12px; height: 100%; }
/* 让卡片撑满整列，确保与左侧榜单同样高度 */
.dashboard__col > .ui-card,
.dashboard__col > section > .ui-card { flex: 1 1 auto; min-height: 0; height: 100%; }
.dashboard__col > section { flex: 1 1 0; display: flex; }

/* 中区：图表在上，summary/环形总结在下（融合成一个卡片内容） */
.lens-grid { display: flex; flex-direction: column; gap: 10px; height: 100%; }
.lens-grid__main { flex: 1 1 auto; min-height: 0; min-width: 100%; }
.lens-grid__side { padding-top: 2px; }
.lens-summary { display: flex; align-items: stretch; gap: 14px; }
.lens-summary__big { display: flex; flex-direction: column; justify-content: center; padding-right: 8px; }
.lens-summary__num {
  font-size: var(--fs-4xl); font-weight: 800; color: var(--c-primary);
  line-height: 1; font-variant-numeric: tabular-nums; letter-spacing: -1px;
}
.lens-summary__lbl { color: var(--c-muted); font-size: var(--fs-sm); margin-top: 4px; }

/* 环形 summary：让各 ring 平分剩余空间（去掉固定 10rem 后更舒展） */
.lens-summary__rings { display: flex; gap: 10px; flex: 1 1 auto; min-width: 0; align-items: stretch; }
.lens-ring {
  flex: 1 1 0; min-width: 0;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  padding: 12px 14px;
  border-radius: var(--r);
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
}
.lens-ring--primary { border-color: var(--c-primary-tint); }
.lens-ring__num { font-size: var(--fs-xl); font-weight: 700; color: var(--c-text); font-variant-numeric: tabular-nums; }
.lens-ring--primary .lens-ring__num { color: var(--c-primary); }
.lens-ring__lbl { color: var(--c-muted); font-size: var(--fs-xs); margin-top: 2px; white-space: nowrap; }

/* 高分榜 list：让列表在卡片中均摊高度，避免卡片视觉上收缩 */
.live-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 8px;
  flex: 1 1 auto; min-height: 0;
}
.live-list__item {
  display: grid; grid-template-columns: 28px 1fr auto; gap: 10px; align-items: center;
  padding: 8px 12px; border-radius: var(--r-sm);
  background: var(--c-surface-2);
  transition: background var(--t-fast) var(--ease-out), transform var(--t-fast) var(--ease-out);
}
.live-list__item:hover { background: var(--c-primary-tint); transform: translateX(2px); }
.live-list__rank {
  width: 26px; height: 26px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 12px;
  background: var(--c-surface); color: var(--c-muted);
  border: 1px solid var(--c-border);
}
.live-list__rank--gold   { color: #fff; background: linear-gradient(135deg, #f59e0b, #d97706); border-color: transparent; }
.live-list__rank--silver { color: #fff; background: linear-gradient(135deg, #94a3b8, #64748b); border-color: transparent; }
.live-list__rank--bronze { color: #fff; background: linear-gradient(135deg, #fb923c, #c2410c); border-color: transparent; }
.live-list__info { min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.live-list__title { color: var(--c-text); font-weight: 500; font-size: var(--fs-md); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.live-list__title:hover { color: var(--c-primary); }
.live-list__meta { color: var(--c-muted); font-size: var(--fs-xs); }
.live-list__rating { color: var(--c-primary); font-weight: 700; font-size: var(--fs-md); font-variant-numeric: tabular-nums; }

/* 第二排：图表横向流布（3 列） */
.dashboard__row { display: grid; gap: 12px; }
.dashboard__row--3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }

/* 底部 TOP10 横向卡片 */
.dashboard__bottom {
  background: linear-gradient(180deg, transparent, color-mix(in srgb, var(--c-primary) 4%, transparent));
  border-top: 1px solid var(--c-border);
  border-bottom: 1px solid var(--c-border);
  border-radius: var(--r);
  padding: 12px 14px;
}
.dashboard__bottom-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; gap: 8px; flex-wrap: wrap; }
.dashboard__bottom-title { font-weight: 600; font-size: var(--fs-md); color: var(--c-text); }
.bottom-grid {
  display: grid;
  grid-template-columns: repeat(10, minmax(0, 1fr));
  gap: 8px;
}
.bottom-card {
  display: grid;
  grid-template-columns: 22px 1fr auto;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-sm);
  color: var(--c-text);
  text-decoration: none;
  transition: border-color var(--t-fast) var(--ease-out), background var(--t-fast) var(--ease-out), transform var(--t-fast) var(--ease-out);
}
.bottom-card:hover { border-color: var(--c-primary); background: var(--c-primary-tint); transform: translateY(-1px); }
.bottom-card__rank { color: var(--c-warning); font-weight: 700; font-size: var(--fs-sm); text-align: center; }
.bottom-card__title { font-size: var(--fs-sm); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bottom-card__rating { color: var(--c-primary); font-weight: 700; font-size: var(--fs-sm); font-variant-numeric: tabular-nums; }

/* 响应式：在 >1600px 时尽量占满；在 <1280px 时逐步收敛 */
@media (max-width: 1600px) {
  .dashboard__grid { grid-template-columns: minmax(260px, 1fr) minmax(380px, 2fr) minmax(260px, 1fr); }
}
@media (max-width: 1280px) {
  .dashboard__grid { grid-template-columns: 1fr 1fr; }
  .dashboard__col--right { grid-column: 1 / -1; }
  .dashboard__row--3 { grid-template-columns: 1fr 1fr; }
  .bottom-grid { grid-template-columns: repeat(5, 1fr); }
}
@media (max-width: 900px) {
  .dashboard__grid { grid-template-columns: 1fr; }
  .dashboard__row--3 { grid-template-columns: 1fr; }
  .bottom-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .bottom-grid { grid-template-columns: 1fr; }
}
</style>
