<template>
  <div class="ui-empty">
    <div v-if="icon" class="ui-empty__icon">{{ icon }}</div>
    <div class="ui-empty__title">{{ title }}</div>
    <div v-if="desc" class="ui-empty__desc">{{ desc }}</div>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  icon:  { type: String, default: '' },
  title: { type: String, default: '暂无数据' },
  desc:  { type: String, default: '' },
})
</script>

<style scoped>
.ui-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; padding: 56px 20px; color: var(--c-muted);
  animation: fadeUp var(--t-slow) var(--ease-out) both;
}
.ui-empty__icon { font-size: 48px; line-height: 1; opacity: .65; }
.ui-empty__title { font-size: var(--fs-md); color: var(--c-text-soft); font-weight: 500; }
.ui-empty__desc  { font-size: var(--fs-sm); color: var(--c-muted); }
</style>