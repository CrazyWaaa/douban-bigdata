<template>
  <div :class="['ui-skel', { 'ui-skel--text': variant === 'text', 'ui-skel--circle': variant === 'circle' }]"
       :style="{ width: typeof width === 'number' ? width + 'px' : width, height: typeof height === 'number' ? height + 'px' : height }">
  </div>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'block' },
  width:   { type: [String, Number], default: '100%' },
  height:  { type: [String, Number], default: '16px' },
});
</script>

<style scoped>
.ui-skel {
  display: inline-block;
  background: linear-gradient(90deg, var(--c-surface-2) 0%, var(--c-border) 50%, var(--c-surface-2) 100%);
  background-size: 200% 100%;
  border-radius: 6px;
  animation: shimmer 1.4s linear infinite;
}
.ui-skel--text { border-radius: 4px; }
.ui-skel--circle { border-radius: 50%; }
</style>
