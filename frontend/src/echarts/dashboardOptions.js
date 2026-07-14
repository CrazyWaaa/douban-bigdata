/**
 * ECharts option 工厂(集中管理大屏用图)
 *  输入:真实的 API 返回数组;输出稳定的 option(主题切换时不再重建)
 *  设计原则:
 *   - 不允许隐式依赖全局变量
 *   - 数据先归一化(过滤 null/0/越界),再下钻
 *   - 配色与字号走 CSS 变量(--c-text / --c-muted 等)
 */
import { formatRating } from '../utils/format'

/** 取 CSS 变量值(echarts 不能直接读 CSS 变量,只能拿计算值) */
function readVar(name, fallback = '') {
  if (typeof window === 'undefined') return fallback
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return v || fallback
}

/** 主题快照:ECharts 重绘/主题切换前调用一次,缓存到调用栈的闭包变量 */
function themeSnapshot() {
  return {
    text:    readVar('--c-text',    '#e2e8f0'),
    muted:   readVar('--c-muted',   '#94a3b8'),
    border:  readVar('--c-border',  'rgba(148,163,184,.18)'),
    primary: readVar('--c-primary', '#22d3ee'),
    success: readVar('--c-success', '#34d399'),
    warning: readVar('--c-warning', '#f59e0b'),
    info:    readVar('--c-info',    '#38bdf8'),
    danger:  readVar('--c-danger',  '#fb7185'),
    surface: readVar('--c-surface', '#0f172a'),
    surface2: readVar('--c-surface-2', 'rgba(148,163,184,.08)'),
  }
}

/** 类型桶(bar+line)双轴:左数量,右平均分(0-10) */
export function buildGenreDualOption(rawGenres, opts = {}) {
  const t = themeSnapshot()
  const items = (rawGenres || []).filter((d) => d && d.name && Number.isFinite(d.count))
    .sort((a, b) => b.count - a.count)
    .slice(0, opts.limit ?? 12)
  const categories = items.map((d) => d.name)
  const counts     = items.map((d) => d.count)
  const ratings    = items.map((d) => Number(d.avg_rating || 0))
  const maxCount   = Math.max(1, ...counts)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, .92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (params) => {
        const idx = params[0].dataIndex
        const it = items[idx]
        const r = Number(it.avg_rating || 0).toFixed(1)
        return `<div style="font-weight:600;margin-bottom:4px">${it.name}</div>`
          + `<div>片单引用数: <b style="color:${t.primary}">${it.count}</b></div>`
          + `<div>平均评分: <b style="color:${t.warning}">${r}</b></div>`
      },
    },
    legend: { data: ['数量', '平均分'], textStyle: { color: t.muted }, top: 0, right: 0 },
    grid: { left: 38, right: 44, top: 28, bottom: 22, containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: t.muted, fontSize: 11, interval: 0, rotate: categories.length > 8 ? 24 : 0 },
      axisLine: { lineStyle: { color: t.border } },
    },
    yAxis: [
      {
        type: 'value',
        name: '片单引用',
        nameTextStyle: { color: t.muted, fontSize: 10 },
        axisLabel: { color: t.muted, fontSize: 10 },
        splitLine: { lineStyle: { color: t.border, type: 'dashed' } },
      },
      {
        type: 'value',
        name: '平均分',
        min: 0, max: 10,
        nameTextStyle: { color: t.muted, fontSize: 10 },
        axisLabel: { color: t.muted, fontSize: 10 },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '数量',
        type: 'bar',
        data: counts,
        barMaxWidth: 22,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: t.primary }, { offset: 1, color: 'rgba(34,211,238,.12)' }] },
        },
      },
      {
        name: '平均分',
        type: 'line',
        yAxisIndex: 1,
        data: ratings,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: t.warning, width: 2 },
        itemStyle: { color: t.warning },
      },
    ],
  }
}

