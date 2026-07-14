<template>
  <div ref="el" class="kpi-bar" :class="{ 'is-draggable': draggable }" @pointerdown="onPointerDown" @pointermove="onPointerMove" @pointerup="onPointerUp" @pointerleave="onPointerUp">
    <div class="kpi-bar__inner" :style="{ transform: `translateX(${translateX}px)` }">
      <slot />
    </div>
    <div class="kpi-bar__edge kpi-bar__edge--left" v-if="canScrollLeft" />
    <div class="kpi-bar__edge kpi-bar__edge--right" v-if="canScrollRight" />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  speed: { type: Number, default: 40 },        // 自动滚动 px/s（desktop）
  draggable: { type: Boolean, default: true },// 移动端可拖
  autoplay: { type: Boolean, default: false },// 大屏关闭：桌面端不滚
  pauseOnHover: { type: Boolean, default: true },
})

const el = ref(null)
const translateX = ref(0)
const canScrollLeft = ref(false)
const canScrollRight = ref(true)
let raf = 0
let lastTs = 0
let pointerStartX = 0
let pointerStartTx = 0
let dragging = false

function meta() {
  if (!el.value) return { scrollable: 0 }
  const inner = el.value.querySelector('.kpi-bar__inner')
  if (!inner) return { scrollable: 0 }
  return { scrollable: inner.scrollWidth - el.value.clientWidth }
}

function tick(ts) {
  if (!lastTs) lastTs = ts
  const dt = ts - lastTs
  lastTs = ts
  const m = meta()
  if (m.scrollable > 0) {
    const next = translateX.value - (props.speed * dt) / 1000
    if (next <= -m.scrollable) {
      translateX.value = -m.scrollable
      updateEdges()
      return
    }
    translateX.value = next
    updateEdges()
  }
  raf = requestAnimationFrame(tick)
}

function startAutoplay() {
  if (!props.autoplay) return
  if (raf) cancelAnimationFrame(raf)
  lastTs = 0
  raf = requestAnimationFrame(tick)
}

function stopAutoplay() {
  if (raf) { cancelAnimationFrame(raf); raf = 0 }
}

function updateEdges() {
  const m = meta()
  canScrollLeft.value = translateX.value < -2
  canScrollRight.value = translateX.value > -m.scrollable + 2
}

function clamp(v) {
  const m = meta()
  if (m.scrollable <= 0) return 0
  return Math.max(-m.scrollable, Math.min(0, v))
}

function onPointerDown(e) {
  if (!props.draggable) return
  stopAutoplay()
  dragging = true
  pointerStartX = e.clientX
  pointerStartTx = translateX.value
  el.value.setPointerCapture?.(e.pointerId)
}
function onPointerMove(e) {
  if (!dragging) return
  translateX.value = clamp(pointerStartTx + (e.clientX - pointerStartX))
  updateEdges()
}
function onPointerUp() {
  if (!dragging) return
  dragging = false
  startAutoplay()
}

onMounted(async () => {
  await nextTick()
  updateEdges()
  startAutoplay()
  window.addEventListener('resize', updateEdges)
})
onBeforeUnmount(() => {
  stopAutoplay()
  window.removeEventListener('resize', updateEdges)
})
</script>

<style scoped>
.kpi-bar {
  position: relative;
  width: 100%;
  overflow: hidden;
  touch-action: pan-x;
}
.kpi-bar.is-draggable { cursor: grab; }
.kpi-bar.is-draggable:active { cursor: grabbing; }
.kpi-bar__inner {
  display: flex; gap: 12px;
  will-change: transform;
  padding: 4px 2px 8px;
}
.kpi-bar__inner > * { flex: 1; min-width: 140px; max-width: 220px; }
.kpi-bar__edge {
  position: absolute; top: 0; bottom: 0; width: 36px;
  pointer-events: none;
}
.kpi-bar__edge--left {
  left: 0;
  background: linear-gradient(90deg, var(--c-bg), transparent);
}
.kpi-bar__edge--right {
  right: 0;
  background: linear-gradient(270deg, var(--c-bg), transparent);
}
</style>
