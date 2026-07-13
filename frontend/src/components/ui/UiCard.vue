<template>
  <div :class="['ui-card', { 'is-hoverable': hoverable, 'is-elevated': elevated, 'is-glow': glow }]">
    <header v-if="title || $slots.header" class="ui-card__head">
      <div class="ui-card__title">
        <span v-if="icon" class="ui-card__icon" aria-hidden="true">{{ icon }}</span>
        <h3 v-if="title">{{ title }}</h3>
        <slot name="header" />
      </div>
      <div v-if="$slots.actions" class="ui-card__actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="ui-card__body" :style="bodyStyle">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  icon: { type: String, default: '' },
  hoverable: { type: Boolean, default: false },
  elevated: { type: Boolean, default: true },
  glow: { type: Boolean, default: false },
  bodyStyle: { type: Object, default: () => ({}) },
});
</script>

<style scoped>
.ui-card {
  position: relative;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform var(--t) var(--ease-out),
              border-color var(--t) var(--ease-out),
              box-shadow var(--t) var(--ease-out);
}
.ui-card.is-elevated { box-shadow: var(--shadow); }
.ui-card.is-hoverable { cursor: pointer; }
.ui-card.is-hoverable:hover {
  transform: translateY(-3px);
  border-color: var(--c-primary);
  box-shadow: var(--shadow-lg);
}
.ui-card.is-glow::before {
  content: ''; position: absolute; inset: 0; pointer-events: none;
  border-radius: inherit;
  box-shadow: var(--glow);
  opacity: 0; transition: opacity var(--t) var(--ease-out);
}
.ui-card.is-glow:hover::before { opacity: 1; }
.ui-card__head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid var(--c-border);
  background: linear-gradient(180deg, var(--c-surface-2) 0%, transparent 100%);
  flex: 0 0 auto;
}
.ui-card__title { display: flex; align-items: center; gap: 8px; min-width: 0; }
.ui-card__title h3 { margin: 0; font-size: var(--fs-md); font-weight: 600; color: var(--c-text); }
.ui-card__icon { font-size: 16px; line-height: 1; }
.ui-card__actions { display: flex; gap: 6px; align-items: center; }
.ui-card__body { padding: 12px 14px; flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; }
.ui-card__body > * { min-width: 0; }
</style>
