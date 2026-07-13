// 复用的图表 option 工厂：渐变面积折线 / 玫瑰图 / 横向排名条

export function buildAreaLineOption(items, opts) {
  const color = (opts && opts.color) || '#38bdf8'
  const label = (opts && opts.label) || ''
  const max = (opts && opts.max) || null
  const data = (items || []).map(function (d) {
    return { name: String(d.name != null ? d.name : (d.year != null ? d.year : (d.bucket != null ? d.bucket : ''))), value: (d.count != null ? d.count : (d.value != null ? d.value : 0)) }
  })
  var peakIdx = 0
  for (var i = 1; i < data.length; i++) if (data[i].value > data[peakIdx].value) peakIdx = i
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', lineStyle: { color: 'rgba(56,189,248,.3)' } },
      formatter: function (params) {
        var p = params[0]
        var pt = data[p.dataIndex]
        var s = ''
        s += '<div style="font-weight:600;margin-bottom:4px;">' + pt.name + '</div>'
        s += '<div>数量: <b>' + pt.value + '</b></div>'
        return s
      },
    },
    grid: { left: 8, right: 16, top: 24, bottom: 28, containLabel: true },
    xAxis: {
      type: 'category', data: data.map(function (d) { return d.name }), boundaryGap: false,
      axisLabel: { color: '#94a3b8', fontSize: 11, hideOverlap: true },
    },
    yAxis: { type: 'value', max: max != null ? max : undefined, axisLabel: { color: '#94a3b8', fontSize: 11 } },
    series: [{
      type: 'line', name: label,
      data: data.map(function (d) { return d.value }),
      smooth: true,
      symbol: 'circle',
      symbolSize: function (val, idx) { return idx === peakIdx ? 10 : 6 },
      showSymbol: true,
      lineStyle: { width: 2.5, color: color, shadowColor: color, shadowBlur: 12 },
      itemStyle: { color: color, borderColor: '#0b1020', borderWidth: 2 },
      emphasis: { focus: 'series', scale: true },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + 'AA' },
            { offset: 1, color: color + '05' },
          ],
        },
      },
      markPoint: {
        symbol: 'circle', symbolSize: 14,
        itemStyle: { color: color, shadowBlur: 18, shadowColor: color },
        data: [{ type: 'max', name: '峰值' }],
      },
      markLine: { silent: true, symbol: 'none', lineStyle: { color: 'rgba(148,163,184,.2)', type: 'dashed' }, data: [{ type: 'average' }] },
      animationDuration: 1200, animationEasing: 'cubicOut',
    }],
  }
}

export function buildPolarBarOption(items, opts) {
  const color = (opts && opts.color) || '#22d3ee'
  const accent = (opts && opts.accent) || '#f59e0b'
  const list = items || []
  const data = list.map(function (d, i) {
    return {
      name: (d.bucket != null ? d.bucket : d.name),
      value: (d.count != null ? d.count : (d.value != null ? d.value : 0)),
      itemStyle: { color: i === list.length - 1 ? accent : color },
    }
  })
  return {
    tooltip: { trigger: 'item', formatter: '{b}<br/>数量: <b>{c}</b>' },
    polar: { radius: '78%' },
    angleAxis: {
      type: 'category', data: data.map(function (d) { return d.name }), startAngle: 90,
      axisLine: { lineStyle: { color: 'rgba(148,163,184,.3)' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
    },
    radiusAxis: { show: false },
    series: [{
      type: 'bar', data: data,
      coordinateSystem: 'polar',
      roundCap: true, barWidth: '62%',
      itemStyle: { borderRadius: 6, opacity: 0.92 },
      label: { show: true, position: 'middle', color: '#e6edf7', fontWeight: 600 },
      animationDuration: 1400, animationEasing: 'cubicOut',
    }],
  }
}

export function buildRankedBarOption(items, opts) {
  const color = (opts && opts.color) || '#34d399'
  const top = (opts && opts.top) || 10
  const sliced = (items || []).slice(0, top).slice().reverse()
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 110, right: 36, top: 8, bottom: 28 },
    xAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 11 } },
    yAxis: {
      type: 'category', data: sliced.map(function (d) { return d.name }),
      axisLabel: {
        color: '#cbd5e1', fontSize: 12,
        formatter: function (val, idx) {
          var realIdx = sliced.length - 1 - idx
          var rank = realIdx + 1
          if (rank <= 3) return '{r' + rank + '|' + rank + '}  ' + val
          return rank + '. ' + val
        },
        rich: {
          r1: { color: '#f59e0b', fontWeight: 700, fontSize: 13 },
          r2: { color: '#94a3b8', fontWeight: 700, fontSize: 13 },
          r3: { color: '#fb923c', fontWeight: 700, fontSize: 13 },
        },
      },
    },
    series: [{
      type: 'bar',
      data: sliced.map(function (d) { return { value: (d.count != null ? d.count : (d.value != null ? d.value : 0)), name: d.name } }),
      itemStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [
          { offset: 0, color: color + '22' },
          { offset: 1, color: color },
        ]},
        borderRadius: [0, 6, 6, 0],
      },
      label: { show: true, position: 'right', color: '#e6edf7', fontWeight: 500 },
      animationDuration: 1200, animationEasing: 'cubicOut',
    }],
  }
}

