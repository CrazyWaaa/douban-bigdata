/**
 * 大屏可视化 ECharts option 工厂(集中管理)
 * 依据真实接口字段构建,主题切换时通过 readVar 刷新颜色变量。
 */

function readVar(name, fallback = '') {
  if (typeof window === 'undefined') return fallback
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return v || fallback
}

/** 主题快照:在大屏加载/主题切换时由调用方主动调用 */
export function themeSnapshot() {
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

/** Sankey 三列能量流 */
export function buildSankeyOption(payload) {
  const t = themeSnapshot()
  const rawNodes = payload?.nodes || []
  const nodes = rawNodes.map((n) => ({
    ...n,
    name: String(n.name),
  }))
  const nodeNames = new Set(nodes.map((n) => n.name))
  const links = (payload?.links || [])
    .filter((l) => l && l.value > 0)
    .map((l) => ({
      ...l,
      source: String(l.source),
      target: String(l.target),
    }))
    .filter((l) => nodeNames.has(l.source) && nodeNames.has(l.target))
  return {
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove|click',
      backgroundColor: 'rgba(15,23,42,.92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (p) => {
        if (p.dataType === 'edge') {
          return `${p.data.source} → ${p.data.target}<br/>流量: <b>${p.data.value}</b>`
        }
        return `<b>${p.name}</b><br/>净流出: ${(p.value || 0)}`
      },
    },
    series: [{
      type: 'sankey',
      data: nodes,
      links,
      nodeAlign: 'justify',
      emphasis: { focus: 'adjacency' },
      nodeWidth: 18,
      nodeGap: 12,
      layoutIterations: 64,
      label: { color: t.text, fontSize: 11 },
      lineStyle: { color: 'gradient', curveness: 0.5, opacity: 0.55 },
      itemStyle: { borderWidth: 0, color: t.primary },
    }],
  }
}

/** Treemap 类型 × 国家 矩阵 */
export function buildTreemapOption(payload) {
  const t = themeSnapshot()
  const data = Array.isArray(payload) ? payload : []
  // 按类型分组 -> 国家
  const byGenre = new Map()
  for (const it of data) {
    const g = it.genre || '其他'
    if (!byGenre.has(g)) byGenre.set(g, [])
    byGenre.get(g).push({ name: it.country, value: it.value })
  }
  const tree = []
  for (const [genre, arr] of byGenre) {
    const total = arr.reduce((s, x) => s + (x.value || 0), 0)
    if (total < 1) continue
    tree.push({ name: genre, value: total, children: arr })
  }
  const colors = [t.primary, t.success, t.warning, t.info, t.danger, '#a78bfa', '#f472b6', '#22c55e', '#fde047', '#fb923c']
  let ci = 0
  for (const n of tree) {
    n.itemStyle = { color: colors[ci % colors.length], borderColor: t.surface, borderWidth: 2 }
    for (const c of n.children || []) {
      c.itemStyle = { color: colors[ci % colors.length], borderColor: t.surface, borderWidth: 1 }
    }
    ci++
  }
  return {
    tooltip: {
      formatter: (p) => {
        const path = (p.treePathInfo || []).map((x) => x.name).filter(Boolean).join(' / ')
        return `${path}<br/>片数: <b>${p.value || 0}</b>`
      },
    },
    series: [{
      type: 'treemap',
      roam: false,
      breadcrumb: { show: false },
      nodeClick: false,
      width: '100%',
      height: '100%',
      top: 8,
      left: 8,
      right: 8,
      bottom: 8,
      tile: 'squarify',
      data: tree,
      label: {
        show: true,
        formatter: (p) => {
          const path = (p.treePathInfo || []).map((x) => x.name).filter(Boolean)
          if (path.length >= 3) return `{b|${p.data.name}}\n{c|${p.value} 部}`
          if (path.length === 2) return `{b|${p.data.name}}\n{c|${p.data.value || 0} 部}`
          return `{b|${p.data.name}}\n{c|${p.data.value || 0} 部}`
        },
        rich: {
          b: { color: '#0b1020', fontWeight: 700, fontSize: 12, lineHeight: 18 },
          c: { color: '#0b1020', fontSize: 11, lineHeight: 16 },
        },
      },
      upperLabel: {
        show: true,
        height: 22,
        color: t.text,
        fontWeight: 600,
        formatter: (p) => (p.data.children && p.data.children.length ? `${p.data.name}  ${p.data.value}` : ''),
      },
      levels: [
        { itemStyle: { gapWidth: 6, borderColor: t.surface, borderWidth: 6 } },
        { itemStyle: { gapWidth: 3, borderColor: t.surface, borderWidth: 3 } },
      ],
    }],
  }
}

