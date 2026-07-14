<template>
  <div class="kind-progress" role="progressbar" :aria-label="label" :aria-valuenow="percent">
    <div class="kind-progress__bar">
      <div class="kind-progress__fill" :style="{ width: percent + '%', background: color }" />
    </div>
    <span class="kind-progress__lbl">{{ label }}</span>
    <span class="kind-progress__pct">{{ percent.toFixed(0) }}%</span>
  </div>
</template>

<script setup>
defineProps({
  label:   { type: String, required: true },
  percent: { type: Number, required: true },
  color:   { type: String, default: '#22d3ee' },
})
</script>

<style scoped>
.kind-progress {
  display: grid;
  grid-template-columns: 56px 1fr 48px;
  gap: 8px;
  align-items: center;
  font-size: var(--fs-xs);
  color: var(--c-muted);
}
.kind-progress__bar {
  position: relative;
  height: 6px;
  background: var(--c-surface-2);
  border-radius: 999px;
  overflow: hidden;
}
.kind-progress__fill {
  position: absolute; left: 0; top: 0; bottom: 0;
  border-radius: 999px;
  transition: width .35s var(--ease-out);
}
.kind-progress__lbl { color: var(--c-text); font-weight: 500; }
.kind-progress__pct { text-align: right; font-variant-numeric: tabular-nums; }
</style>