// 类型分布 · 评分透镜：双轴复合图（条=数量 / 线=均分）
export function buildLensOption(items, opts) {
  const barColor = (opts && opts.barColor) || '#38bdf8'
  const lineColor = (opts && opts.lineColor) || '#f59e0b'
  const list = (items || []).slice(0, 10)
  const names = list.map(function (d) { return String(d.name != null ? d.name : '') })
  const counts = list.map(function (d) { return Number(d.count || 0) })
  const avgs = list.map(function (d) { return Number(d.avg_rating || 0) })
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: [{ type: 'shadow' }, { type: 'cross' }],
      formatter: function (params) {
        var idx = params[0].dataIndex
        var s = '<div style="font-weight:600;margin-bottom:4px;">' + names[idx] + '</div>'
        s += '<div>数量: <b>' + counts[idx] + '</b></div>'
        s += '<div>均分: <b>' + (avgs[idx] ? avgs[idx].toFixed(2) : '-') + '</b></div>'
        return s
      },
    },
    legend: { textStyle: { color: '#94a3b8' }, top: 0, right: 0, data: ['数量', '均分'] },
    grid: { left: 8, right: 16, top: 30, bottom: 24, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { color: '#94a3b8', fontSize: 11, hideOverlap: true, rotate: 30 } },
    yAxis: [
      { type: 'value', name: '数量', axisLabel: { color: '#94a3b8', fontSize: 11 }, splitLine: { lineStyle: { color: 'rgba(148,163,184,.12)' } } },
      { type: 'value', name: '均分', min: 0, max: 10, axisLabel: { color: '#94a3b8', fontSize: 11 }, splitLine: { show: false } },
    ],
    series: [
      {
        name: '数量', type: 'bar', yAxisIndex: 0, data: counts,
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [
            { offset: 0, color: barColor }, { offset: 1, color: barColor + '22' },
          ]},
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: '均分', type: 'line', yAxisIndex: 1, data: avgs, smooth: true,
        lineStyle: { color: lineColor, width: 2.5 },
        itemStyle: { color: lineColor },
        symbol: 'circle', symbolSize: 7,
        markPoint: { symbol: 'circle', symbolSize: 12, itemStyle: { color: lineColor }, data: [{ type: 'max', name: '峰值' }] },
      },
    ],
  }
}

// =====================================================================
// 高级图表工厂(全部接收 (items, opts) 形式,opts 用于覆盖颜色/尺寸等)
// =====================================================================

/**
 * Radar:多影片维度对比,默认维度:剧情/演技/视效/音乐/节奏
 * items: [{ name, values: [剧情,演技,视效,音乐,节奏] }]
 */
export function buildRadarOption(items, opts) {
  const palette = (opts && opts.palette) || ['#38bdf8', '#f59e0b', '#a78bfa', '#34d399', '#f472b6', '#22d3ee']
  const indicator = [
    { name: '剧情', max: 10 },
    { name: '演技', max: 10 },
    { name: '视效', max: 10 },
    { name: '音乐', max: 10 },
    { name: '节奏', max: 10 },
  ]
  const list = (items || []).slice(0, opts?.top || 6)
  return {
    tooltip: { trigger: 'item' },
    legend: {
      type: 'scroll', bottom: 0,
      textStyle: { color: 'var(--c-muted)', fontSize: 11 },
    },
    radar: {
      indicator,
      center: ['50%', '48%'],
      radius: '64%',
      splitNumber: 5,
      axisName: { color: '#94a3b8', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,.18)' } },
      splitArea: { areaStyle: { color: ['rgba(56,189,248,.04)', 'rgba(56,189,248,.08)'] } },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,.25)' } },
    },
    series: [{
      type: 'radar',
      data: list.map((d, i) => ({
        name: d.name,
        value: d.values,
        symbolSize: 6,
        lineStyle: { width: 2, color: palette[i % palette.length] },
        itemStyle: { color: palette[i % palette.length] },
        areaStyle: { color: palette[i % palette.length], opacity: 0.18 },
      })),
      animationDuration: 1200,
    }],
  }
}

