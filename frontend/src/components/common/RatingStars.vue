<template>
  <div class="rating-stars" :aria-label="ariaLabel">
    <div v-for="(seg, i) in segments" :key="i" class="rating-stars__row">
      <span class="rating-stars__lbl">{{ seg.lbl }}</span>
      <div class="rating-stars__bar">
        <div class="rating-stars__fill" :style="{ width: seg.percent + '%', background: seg.color }" />
      </div>
      <span class="rating-stars__pct">{{ seg.percent.toFixed(1) }}%</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { normalizeStars } from '../../utils/format'

const props = defineProps({
  stars: { type: Object, default: () => null },
})

const PALETTE = ['#ef4444', '#f59e0b', '#facc15', '#84cc16', '#22c55e']

const segments = computed(() => {
  const ns = normalizeStars(props.stars)
  if (!ns) return []
  const total = ns.total > 0 ? ns.total : 1
  return ['5', '4', '3', '2', '1'].map((k, i) => {
    const v = Number(ns.segments[['1','2','3','4','5'].indexOf(k)]) || 0
    const pct = (v / total) * 100
    return { lbl: `${k}星`, percent: pct, color: PALETTE[i] }
  })
})

const ariaLabel = computed(() => {
  if (!segments.value.length) return ''
  return segments.value.map((s) => `${s.lbl} ${s.percent.toFixed(0)}%`).join(', ')
})
</script>

<style scoped>
.rating-stars { display: flex; flex-direction: column; gap: 4px; width: 100%; }
.rating-stars__row {
  display: grid;
  grid-template-columns: 36px 1fr 52px;
  align-items: center;
  gap: 8px;
  font-size: var(--fs-xs);
  color: var(--c-muted);
}
.rating-stars__lbl { font-variant-numeric: tabular-nums; }
.rating-stars__bar {
  position: relative;
  height: 6px;
  background: var(--c-surface-2);
  border-radius: 999px;
  overflow: hidden;
}
.rating-stars__fill {
  position: absolute; left: 0; top: 0; bottom: 0;
  border-radius: 999px;
  transition: width .35s var(--ease-out);
}
.rating-stars__pct { text-align: right; font-variant-numeric: tabular-nums; }
</style>