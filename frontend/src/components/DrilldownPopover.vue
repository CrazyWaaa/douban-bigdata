<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="drill-popover"
      :style="popupStyle"
      @click.stop
    >
      <header class="drill-popover__head">
        <span class="drill-popover__title">{{ title }}</span>
        <button class="drill-popover__close" @click="$emit('close')" aria-label="close-label">×</button>
      </header>
      <div class="drill-popover__meta">
        <span>共 <b>{{ matched.length }}</b> 部</span>
        <span>均分 <b>{{ avgRating }}</b></span>
        <span v-if="yearRange">年代 <b>{{ yearRange }}</b></span>
      </div>
      <div class="drill-popover__charts">
        <div class="drill-popover__chart">
          <div class="drill-popover__label">评分段</div>
          <EChart :option="ratingPieOption" height="160px" />
        </div>
        <div class="drill-popover__chart">
          <div class="drill-popover__label">年代段</div>
          <EChart :option="decadePieOption" height="160px" />
        </div>
        <div class="drill-popover__chart drill-popover__chart--full">
          <div class="drill-popover__label">地区</div>
          <EChart v-if="countryDist.length" :option="countryPieOption" height="160px" />
          <div v-else class="drill-popover__empty">无地区数据</div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount } from "vue";
import EChart from "./EChart.vue";
import { useDrilldown } from "../composables/useDrilldown";

const props = defineProps({
  visible: { type: Boolean, default: false },
  pos: { type: Object, default: () => ({ x: 0, y: 0 }) },
  dim: { type: String, default: "" },
  value: { type: [String, Number], default: "" },
  title: { type: String, default: "" },
  movies: { type: Array, default: () => [] },
});
const emit = defineEmits(["close"]);

const popupStyle = computed(() => ({
  left: (props.pos?.x || 0) + 'px',
  top: (props.pos?.y || 0) + 'px',
}));

const dimRef = computed(() => props.dim);
const valueRef = computed(() => props.value);
const moviesRef = computed(() => props.movies);

const { matched, ratingDist, decadeDist, countryDist } = useDrilldown(moviesRef, dimRef, valueRef);

const PIE_COLORS = ["#38bdf8", "#a78bfa", "#34d399", "#f472b6", "#f59e0b", "#22d3ee", "#fb923c", "#fb7185"];

function makePieOption(items) {
  const data = (items || []).map((d, i) => ({ ...d, itemStyle: { color: PIE_COLORS[i % PIE_COLORS.length] } }));
  return {
    tooltip: { trigger: "item", formatter: "{b}<br/>数量: <b>{c}</b> ({d}%)" },
    legend: { type: "scroll", orient: "horizontal", bottom: 0, textStyle: { color: "#94a3b8", fontSize: 11 } },
    series: [{
      type: "pie", radius: ["38%", "70%"], center: ["50%", "42%"],
      avoidLabelOverlap: true,
      label: { show: true, formatter: "{b}\n{d}%", color: "#cbd5e1", fontSize: 11 },
      labelLine: { length: 8, length2: 6 },
      data,
      animationDuration: 600, animationEasing: "cubicOut",
    }],
  };
}

const ratingPieOption = computed(() => makePieOption(ratingDist.value));
const decadePieOption = computed(() => makePieOption(decadeDist.value));
const countryPieOption = computed(() => makePieOption(countryDist.value));

const avgRating = computed(() => {
  const list = matched.value.filter((m) => m.rating != null);
  if (!list.length) return "-";
  return (list.reduce((s, m) => s + Number(m.rating || 0), 0) / list.length).toFixed(2);
});
const yearRange = computed(() => {
  const years = matched.value.map((m) => m.year).filter((y) => y != null);
  if (!years.length) return "";
  return Math.min(...years) + " - " + Math.max(...years);
});

// 点击浮窗外部 → 关闭
function onDocClick(e) {
  if (!props.visible) return;
  if (e.target.closest(".drill-popover")) return;
  emit("close");
}
onMounted(() => document.addEventListener("click", onDocClick));
onBeforeUnmount(() => document.removeEventListener("click", onDocClick));
</script>

<style scoped>
.drill-popover {
  position: fixed;
  z-index: 9000;
  width: 380px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r);
  box-shadow: var(--shadow-lg);
  padding: 12px 14px 10px;
  color: var(--c-text);
  animation: drillIn 180ms var(--ease-out);
}
@keyframes drillIn {
  from { opacity: 0; transform: translateY(-6px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0)    scale(1);    }
}
.drill-popover__head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.drill-popover__title { font-weight: 600; font-size: var(--fs-md); }
.drill-popover__close {
  background: transparent; border: 0; color: var(--c-muted);
  font-size: 20px; line-height: 1; cursor: pointer; padding: 0 4px;
  border-radius: 4px; transition: color var(--t-fast) var(--ease-out), background var(--t-fast) var(--ease-out);
}
.drill-popover__close:hover { color: var(--c-text); background: var(--c-surface-2); }
.drill-popover__meta {
  display: flex; gap: 14px; flex-wrap: wrap;
  color: var(--c-muted); font-size: var(--fs-xs); margin: 6px 0 10px;
}
.drill-popover__meta b { color: var(--c-text); font-weight: 600; }
.drill-popover__charts {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px 14px;
}
.drill-popover__chart--full { grid-column: 1 / -1; }
.drill-popover__label {
  font-size: var(--fs-xs); color: var(--c-muted);
  margin-bottom: 2px; padding-left: 4px;
}
.drill-popover__empty {
  height: 160px; display: flex; align-items: center; justify-content: center;
  color: var(--c-muted); font-size: var(--fs-sm);
  background: var(--c-surface-2); border-radius: var(--r-sm);
}
</style>
