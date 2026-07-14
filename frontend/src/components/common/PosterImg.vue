<template>
  <div class="poster" :style="ratioStyle" :data-state="state" @click="onClick">
    <img
      v-if="resolvedSrc"
      :src="resolvedSrc"
      :alt="alt || ''"
      :loading="lazy ? 'lazy' : 'eager'"
      decoding="async"
      referrerpolicy="no-referrer"
      @load="onLoad"
      @error="onError"
      v-show="state === 'loaded'"
    />
    <div v-if="state === 'loading'" class="poster__skeleton" />
    <div v-if="state !== 'loaded'" class="poster__placeholder" aria-hidden="true">
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <circle cx="8.5" cy="8.5" r="1.5"/>
        <path d="M21 15l-5-5L5 21"/>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { posterUrl } from '../../utils/format'

const props = defineProps({
  src:     { type: String, default: '' },
  alt:     { type: String, default: '' },
  ratio:   { type: String, default: '2 / 3' },
  lazy:    { type: Boolean, default: true },
  stopPropagation: { type: Boolean, default: false },
})
const emit = defineEmits(['click'])

const state = ref('loading')
const resolvedSrc = computed(() => props.src ? posterUrl(props.src) : '')
const ratioStyle = computed(() => ({ aspectRatio: props.ratio }))

function onLoad() { state.value = 'loaded' }
function onError() { state.value = 'error' }
function onClick(e) {
  if (props.stopPropagation) e.stopPropagation()
  emit('click', e)
}
</script>

<style scoped>
.poster {
  position: relative;
  display: block;
  width: 100%;
  background: var(--c-surface-2);
  border-radius: 8px;
  overflow: hidden;
  isolation: isolate;
}
.poster img {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
  opacity: 0;
  transition: opacity .25s var(--ease-out);
}
.poster[data-state="loaded"] img { opacity: 1; }
.poster__skeleton {
  position: absolute; inset: 0;
  background: linear-gradient(90deg, var(--c-surface-2) 0%, var(--c-border) 50%, var(--c-surface-2) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}
.poster__placeholder {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  color: var(--c-muted);
  background: var(--c-surface-2);
}
</style>