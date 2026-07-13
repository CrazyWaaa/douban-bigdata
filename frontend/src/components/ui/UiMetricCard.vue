<template>
  <div :class="['ui-metric', tone && `ui-metric--${tone}`]">
    <div class="ui-metric__head">
      <span class="ui-metric__label">{{ label }}</span>
      <span v-if="trend != null" :class="['ui-metric__trend', trend > 0 ? 'is-up' : trend < 0 ? 'is-down' : 'is-flat']">
        <span aria-hidden="true">{{ trend > 0 ? '▲' : trend < 0 ? '▼' : '·' }}</span>
        {{ Math.abs(trend) }}%
      </span>
    </div>
    <div class="ui-metric__value">
      <span class="ui-metric__num">{{ display }}</span>
      <span v-if="unit" class="ui-metric__unit">{{ unit }}</span>
    </div>
    <div v-if="sub" class="ui-metric__sub">{{ sub }}</div>
    <div class="ui-metric__bg" aria-hidden="true"></div>
  </div>
</template>

<script setup>
import { computed, toRef } from 'vue';
import { useCountUp } from '../../composables/useCountUp';

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  sub:   { type: String, default: '' },
  unit:  { type: String, default: '' },
  trend: { type: Number, default: null },
  tone:  { type: String, default: 'primary' },
  decimals: { type: Number, default: 0 },
});

const src = toRef(props, 'value');
const animated = useCountUp(src, { decimals: props.decimals });
const display = computed(() => {
  const v = animated.value;
  if (v == null || isNaN(v)) return '-';
  if (props.decimals > 0) return Number(v).toFixed(props.decimals);
  if (typeof v === 'number' && v >= 10000) return (v / 10000).toFixed(1) + 'w';
  return Number(v).toLocaleString();
});
</script>

<style scoped>
.ui-metric {
  position: relative; overflow: hidden;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r);
  padding: 12px 14px;
  transition: transform var(--t) var(--ease-out), border-color var(--t) var(--ease-out), box-shadow var(--t) var(--ease-out);
}
.ui-metric:hover { transform: translateY(-2px); border-color: var(--c-primary); box-shadow: var(--shadow); }
.ui-metric__head { display: flex; align-items: center; justify-content: space-between; }
.ui-metric__label { color: var(--c-muted); font-size: var(--fs-sm); }
.ui-metric__trend { font-size: var(--fs-xs); display: inline-flex; align-items: center; gap: 2px; }
.ui-metric__trend.is-up   { color: var(--c-success); }
.ui-metric__trend.is-down { color: var(--c-danger); }
.ui-metric__trend.is-flat { color: var(--c-muted); }
.ui-metric__value { display: flex; align-items: baseline; gap: 4px; margin-top: 6px; }
.ui-metric__num {
  font-size: var(--fs-3xl); font-weight: 700; line-height: 1.1;
  color: var(--c-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px;
}
.ui-metric--success .ui-metric__num { color: var(--c-success); }
.ui-metric--warning .ui-metric__num { color: var(--c-warning); }
.ui-metric--info    .ui-metric__num { color: var(--c-info); }
.ui-metric__unit { font-size: var(--fs-md); color: var(--c-muted); margin-left: 2px; }
.ui-metric__sub  { color: var(--c-muted); font-size: var(--fs-xs); margin-top: 4px; }
.ui-metric__bg {
  position: absolute; right: -30px; top: -30px;
  width: 120px; height: 120px; border-radius: 50%;
  background: radial-gradient(circle, var(--c-primary-tint) 0%, transparent 70%);
  pointer-events: none;
}
.ui-metric--success .ui-metric__bg { background: radial-gradient(circle, color-mix(in srgb, var(--c-success) 14%, transparent) 0%, transparent 70%); }
.ui-metric--warning .ui-metric__bg { background: radial-gradient(circle, color-mix(in srgb, var(--c-warning) 14%, transparent) 0%, transparent 70%); }
.ui-metric--info    .ui-metric__bg { background: radial-gradient(circle, color-mix(in srgb, var(--c-info) 14%, transparent) 0%, transparent 70%); }
</style>
