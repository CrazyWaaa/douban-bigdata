<template>
  <div ref="el" :style="{ height: height }"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '360px' }
})

const el = ref(null)
let chart = null
const ro = new ResizeObserver(() => chart && chart.resize())

onMounted(() => {
  chart = echarts.init(el.value)
  chart.setOption(props.option)
  ro.observe(el.value)
})
onBeforeUnmount(() => { ro.disconnect(); chart && chart.dispose() })

watch(() => props.option, (o) => chart && chart.setOption(o, true), { deep: true })
</script>