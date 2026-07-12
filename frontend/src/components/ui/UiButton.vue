<template>
  <button
    :class="['ui-btn', `ui-btn--${variant}`, `ui-btn--${size}`, { 'is-loading': loading, 'is-block': block }]"
    :disabled="disabled || loading"
    @click="onClick"
  >
    <span v-if="loading" class="ui-btn__spinner" aria-hidden="true"></span>
    <span v-else-if="$slots.icon" class="ui-btn__icon"><slot name="icon" /></span>
    <span class="ui-btn__label"><slot /></span>
  </button>
</template>

<script setup>
const props = defineProps({
  variant: { type: String, default: 'primary' },
  size:    { type: String, default: 'md' },
  loading: { type: Boolean, default: false },
  disabled:{ type: Boolean, default: false },
  block:   { type: Boolean, default: false },
});
const emit = defineEmits(['click']);
function onClick(e) { if (!props.disabled && !props.loading) emit('click', e); }
</script>

<style scoped>
.ui-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  border-radius: var(--r-sm);
  font-weight: 500; line-height: 1;
  cursor: pointer; user-select: none;
  transition: background var(--t-fast) var(--ease-out),
              color var(--t-fast) var(--ease-out),
              border-color var(--t-fast) var(--ease-out),
              transform var(--t-fast) var(--ease-out),
              box-shadow var(--t-fast) var(--ease-out);
  border: 1px solid transparent;
  white-space: nowrap;
}
.ui-btn:active:not(:disabled) { transform: translateY(1px); }
.ui-btn:disabled { opacity: .5; cursor: not-allowed; }
.ui-btn.is-block { width: 100%; }
.ui-btn--sm { padding: 5px 10px; font-size: var(--fs-sm); }
.ui-btn--md { padding: 8px 14px; font-size: var(--fs-md); }
.ui-btn--lg { padding: 10px 18px; font-size: var(--fs-md); }
.ui-btn--primary { background: var(--c-primary); color: #0b1020; }
.ui-btn--primary:hover:not(:disabled) { background: var(--c-primary-soft); box-shadow: var(--shadow-sm); }
.ui-btn--ghost { background: transparent; color: var(--c-text); border-color: var(--c-border); }
.ui-btn--ghost:hover:not(:disabled) { border-color: var(--c-primary); color: var(--c-primary); }
.ui-btn--outline { background: transparent; color: var(--c-primary); border-color: var(--c-primary); }
.ui-btn--outline:hover:not(:disabled) { background: var(--c-primary-tint); }
.ui-btn--danger { background: var(--c-danger); color: #fff; }
.ui-btn--danger:hover:not(:disabled) { filter: brightness(1.1); }
.ui-btn__spinner {
  width: 12px; height: 12px; border-radius: 50%;
  border: 2px solid currentColor; border-right-color: transparent;
  animation: spin .8s linear infinite;
}
</style>
