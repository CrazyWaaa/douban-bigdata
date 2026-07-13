<template>
  <div class="page-shell">
    <header class="page-head fade-up">
      <div>
        <h1 class="page-title">{{ title }}</h1>
        <p class="page-sub">{{ subtitle }}</p>
      </div>
      <div class="page-head__actions">
        <slot name="actions" />
      </div>
    </header>
    <div v-if="loading" class="page-loading fade-up">加载中…</div>
    <div v-else-if="error" class="page-error fade-up">
      <span>数据加载失败：{{ error }}</span>
      <button class="page-error__btn" @click="$emit('retry')">重试</button>
    </div>
    <div v-else class="page-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title:    { type: String, default: '' },
  subtitle: { type: String, default: '' },
  loading:  { type: Boolean, default: false },
  error:    { type: String, default: '' },
})
defineEmits(['retry'])
</script>

<style scoped>
.page-shell { display: flex; flex-direction: column; gap: 16px; min-height: 100%; }
.page-head {
  display: flex; justify-content: space-between; align-items: flex-end;
  flex-wrap: wrap; gap: 12px;
}
.page-title { margin: 0; font-size: var(--fs-2xl); font-weight: 700; color: var(--c-text); }
.page-sub { margin: 4px 0 0; color: var(--c-muted); font-size: var(--fs-sm); }
.page-head__actions { display: flex; gap: 8px; align-items: center; }
.page-body { display: flex; flex-direction: column; gap: 14px; }
.page-loading, .page-error {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  padding: 60px 20px; color: var(--c-muted);
  background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r);
}
.page-error__btn {
  padding: 4px 12px; border: 1px solid var(--c-border-strong); border-radius: var(--r-sm);
  background: var(--c-surface-2); color: var(--c-text); cursor: pointer;
  transition: border-color var(--t-fast) var(--ease-out);
}
.page-error__btn:hover { border-color: var(--c-primary); color: var(--c-primary); }
</style>
