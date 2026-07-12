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