/** Calendar 月度热力 */
export function buildCalendarOption(points, year) {
  const t = themeSnapshot()
  const data = (points || []).map((p) => [p.date, Number(p.value || 0)])
  const max = Math.max(1, ...data.map((d) => d[1]))
  const yr = year || (data[0] ? Number(data[0][0].slice(0, 4)) : new Date().getFullYear())
  return {
    tooltip: {
      formatter: (p) => `${String(p.value[0]).slice(0, 7)}<br/>上榜片数: <b>${p.value[1]}</b>`,
      backgroundColor: 'rgba(15,23,42,.92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
    },
    visualMap: {
      min: 0, max, calculable: false,
      orient: 'horizontal', left: 'center', bottom: 4,
      text: ['多', '少'],
      inRange: { color: ['#172554', '#0ea5e9', '#8b5cf6', '#ec4899'] },
      textStyle: { color: t.muted, fontSize: 10 },
    },
    calendar: {
      top: 38, left: 28, right: 28, bottom: 44,
      range: String(yr),
      orient: 'horizontal',
      cellSize: ['auto', 18],
      itemStyle: { borderColor: 'rgba(15,23,42,.7)', borderWidth: 2, color: 'rgba(56,189,248,.04)' },
      splitLine: { show: false },
      yearLabel: { show: false },
      monthLabel: { color: t.text, fontSize: 11, nameMap: 'ZH' },
      dayLabel: { color: t.muted, fontSize: 10, firstDay: 1 },
    },
    series: [{ type: 'heatmap', coordinateSystem: 'calendar', data }],
  }
}

/** Graph 合作网络 */
export function buildGraphOption(payload) {
  const t = themeSnapshot()
  const data = payload || { nodes: [], links: [] }
  return {
    tooltip: {
      backgroundColor: 'rgba(15,23,42,.92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (p) => p.dataType === 'edge'
        ? `${p.data.source} ↔ ${p.data.target}<br/>合作: <b>${p.data.value || 0}</b> 部`
        : `${p.data.name}<br/>作品数: <b>${p.data.value || 0}</b>`,
    },
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      left: 20, right: 20, top: 20, bottom: 20,
      data: data.nodes || [],
      links: data.links || [],
      label: { show: true, position: 'right', color: t.text, fontSize: 11, formatter: '{b}' },
      labelLayout: { hideOverlap: true },
      force: { initLayout: 'circular', repulsion: 380, edgeLength: [60, 140], gravity: 0.06, friction: 0.5 },
      lineStyle: { color: 'source', opacity: 0.55, width: 1.4, curveness: 0.12 },
      emphasis: { focus: 'adjacency', lineStyle: { opacity: 0.95, width: 3 } },
      itemStyle: { color: t.primary },
    }],
  }
}

