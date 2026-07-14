# -*- coding: utf-8 -*-
"""修复 buildWorldMapOption:国家名映射 + value 字段 + visualMap"""
p = r"D:\Ayueqian\project\code\douban-bigdata\frontend\src\echarts\options.js"
data = open(p, "rb").read().decode("utf-8")

# 原 COUNTRY_MAP 在 7297 起,j 替换为新的"世界名/长名 -> 内部短名"映射
START = data.find("const COUNTRY_MAP = {")
# 找对应的闭合 '}'
SEARCH_FROM = START
depth = 0
i = SEARCH_FROM
while i < len(data):
    ch = data[i]
    if ch == "{":
        depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0:
            END = i + 1
            break
    i += 1

OLD_MAP = data[START:END]
NEW_MAP = """const COUNTRY_MAP = {
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
  }"""

assert OLD_MAP.startswith("const COUNTRY_MAP = {"), "old map block not found"
data = data[:START] + NEW_MAP + data[END:]
print("[OK] replaced COUNTRY_MAP, +" + str(len(NEW_MAP) - len(OLD_MAP)) + " chars")

# 修 value 字段:[0,0,count] -> 直接 count(地图 series 不需要热力点格式)
OLD_VALUE = """    name: x.name,
    name_zh: x.name_zh,
    count: x.count,
    avg_rating: x.rating_n > 0 ? Number((x.rating_sum / x.rating_n).toFixed(2)) : 0,
    value: [0, 0, x.count],
  }))"""
NEW_VALUE = """    name: x.name,
    name_zh: x.name_zh,
    count: x.count,
    avg_rating: x.rating_n > 0 ? Number((x.rating_sum / x.rating_n).toFixed(2)) : 0,
    value: x.count,
  }))"""
assert OLD_VALUE in data, "value block not found"
data = data.replace(OLD_VALUE, NEW_VALUE)
print("[OK] fixed value field for map series")

# 修 visualMap + tooltip:visualMap 改用 log 刻度 / tooltip 适配新 value
OLD_VM = """  const max = Math.max(1, ...finalData.map((x) => x.count))
  return {
    tooltip: {
      backgroundColor: 'rgba(15,23,42,.92)',
      borderColor: 'rgba(56,189,248,.4)',
      textStyle: { color: t.text },
      formatter: (p) => {
        const zh = p.data?.name_zh || p.name
        const count = p.data?.count || (p.value && p.value[2]) || 0
        const avg = p.data?.avg_rating
        return `${zh}<br/>\u7247\u6570: <b>${count}</b>${avg ? `<br/>\u5e73\u5747: ${avg}` : ''}`
      },
    },
    visualMap: {
      min: 0, max, left: 16, bottom: 16,
      text: ['\u591a', '\u5c11'],
      inRange: { color: ['#0c4a6e', '#0ea5e9', '#a78bfa', '#f472b6'] },
      textStyle: { color: t.muted, fontSize: 10 },
    },"""
NEW_VM = """  const max = Math.max(1, ...finalData.map((x) => x.count))
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
        return `${zh}<br/>\u7247\u6570: <b>${count}</b>${avg ? `<br/>\u5e73\u5747: ${avg}` : ''}`
      },
    },
    visualMap: {
      min: 0, max, left: 16, bottom: 16,
      calculable: true,
      text: ['\u591a', '\u5c11'],
      inRange: { color: ['#0c4a6e', '#0ea5e9', '#a78bfa', '#f472b6'] },
      textStyle: { color: t.muted, fontSize: 10 },
    },"""
assert OLD_VM in data, "visualMap block not found"
data = data.replace(OLD_VM, NEW_VM)
print("[OK] fixed visualMap + tooltip")

open(p, "wb").write(data.encode("utf-8"))
print("\n=== buildWorldMapOption patched ===")
