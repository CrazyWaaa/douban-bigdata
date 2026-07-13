<template>
  <div ref="el" class="echart-wrapper" :style="wrapperStyle"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch, computed, nextTick, onActivated, onDeactivated } from 'vue'
import { ensureRegistered, resolveThemeName } from '../echarts/echarts-setup'

const echarts = ensureRegistered()
const props = defineProps({
  option:   { type: Object, required: true },
  height:   { type: String, default: '360px' },
  fill:     { type: Boolean, default: false },
  theme:    { type: String, default: 'douban' },
  notMerge: { type: Boolean, default: false },
  // 暴露给需要用 echarts 底层 API 的调用方(如 3D 图、地图)
  onChart:  { type: Function, default: null },
})
const emit = defineEmits(['itemClick', 'chartReady'])

const el = ref(null)
let chart = null
let ro = null
let themeObserver = null
let currentThemeName = ''

const wrapperStyle = computed(() => {
  if (props.fill) return { height: '100%' }
  return { height: props.height }
})

function initChart() {
  if (!el.value) return
  currentThemeName = resolveThemeName(props.theme)
  chart = echarts.init(el.value, currentThemeName, { renderer: 'canvas' })
  chart.setOption(props.option, props.notMerge)
  if (typeof props.onChart === 'function') props.onChart(chart)
  emit('chartReady', chart)
  chart.on('click', (params) => {
    if (params && params.data != null) emit('itemClick', params)
  })
  ro = new ResizeObserver(() => chart && chart.resize())
  ro.observe(el.value)
}

function reinitForTheme() {
  // 主题切换:保留数据,dispose 后用新主题重建
  const cached = chart ? chart.getOption() : props.option
  if (chart) { chart.dispose(); chart = null }
  if (ro) { ro.disconnect(); ro = null }
  initChart()
  if (cached) chart && chart.setOption(cached, true)
}

onMounted(async () => {
  await nextTick()
  initChart()
  // 监听 data-theme 变化
  if (typeof MutationObserver !== 'undefined' && document?.documentElement) {
    themeObserver = new MutationObserver(() => {
      const newName = resolveThemeName(props.theme)
      if (newName !== currentThemeName) reinitForTheme()
    })
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
  }
})

onBeforeUnmount(() => {
  if (themeObserver) themeObserver.disconnect()
  if (ro) ro.disconnect()
  if (chart) { chart.dispose(); chart = null }
})

watch(() => props.option, (o) => { if (chart) chart.setOption(o, props.notMerge) }, { deep: true })
</script>

<style scoped>
.echart-wrapper { width: 100%; min-width: 0; }
</style>
