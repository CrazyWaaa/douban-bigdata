<template>
  <span :class="['ui-tag', tone && `ui-tag--${tone}`]">
    <slot />
  </span>
</template>

<script setup>
defineProps({
  tone: { type: String, default: 'default' },
});
</script>

<style scoped>
.ui-tag {
  display: inline-flex; align-items: center;
  padding: 2px 8px; border-radius: 999px;
  font-size: var(--fs-xs); line-height: 1.4;
  background: var(--c-surface-2); color: var(--c-text-soft);
  border: 1px solid var(--c-border);
}
.ui-tag--primary { background: var(--c-primary-tint); color: var(--c-primary); border-color: transparent; }
.ui-tag--success { background: color-mix(in srgb, var(--c-success) 18%, transparent); color: var(--c-success); border-color: transparent; }
.ui-tag--warning { background: color-mix(in srgb, var(--c-warning) 18%, transparent); color: var(--c-warning); border-color: transparent; }
.ui-tag--info    { background: color-mix(in srgb, var(--c-info) 18%, transparent); color: var(--c-info); border-color: transparent; }
</style>
