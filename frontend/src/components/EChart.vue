<template>
  <div ref="el" :style="{ height: height }"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { ensureRegistered } from '../echarts/echarts-setup'

const echarts = ensureRegistered()
const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '360px' },
  theme:  { type: String, default: 'douban' },
  notMerge: { type: Boolean, default: true },
})

const el = ref(null)
let chart = null
let ro = null

onMounted(() => {
  chart = echarts.init(el.value, props.theme, { renderer: 'canvas' })
  chart.setOption(props.option, props.notMerge)
  ro = new ResizeObserver(() => chart && chart.resize())
  ro.observe(el.value)
})

onBeforeUnmount(() => {
  if (ro) ro.disconnect()
  if (chart) { chart.dispose(); chart = null }
})

watch(() => props.option, (o) => { if (chart) chart.setOption(o, true) }, { deep: true })
</script>