/**
 * Sankey:三列能量流(类型→地区→年代)
 * items: [{ source, target, value }]
 */
export function buildSankeyOption(items, opts) {
  const palette = (opts && opts.palette) || ['#38bdf8', '#f59e0b', '#34d399', '#a78bfa', '#f472b6', '#22d3ee', '#fb923c']
  const links = (items || []).map((d, i) => ({
    source: d.source,
    target: d.target,
    value: d.value,
    lineStyle: { color: 'gradient', curveness: 0.5, opacity: 0.55 },
  }))
  return {
    tooltip: {
      trigger: 'item',
      formatter: (p) => {
        if (p.dataType === 'edge') return `${p.data.source} → ${p.data.target}<br/>影片数: <b>${p.data.value}</b>`
        return `${p.name}<br/>总流量: <b>${p.value}</b>`
      },
    },
    series: [{
      type: 'sankey',
      left: 8, right: 80, top: 16, bottom: 16,
      data: opts?.nodes || [],
      links,
      nodeAlign: 'left',
      nodeGap: 12,
      nodeWidth: 14,
      label: { color: '#cbd5e1', fontSize: 12, fontWeight: 500 },
      itemStyle: { color: '#38bdf8', borderColor: 'rgba(15,23,42,.6)', borderWidth: 1 },
      lineStyle: { color: 'gradient', opacity: 0.45, curveness: 0.5 },
      emphasis: { focus: 'adjacency' },
      animationDuration: 1200,
    }],
    color: palette,
  }
}

/**
 * Treemap:类型/地区嵌套树
 * items: [{ name, value, children? }]  二级结构
 */
export function buildTreemapOption(items, opts) {
  const palette = (opts && opts.palette) || ['#38bdf8', '#f59e0b', '#34d399', '#a78bfa', '#f472b6', '#22d3ee', '#fb923c', '#a3e635', '#60a5fa']
  const data = (items || []).filter((item) => Number(item.value) > 0).map((item, index) => ({
    ...item,
    itemStyle: { color: palette[index % palette.length] },
    children: (item.children || []).filter((child) => Number(child.value) > 0),
  }))
  return {
    tooltip: {
      formatter: (p) => `${p.name}<br/>数量: <b>${Number(p.value || 0)}</b>`,
    },
    series: [{
      type: 'treemap',
      roam: false,
      nodeClick: 'zoomToNode',
      breadcrumb: { show: true, bottom: 4, itemStyle: { color: '#334155', borderColor: '#475569' } },
      top: 8, left: 8, right: 8, bottom: 32,
      leafDepth: 2,
      label: {
        show: true,
        color: '#fff',
        fontSize: 12,
        overflow: 'truncate',
        formatter: (p) => `${p.name}\n${Number(p.value || 0)} 部`,
      },
      upperLabel: { show: true, height: 28, color: '#fff', fontSize: 13, fontWeight: 700 },
      itemStyle: { borderColor: '#0f172a', borderWidth: 2, gapWidth: 2 },
      levels: [
        { itemStyle: { gapWidth: 6, borderWidth: 0 } },
        { colorSaturation: [0.35, 0.65], itemStyle: { gapWidth: 2, borderWidth: 2 } },
        { colorSaturation: [0.2, 0.55], itemStyle: { gapWidth: 1, borderWidth: 1 } },
      ],
      data,
    }],
  }
}

export function buildWordCloudOption(items, opts) {
  const palette = (opts && opts.palette) || ['#38bdf8', '#f59e0b', '#34d399', '#a78bfa', '#f472b6', '#22d3ee', '#fb923c']
  const data = (items || []).filter((item) => item.name && Number(item.value) > 0)
  const max = Math.max(1, ...data.map((item) => Number(item.value)))
  const min = Math.min(...data.map((item) => Number(item.value)), max)
  return {
    tooltip: { show: true, formatter: '{b}<br/>出现: <b>{c}</b> 次' },
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      left: 'center', top: 'center',
      width: '92%', height: '92%',
      sizeRange: [14, 58],
      rotationRange: [-20, 20],
      rotationStep: 10,
      gridSize: 8,
      drawOutOfBound: false,
      shrinkToFit: true,
      layoutAnimation: true,
      textStyle: {
        fontFamily: '"PingFang SC", "Microsoft YaHei", sans-serif',
        fontWeight: 700,
        color: (params) => palette[params.dataIndex % palette.length],
      },
      emphasis: { focus: 'self', textStyle: { textShadowBlur: 10, textShadowColor: '#38bdf8' } },
      data: data.map((item) => ({
        ...item,
        value: Number(item.value),
        textStyle: { fontSize: 14 + ((Number(item.value) - min) / Math.max(1, max - min)) * 44 },
      })),
    }],
  }
}

