<template>
  <div ref="el" class="marquee" :class="{ 'is-paused': paused }">
    <div class="marquee__track" :style="trackStyle">
      <div class="marquee__group">
        <slot :items="items" />
      </div>
      <div class="marquee__group" aria-hidden="true">
        <slot :items="items" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
  speed: { type: Number, default: 50 }, // px/s
  pauseOnHover: { type: Boolean, default: true },
  separator: { type: String, default: '' },
})

const el = ref(null)
const paused = ref(false)
const offset = ref(0)
let raf = 0
let lastTs = 0
const halfWidth = ref(0)

const trackStyle = computed(() => ({
  transform: `translate3d(${offset.value}px, 0, 0)`,
  transition: paused.value ? 'transform 0.4s var(--ease-out)' : 'none',
  animationPlayState: paused.value ? 'paused' : 'running',
}))

function tick(ts) {
  if (!lastTs) lastTs = ts
  const dt = ts - lastTs
  lastTs = ts
  if (halfWidth.value > 0) {
    offset.value -= (props.speed * dt) / 1000
    if (-offset.value >= halfWidth.value) {
      offset.value += halfWidth.value
    }
  }
  raf = requestAnimationFrame(tick)
}

function measure() {
  const track = el.value?.querySelector('.marquee__track')
  const first = track?.querySelector('.marquee__group')
  if (first) halfWidth.value = first.scrollWidth + 16
  raf = requestAnimationFrame(tick)
}

function onEnter() { if (props.pauseOnHover) paused.value = true }
function onLeave() { paused.value = false }

onMounted(() => {
  // 等一帧让布局稳定
  setTimeout(measure, 0)
  window.addEventListener('resize', measure)
})
onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', measure)
})
</script>

<style scoped>
.marquee {
  position: relative;
  width: 100%;
  overflow: hidden;
  mask-image: linear-gradient(90deg, transparent 0, #000 6%, #000 94%, transparent 100%);
  -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 6%, #000 94%, transparent 100%);
}
.marquee__track {
  display: flex;
  width: max-content;
  gap: 16px;
  will-change: transform;
  align-items: stretch;
}
.marquee__group {
  display: flex; gap: 16px; padding: 4px 8px;
  align-items: stretch;
}
.marquee__group > * { flex-shrink: 0; }
.marquee.is-paused .marquee__track { cursor: pointer; }
</style>
