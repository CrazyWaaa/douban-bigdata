// 按需注册 ECharts 模块 —— 首屏只引入用到的图表，体积从 ~1MB 砍到 ~400KB
import * as echarts from 'echarts/core'
import {
  BarChart, LineChart, PieChart, ScatterChart, RadarChart, EffectScatterChart,
} from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
  DataZoomComponent, MarkLineComponent, MarkPointComponent, MarkAreaComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

const doubanTheme = {
  color: ['#38bdf8', '#f59e0b', '#34d399', '#a78bfa', '#f472b6', '#22d3ee', '#fb923c'],
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

echarts.registerTheme('douban', doubanTheme)

let registered = false
export function ensureRegistered() {
  if (registered) return echarts
  registered = true
  echarts.use([
    BarChart, LineChart, PieChart, ScatterChart, RadarChart, EffectScatterChart,
    GridComponent, TooltipComponent, LegendComponent, TitleComponent,
    DataZoomComponent, MarkLineComponent, MarkPointComponent, MarkAreaComponent,
    CanvasRenderer,
  ])
  return echarts
}

export default ensureRegistered