export function buildGaugeOption(items, opts) {
  const list = items || []
  return {
    tooltip: { formatter: '{a} <br/>{b}: {c}' },
    series: list.map((d, i) => ({
      name: d.name,
      type: 'gauge',
      min: 0,
      max: d.max || 100,
      center: [`${((i + 0.5) * 100) / list.length}%`, '55%'],
      radius: '70%',
      startAngle: 200,
      endAngle: -20,
      axisLine: {
        lineStyle: {
          width: 14,
          color: [
            [0.6, '#f87171'],
            [0.8, '#f59e0b'],
            [1.0, d.color || '#34d399'],
          ],
        },
      },
      pointer: { length: '62%', width: 5, itemStyle: { color: d.color || '#38bdf8' } },
      axisTick: { length: 6, lineStyle: { color: 'rgba(148,163,184,.3)' } },
      splitLine: { length: 10, lineStyle: { color: 'rgba(148,163,184,.5)' } },
      axisLabel: { color: '#94a3b8', fontSize: 10, distance: -22 },
      title: { offsetCenter: [0, '70%'], color: '#94a3b8', fontSize: 12 },
      detail: { valueAnimation: true, color: '#e6edf7', fontSize: 22, fontWeight: 700, offsetCenter: [0, '40%'], formatter: '{value}' },
      data: [{ value: d.value, name: d.name }],
    })),
  }
}

export function buildFunnelOption(items, opts) {
  const palette = (opts && opts.palette) || ['#38bdf8', '#f59e0b', '#34d399', '#a78bfa', '#f472b6']
  return {
    tooltip: { trigger: 'item', formatter: '{b}<br/>数量: <b>{c}</b><br/>占比: <b>{d}%</b>' },
    legend: { textStyle: { color: '#94a3b8' }, bottom: 0, type: 'scroll' },
    series: [{
      type: 'funnel',
      left: '8%', right: '8%', top: 16, bottom: 36,
      width: '84%',
      min: 0,
      sort: 'descending',
      gap: 4,
      label: { show: true, position: 'inside', color: '#fff', fontWeight: 600 },
      labelLine: { length: 10, lineStyle: { width: 1 } },
      itemStyle: { borderColor: 'rgba(15,23,42,.6)', borderWidth: 1 },
      emphasis: { label: { fontSize: 16 } },
      data: (items || []).map((d, i) => ({
        ...d,
        itemStyle: { color: palette[i % palette.length] },
      })),
    }],
  }
}

/**
 * Calendar Heatmap:按年×月 的影片数热力
 * items: [{ date: 'YYYY-MM-DD', value: number }]
 */
export function buildCalendarOption(items, year, opts) {
  const y = year || new Date().getFullYear()
  const data = (items || []).map((item) => [item.date, Number(item.value || 0)])
  const max = Math.max(1, ...data.map((item) => item[1]))
  return {
    tooltip: { formatter: (p) => `${String(p.value[0]).slice(0, 7)}<br/>上映影片: <b>${p.value[1]}</b>` },
    visualMap: {
      min: 0, max, calculable: false,
      orient: 'horizontal', left: 'center', bottom: 0,
      text: ['多', '少'],
      inRange: { color: ['#172554', '#0ea5e9', '#8b5cf6', '#ec4899'] },
      textStyle: { color: '#94a3b8', fontSize: 10 },
    },
    calendar: {
      top: 34, left: 24, right: 24, bottom: 42,
      range: String(y),
      orient: 'horizontal',
      cellSize: ['auto', 18],
      itemStyle: { borderColor: 'rgba(15,23,42,.7)', borderWidth: 2, color: 'rgba(56,189,248,.04)' },
      splitLine: { show: false },
      yearLabel: { show: false },
      monthLabel: { color: '#cbd5e1', fontSize: 11, nameMap: 'ZH' },
      dayLabel: { show: false },
    },
    series: [{ type: 'heatmap', coordinateSystem: 'calendar', data }],
  }
}