/** 年代趋势:左 count,右 avg_rating。slice 后的年份序列 */
export function buildYearTrendOption(rawYear, opts = {}) {
  const t = themeSnapshot()
  const items = (rawYear || []).filter((d) => d && Number.isFinite(d.count))
    .slice(0, opts.limit ?? 20)
  const cats = items.map((d) => `${d.year ?? d.name ?? ''}`)
  const counts = items.map((d) => d.count)
  const ratings = items.map((d) => Number(d.avg_rating || 0))

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, .92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (params) => {
        const idx = params[0].dataIndex
        const it = items[idx]
        return `<div style="font-weight:600;margin-bottom:4px">${it.year || it.name}</div>`
          + `<div>片数: <b style="color:${t.primary}">${it.count}</b></div>`
          + `<div>平均分: <b style="color:${t.warning}">${formatRating(it.avg_rating)}</b></div>`
      },
    },
    grid: { left: 38, right: 44, top: 18, bottom: 24, containLabel: true },
    xAxis: { type: 'category', data: cats, axisLabel: { color: t.muted, fontSize: 10 }, axisLine: { lineStyle: { color: t.border } } },
    yAxis: [
      { type: 'value', name: '片数', axisLabel: { color: t.muted, fontSize: 10 }, splitLine: { lineStyle: { color: t.border, type: 'dashed' } } },
      { type: 'value', name: '均分', min: 0, max: 10, axisLabel: { color: t.muted, fontSize: 10 }, splitLine: { show: false } },
    ],
    series: [
      {
        name: '片数', type: 'bar', data: counts, barMaxWidth: 18,
        itemStyle: {
          borderRadius: [3, 3, 0, 0],
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: t.info }, { offset: 1, color: 'rgba(56,189,248,.1)' }] },
        },
      },
      {
        name: '均分', type: 'line', yAxisIndex: 1, data: ratings, smooth: true,
        symbol: 'circle', symbolSize: 5,
        lineStyle: { color: t.warning, width: 2 }, itemStyle: { color: t.warning },
      },
    ],
  }
}

/** 评分环形(用真实桶,不补默认) */
export function buildRatingRingOption(rawDist) {
  const t = themeSnapshot()
  const items = (rawDist || []).filter((d) => d && typeof d.bucket === 'string')
  const total = items.reduce((s, x) => s + (x.count || 0), 0)
  const data = items.map((d, i) => ({
    name: d.bucket,
    value: d.count,
    itemStyle: { color: [t.danger, t.warning, t.primary, t.success][i] || t.muted },
  }))
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, .92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (p) => `${p.name}<br/><b style="color:${t.primary}">${p.value}</b> 部 (${p.percent}%)`,
    },
    legend: { bottom: 0, textStyle: { color: t.muted, fontSize: 11 } },
    series: [{
      type: 'pie',
      radius: ['52%', '78%'],
      center: ['50%', '46%'],
      avoidLabelOverlap: true,
      label: { color: t.text, formatter: (p) => `${p.name}\n${p.value} 部`, fontSize: 11 },
      labelLine: { length: 8, length2: 6 },
      data,
      animationDuration: 700,
      animationEasing: 'cubicOut',
    }],
    graphic: total === 0 ? [{
      type: 'text', left: 'center', top: '38%',
      style: { text: '暂无评分数据', fill: t.muted, fontSize: 12 },
    }] : undefined,
  }
}

/** 国家横向条形(自动剔除长名桶次要项) */
export function buildCountryBarOption(rawCountries, opts = {}) {
  const t = themeSnapshot()
  const items = (rawCountries || []).filter((d) => d && d.name && Number.isFinite(d.count))
    .sort((a, b) => b.count - a.count)
    .slice(0, opts.limit ?? 10)
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15, 23, 42, .92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (params) => {
        const idx = params[0].dataIndex
        const it = items[idx]
        return `<div style="font-weight:600;margin-bottom:4px">${it.name}</div>`
          + `<div>片数: <b style="color:${t.primary}">${it.count}</b></div>`
          + `<div>平均分: <b style="color:${t.warning}">${formatRating(it.avg_rating)}</b></div>`
      },
    },
    grid: { left: 90, right: 24, top: 12, bottom: 12, containLabel: true },
    xAxis: { type: 'value', axisLabel: { color: t.muted, fontSize: 10 }, splitLine: { lineStyle: { color: t.border, type: 'dashed' } } },
    yAxis: {
      type: 'category', data: items.map((d) => d.name).reverse(),
      axisLabel: { color: t.text, fontSize: 11 },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [{
      type: 'bar',
      data: items.map((d) => d.count).reverse(),
      barMaxWidth: 14,
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [{ offset: 0, color: 'rgba(34,211,238,.12)' }, { offset: 1, color: t.primary }] },
      },
      label: { show: true, position: 'right', color: t.muted, fontSize: 11, formatter: (p) => formatRating(items[items.length - 1 - p.dataIndex].avg_rating) },
    }],
  }
}