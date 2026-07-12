<template>
  <UiCard :title="title" :hoverable="false" :body-style="{ padding: '12px 12px 8px' }">
    <template #actions>
      <span v-if="sub" class="muted" style="font-size: var(--fs-xs)">{{ sub }}</span>
      <slot name="actions" />
    </template>
    <div v-if="loading" class="ui-chart__skeleton">
      <div class="ui-skel ui-skel--bar" v-for="i in 4" :key="i" :style="{ height: 10 + (i*4) + 'px' }"></div>
    </div>
    <div v-else-if="error" class="ui-chart__error">
      <div>加载失败</div>
      <UiButton size="sm" variant="ghost" @click="$emit('retry')">重试</UiButton>
    </div>
    <slot v-else />
  </UiCard>
</template>

<script setup>
import UiCard from './UiCard.vue';
import UiButton from './UiButton.vue';
defineProps({
  title: { type: String, required: true },
  sub: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: [Boolean, String], default: false },
});
defineEmits(['retry']);
</script>

<style scoped>
.ui-chart__skeleton { display: flex; flex-direction: column; gap: 10px; padding: 12px 8px; }
.ui-skel {
  background: linear-gradient(90deg, var(--c-surface-2) 0%, var(--c-border) 50%, var(--c-surface-2) 100%);
  background-size: 200% 100%;
  border-radius: 6px;
  animation: shimmer 1.4s linear infinite;
}
.ui-chart__error {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  color: var(--c-muted); padding: 32px 0; font-size: var(--fs-sm);
}
</style>
