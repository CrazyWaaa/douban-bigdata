<template>
  <div ref="el" class="echart-wrapper" :style="wrapperStyle"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch, computed, nextTick } from 'vue'
import { ensureRegistered } from '../echarts/echarts-setup'

const echarts = ensureRegistered()
const props = defineProps({
  option:   { type: Object, required: true },
  height:   { type: String, default: '360px' },
  fill:     { type: Boolean, default: false },
  theme:    { type: String, default: 'douban' },
  notMerge: { type: Boolean, default: true },
})
const emit = defineEmits(['itemClick'])

const el = ref(null)
let chart = null
let ro = null

// fill 模式：让容器填满父容器（父容器必须能提供一个可测量的高度，例如 flex:1 + min-height:0）
const wrapperStyle = computed(() => {
  if (props.fill) return { height: '100%' }
  return { height: props.height }
})

onMounted(async () => {
  // 下一帧再 init，确保父 flex 容器的尺寸计算已完成
  await nextTick()
  chart = echarts.init(el.value, props.theme, { renderer: 'canvas' })
  chart.setOption(props.option, props.notMerge)
  ro = new ResizeObserver(() => chart && chart.resize())
  ro.observe(el.value)
  chart.on('click', (params) => {
    if (params && params.data != null) emit('itemClick', params)
  })
})

onBeforeUnmount(() => {
  if (ro) ro.disconnect()
  if (chart) { chart.dispose(); chart = null }
})

watch(() => props.option, (o) => { if (chart) chart.setOption(o, true) }, { deep: true })
</script>

<style scoped>
.echart-wrapper { width: 100%; min-width: 0; }
</style>