/** Map 世界地图(用后端返回的中英名 + ECharts 内置 world 地图) */
export function buildWorldMapOption(items) {
  const t = themeSnapshot()
  const list = Array.isArray(items) ? items : []
  
  const COUNTRY_MAP = {
    // 后端英文长名 / 各种写法 -> world.json 里 properties.name
    'United States': 'United States',
    'United States of America': 'United States',
    'United Kingdom': 'United Kingdom',
    'Great Britain': 'United Kingdom',
    'UK': 'United Kingdom',
    'Japan': 'Japan',
    'China': 'China',
    'Hong Kong': 'China',
    'Taiwan': 'China',
    'Macao': 'China',
    'Macau': 'China',
    'South Korea': 'Korea',
    'Korea, Republic of': 'Korea',
    'Korea, South': 'Korea',
    'North Korea': 'Dem. Rep. Korea',
    "Korea, Democratic People's Republic of": 'Dem. Rep. Korea',
    'France': 'France',
    'Germany': 'Germany',
    'Italy': 'Italy',
    'Spain': 'Spain',
    'Canada': 'Canada',
    'Australia': 'Australia',
    'India': 'India',
    'Thailand': 'Thailand',
    'Russia': 'Russia',
    'Russian Federation': 'Russia',
    'New Zealand': 'New Zealand',
    'Brazil': 'Brazil',
    'Sweden': 'Sweden',
    'Denmark': 'Denmark',
    'Switzerland': 'Switzerland',
    'Poland': 'Poland',
    'Austria': 'Austria',
    'Argentina': 'Argentina',
    'Mexico': 'Mexico',
    'South Africa': 'South Africa',
    'Netherlands': 'Netherlands',
    'Greece': 'Greece',
    'Czech Rep.': 'Czech Rep.',
    'Czechia': 'Czech Rep.',
    'Czech Republic': 'Czech Rep.',
    'Hungary': 'Hungary',
    'Ireland': 'Ireland',
    'Belgium': 'Belgium',
    'Lebanon': 'Lebanon',
    'Iran': 'Iran',
    'Turkey': 'Turkey',
    'Türkiye': 'Turkey',
    'Israel': 'Israel',
    'Singapore': 'Singapore',
    'Malaysia': 'Malaysia',
    'Vietnam': 'Vietnam',
    'Viet Nam': 'Vietnam',
    'Indonesia': 'Indonesia',
    'Philippines': 'Philippines',
    'Ukraine': 'Ukraine',
    'Romania': 'Romania',
    'Finland': 'Finland',
    'Norway': 'Norway',
    'Portugal': 'Portugal',
    'Chile': 'Chile',
    'Cuba': 'Cuba',
    'Morocco': 'Morocco',
    'Tunisia': 'Tunisia',
    'Jordan': 'Jordan',
    'Qatar': 'Qatar',
    'United Arab Emirates': 'United Arab Emirates',
    'UAE': 'United Arab Emirates',
    'Saudi Arabia': 'Saudi Arabia',
    'Cyprus': 'Cyprus',
    'Malta': 'Malta',
    'Iceland': 'Iceland',
    'Luxembourg': 'Luxembourg',
    'Estonia': 'Estonia',
    'Latvia': 'Latvia',
    'Lithuania': 'Lithuania',
    'Slovenia': 'Slovenia',
    'Slovakia': 'Slovakia',
    'Serbia': 'Serbia',
    'Croatia': 'Croatia',
    'Bulgaria': 'Bulgaria',
    'Albania': 'Albania',
    'Bosnia and Herzegovina': 'Bosnia and Herz.',
    'Bosnia & Herzegovina': 'Bosnia and Herz.',
    'Belarus': 'Belarus',
    'Armenia': 'Armenia',
    'Azerbaijan': 'Azerbaijan',
    'Georgia': 'Georgia',
    'Kazakhstan': 'Kazakhstan',
    'Afghanistan': 'Afghanistan',
    'Bhutan': 'Bhutan',
    'Bangladesh': 'Bangladesh',
    'Nepal': 'Nepal',
    'Sri Lanka': 'Sri Lanka',
    'Myanmar': 'Myanmar',
    'Burma': 'Myanmar',
    'Cambodia': 'Cambodia',
    'Laos': 'Lao PDR',
    'Lao PDR': 'Lao PDR',
    'Mongolia': 'Mongolia',
    'Pakistan': 'Pakistan',
    'Panama': 'Panama',
    'Costa Rica': 'Costa Rica',
    'Honduras': 'Honduras',
    'El Salvador': 'El Salvador',
    'Guatemala': 'Guatemala',
    'Haiti': 'Haiti',
    'Dominican Rep.': 'Dominican Rep.',
    'Dominican Republic': 'Dominican Rep.',
    'Jamaica': 'Jamaica',
    'Trinidad and Tobago': 'Trinidad and Tobago',
  }

  const merged = {}
  for (const x of list) {
    const mappedName = COUNTRY_MAP[x.name_en] || x.name_en
    if (!merged[mappedName]) {
      merged[mappedName] = { name: mappedName, name_zh: x.name_zh, count: 0, avg_rating: 0, rating_sum: 0, rating_n: 0 }
    }
    merged[mappedName].count += Number(x.count || 0)
    if (x.avg_rating) {
      merged[mappedName].rating_sum += Number(x.avg_rating) * Number(x.count || 0)
      merged[mappedName].rating_n += Number(x.count || 0)
    }
  }

  const finalData = Object.values(merged).map((x) => ({
    name: x.name,
    name_zh: x.name_zh,
    count: x.count,
    avg_rating: x.rating_n > 0 ? Number((x.rating_sum / x.rating_n).toFixed(2)) : 0,
    value: x.count,
  }))

  const max = Math.max(1, ...finalData.map((x) => x.count))
  return {
    tooltip: {
      backgroundColor: 'rgba(15,23,42,.92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (p) => {
        const d = p.data || {}
        const zh = d.name_zh || p.name
        const count = d.count != null ? d.count : p.value
        const avg = d.avg_rating
        return `${zh}<br/>片数: <b>${count}</b>${avg ? `<br/>平均: ${avg}` : ''}`
      },
    },
    visualMap: {
      min: 0, max, left: 16, bottom: 16,
      calculable: true,
      text: ['多', '少'],
      inRange: { color: ['#0c4a6e', '#0ea5e9', '#a78bfa', '#f472b6'] },
      textStyle: { color: t.muted, fontSize: 10 },
    },
    geo: {
      map: 'world',
      roam: true,
      zoom: 1.2,
      itemStyle: {
        areaColor: 'rgba(56,189,248,.06)',
        borderColor: 'rgba(56,189,248,.45)',
        borderWidth: 0.6,
      },
      emphasis: {
        itemStyle: { areaColor: '#38bdf8' },
        label: { show: true, color: '#0b1020' },
      },
      label: { show: false },
    },
    series: [{
      type: 'map',
      geoIndex: 0,
      data: finalData,
    }],
  }
}