export function buildGraphOption(payload, opts) {
  const data = payload || { nodes: [], links: [] }
  const palette = (opts && opts.palette) || ['#38bdf8', '#f59e0b', '#34d399', '#a78bfa', '#f472b6', '#22d3ee']
  const categories = (opts && opts.categories) || []
  return {
    tooltip: {
      formatter: (p) => p.dataType === 'edge'
        ? `${p.data.source} → ${p.data.target}<br/>合作: <b>${p.data.value || 0}</b>`
        : `${p.data.name}<br/>连接数: <b>${p.data.value || 0}</b>`,
    },
    legend: categories.length ? [{ bottom: 0, data: categories.map((item) => item.name), textStyle: { color: '#94a3b8' } }] : undefined,
    series: [{
      type: 'graph', layout: 'force', roam: true, draggable: true,
      left: 20, right: 20, top: 20, bottom: 45,
      data: data.nodes || [], links: data.links || [],
      categories: categories.map((item, index) => ({ name: item.name, itemStyle: { color: palette[index % palette.length] } })),
      label: { show: true, position: 'right', color: '#cbd5e1', fontSize: 11, formatter: '{b}' },
      labelLayout: { hideOverlap: true },
      force: { initLayout: 'circular', repulsion: 420, edgeLength: [70, 150], gravity: 0.08, friction: 0.6 },
      lineStyle: { color: 'source', opacity: 0.45, width: 1.5, curveness: 0.12 },
      emphasis: { focus: 'adjacency', scale: 1.4, lineStyle: { opacity: 0.9, width: 3 } },
    }],
  }
}

export function buildMapOption(items, opts) {
  const palette = (opts && opts.palette) || ['#38bdf8', '#f59e0b', '#34d399', '#a78bfa', '#f472b6', '#22d3ee']
  const data = (items || []).filter((item) => Array.isArray(item.value) && item.value.length >= 3)
  const max = Math.max(1, ...data.map((item) => Number(item.value[2] || 0)))
  return {
    tooltip: { formatter: (p) => `${p.name}<br/>影片数: <b>${p.value?.[2] || 0}</b>` },
    graphic: [{
      type: 'group', left: 'center', top: 'middle', bounding: 'raw', silent: true,
      children: [{
        type: 'path',
        shape: {
          pathData: 'M18 119L43 95L77 91L91 67L128 51L157 63L184 48L216 58L238 78L279 72L305 49L344 44L375 58L407 55L441 69L480 61L520 77L554 72L593 88L629 84L662 101L646 122L611 128L583 151L546 146L514 165L474 157L444 175L402 169L365 184L326 174L291 188L260 171L222 178L190 158L151 163L121 143L81 148L49 133Z M82 164L112 174L132 203L125 239L105 272L85 247L73 209Z M222 190L252 201L271 235L263 278L241 316L220 285L208 241Z M351 194L391 202L418 233L409 269L375 284L344 252L332 218Z M484 183L529 190L551 220L541 255L505 270L474 242L463 207Z M565 277L599 287L617 310L601 330L572 319Z',
          x: 0, y: 0, width: 680, height: 360,
        },
        style: { fill: 'rgba(30, 58, 90, .52)', stroke: 'rgba(56, 189, 248, .28)', lineWidth: 1.5 },
      }],
    }],
    visualMap: {
      min: 0, max, left: 12, bottom: 12, dimension: 2,
      inRange: { color: ['#38bdf8', '#a78bfa', '#f472b6'] },
      text: ['多', '少'], textStyle: { color: '#94a3b8', fontSize: 10 }, calculable: false,
    },
    grid: { left: 28, right: 28, top: 22, bottom: 30 },
    xAxis: { type: 'value', min: -180, max: 180, show: false },
    yAxis: { type: 'value', min: -60, max: 85, show: false },
    series: [{
      type: 'effectScatter', coordinateSystem: 'cartesian2d', data,
      showEffectOn: 'emphasis', rippleEffect: { scale: 2.4, brushType: 'stroke' },
      symbolSize: (value) => 8 + Math.sqrt(Number(value[2] || 0) / max) * 30,
      itemStyle: { color: (p) => palette[p.dataIndex % palette.length], shadowBlur: 14, shadowColor: '#38bdf8' },
      label: { show: true, formatter: '{b}', position: 'right', color: '#e2e8f0', fontSize: 10 },
      labelLayout: { hideOverlap: true }, emphasis: { scale: 1.25 },
    }],
  }
}