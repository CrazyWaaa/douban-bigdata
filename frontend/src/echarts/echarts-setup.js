import * as echarts from 'echarts'
import worldGeoJson from '../assets/world.json'

// 深色主色板:青蓝主导 + 紫/粉/绿/橙点缀
const DARK_COLORS = ['#38bdf8', '#f59e0b', '#34d399', '#a78bfa', '#f472b6', '#22d3ee', '#fb923c', '#fb7185', '#a3e635', '#60a5fa']

// 浅色主色板:同色相加深一档,保证对比度
const LIGHT_COLORS = ['#0284c7', '#d97706', '#059669', '#7c3aed', '#db2777', '#0891b2', '#ea580c', '#e11d48', '#65a30d', '#2563eb']

const doubanTheme = {
  color: DARK_COLORS,
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif',
    color: '#cbd5e1',
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: 'rgba(148,163,184,.25)' } },
    axisTick: { show: false },
    axisLabel: { color: '#94a3b8' },
    splitLine: { show: false },
  },
  valueAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: 'rgba(148,163,184,.12)' } },
  },
  tooltip: {
    backgroundColor: 'rgba(15, 23, 42, .92)',
    borderColor: 'rgba(56,189,248,.4)',
    borderWidth: 1,
    textStyle: { color: '#e6edf7' },
    extraCssText: 'backdrop-filter: blur(8px); border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,.45);',
  },
  line: { smooth: true, lineStyle: { width: 2.5 }, symbolSize: 7, symbol: 'circle' },
}

const doubanLightTheme = {
  color: LIGHT_COLORS,
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif',
    color: '#0f172a',
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: 'rgba(15, 23, 42, .18)' } },
    axisTick: { show: false },
    axisLabel: { color: '#475569' },
    splitLine: { show: false },
  },
  valueAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#475569' },
    splitLine: { lineStyle: { color: 'rgba(15, 23, 42, .08)' } },
  },
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, .96)',
    borderColor: 'rgba(2, 132, 199, .35)',
    borderWidth: 1,
    textStyle: { color: '#0f172a' },
    extraCssText: 'backdrop-filter: blur(8px); border-radius: 8px; box-shadow: 0 8px 24px rgba(15, 23, 42, .14);',
  },
  line: { smooth: true, lineStyle: { width: 2.5 }, symbolSize: 7, symbol: 'circle' },
}

echarts.registerMap('world', worldGeoJson)

echarts.registerTheme('douban', doubanTheme)
echarts.registerTheme('doubanLight', doubanLightTheme)

/** 解析最终主题:外部传 'douban' 时按当前 data-theme 路由到对应主题 */
export function resolveThemeName(name) {
  if (name !== 'douban') return name
  if (typeof document === 'undefined') return 'douban'
  const t = document.documentElement.getAttribute('data-theme')
  return t === 'light' ? 'doubanLight' : 'douban'
}

/** 当前主题对应的色板(给 option 工厂用,需要手动写色时取这个) */
export function getThemePalette() {
  if (typeof document !== 'undefined' && document.documentElement.getAttribute('data-theme') === 'light') {
    return LIGHT_COLORS
  }
  return DARK_COLORS
}

/** 主题感知 tooltip 样式(给不依赖主题的 option 工厂用) */
export function getThemeTooltip() {
  if (typeof document !== 'undefined' && document.documentElement.getAttribute('data-theme') === 'light') {
    return doubanLightTheme.tooltip
  }
  return doubanTheme.tooltip
}

export function ensureRegistered() {
  return echarts
}

export default ensureRegistered