/**
 * Gauge option factory.
 * payload: [{ name, value, max?, color? }]
 */
export function buildGaugeOption(payload, opts = {}) {
  const t = themeSnapshot()
  const list = Array.isArray(payload) ? payload.filter((d) => d && d.name) : []
  if (!list.length) {
    return {
      tooltip: {},
      series: [],
      graphic: [{ type: 'text', left: 'center', top: 'middle', style: { text: '暂无指标数据', fill: t.muted, fontSize: 12 } }],
    }
  }
  const rows = opts.rows || 2
  const cols = opts.cols || Math.ceil(list.length / rows)
  const palette = [t.primary, t.warning, t.success, t.info, t.danger, '#a78bfa', '#f472b6', '#22d3ee']
  const series = list.map((it, i) => {
    const r = Math.floor(i / cols)
    const c = i % cols
    const w = 100 / cols
    const h = 100 / rows
    return {
      type: 'gauge',
      name: it.name,
      center: [`${w * c + w / 2}%`, `${h * r + h / 2}%`],
      radius: `${Math.min(w, h) * 0.42}%`,
      min: 0,
      max: it.max ?? 100,
      startAngle: 200,
      endAngle: -20,
      progress: { show: true, width: 8, itemStyle: { color: it.color || palette[i % palette.length] } },
      axisLine: { lineStyle: { width: 8, color: [[1, 'rgba(148,163,184,.18)']] } },
      pointer: { show: false },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      anchor: { show: false },
      title: { show: true, offsetCenter: [0, '70%'], color: t.muted, fontSize: 11 },
      detail: {
        valueAnimation: true,
        offsetCenter: [0, '0%'],
        formatter: (v) => Number(v).toFixed(1),
        color: t.text,
        fontSize: 18,
        fontWeight: 700,
      },
      data: [{ value: Number(it.value || 0), name: it.name }],
    }
  })
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, .92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (p) => `${p.name}<br/><b>${p.value}</b> / ${p.series.max || '-'}`,
    },
    series,
  }
}

/**
 * Funnel option factory.
 * payload: [{ name, value }]
 */
export function buildFunnelOption(payload, opts = {}) {
  const t = themeSnapshot()
  const items = (Array.isArray(payload) ? payload : [])
    .filter((d) => d && d.name && Number.isFinite(d.value) && d.value > 0)
  if (!items.length) {
    return {
      tooltip: {},
      series: [],
      graphic: [{ type: 'text', left: 'center', top: 'middle', style: { text: '暂无漏斗数据', fill: t.muted, fontSize: 12 } }],
    }
  }
  const palette = [t.primary, t.info, t.success, t.warning, t.danger]
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, .92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: '{b}: <b>{c}</b>',
    },
    legend: { show: true, bottom: 0, textStyle: { color: t.muted, fontSize: 11 } },
    series: [{
      type: 'funnel',
      left: '8%',
      right: '8%',
      top: 16,
      bottom: 36,
      width: '84%',
      min: 0,
      max: Math.max(...items.map((d) => d.value)),
      minSize: '0%',
      maxSize: '100%',
      sort: 'descending',
      gap: 2,
      funnelAlign: 'center',
      label: { show: true, position: 'inside', color: '#0b1020', fontWeight: 600, fontSize: 12, formatter: '{b}\n{c}' },
      labelLine: { show: false },
      itemStyle: { borderColor: t.surface, borderWidth: 1 },
      emphasis: { label: { fontSize: 14 } },
      data: items.map((d, i) => ({ ...d, itemStyle: { color: palette[i % palette.length] } })),
    }],
  }
}

/**
 * Radar option factory.
 * payload: [{ name, values: number[] }]
 * opts.indicators: [{ name, max? }]
 */
export function buildRadarOption(payload, opts = {}) {
  const t = themeSnapshot()
  const items = (Array.isArray(payload) ? payload : []).filter((d) => d && d.name && Array.isArray(d.values) && d.values.length)
  if (!items.length) {
    return {
      tooltip: {},
      series: [],
      graphic: [{ type: 'text', left: 'center', top: 'middle', style: { text: '暂无能力数据', fill: t.muted, fontSize: 12 } }],
    }
  }
  const dim = items[0].values.length
  const indicators = (opts.indicators && opts.indicators.length === dim)
    ? opts.indicators.map((it) => ({ name: it.name, max: it.max ?? 10 }))
    : Array.from({ length: dim }, (_, i) => ({
        name: (opts.indicators && opts.indicators[i] && opts.indicators[i].name) || (`维度${i + 1}`),
        max: (opts.indicators && opts.indicators[i] && opts.indicators[i].max) || 10,
      }))
  const maxVal = Math.max(10, ...items.flatMap((d) => d.values))
  for (const ind of indicators) if (ind.max < maxVal) ind.max = maxVal
  const palette = [t.primary, t.warning, t.success, t.danger, t.info, '#a78bfa', '#f472b6', '#22d3ee']
  return {
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, .92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      trigger: 'item',
    },
    legend: {
      data: items.map((d) => d.name),
      bottom: 0,
      textStyle: { color: t.muted, fontSize: 11 },
      icon: 'roundRect',
      itemWidth: 10,
      itemHeight: 10,
    },
    radar: {
      indicator: indicators,
      center: ['50%', '48%'],
      radius: '62%',
      splitNumber: 4,
      axisName: { color: t.muted, fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,.2)' } },
      splitArea: { areaStyle: { color: ['rgba(56,189,248,.04)', 'rgba(56,189,248,.08)'] } },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,.25)' } },
    },
    series: [{
      type: 'radar',
      data: items.map((d, i) => ({
        name: d.name,
        value: d.values,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: { color: palette[i % palette.length], width: 2 },
        itemStyle: { color: palette[i % palette.length] },
        areaStyle: { color: palette[i % palette.length], opacity: 0.18 },
      })),
    }],
  }
}

/**
 * WordCloud option factory.
 * payload: [{ name, value }]
 */
export function buildWordCloudOption(payload, opts = {}) {
  const t = themeSnapshot()
  const list = (Array.isArray(payload) ? payload : [])
    .filter((d) => d && d.name && Number.isFinite(d.value) && d.value > 0)
  if (!list.length) {
    return {
      tooltip: {},
      series: [],
      graphic: [{ type: 'text', left: 'center', top: 'middle', style: { text: '暂无词云数据', fill: t.muted, fontSize: 12 } }],
    }
  }
  const palette = [t.primary, t.warning, t.success, t.danger, t.info, '#a78bfa', '#f472b6', '#22d3ee']
  return {
    tooltip: {
      show: true,
      backgroundColor: 'rgba(15, 23, 42, .92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (p) => `${p.name}<br/>${p.value}`,
    },
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      left: 'center',
      top: 'center',
      width: '92%',
      height: '92%',
      sizeRange: [14, 56],
      rotationRange: [-30, 30],
      rotationStep: 15,
      gridSize: 6,
      drawOutOfBound: false,
      textStyle: {
        fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif',
        fontWeight: 700,
        color: (i) => palette[i % palette.length],
      },
      emphasis: {
        textStyle: { color: '#fff', textShadowColor: t.primary, textShadowBlur: 12 },
      },
      data: list,
    }],
  }
}
