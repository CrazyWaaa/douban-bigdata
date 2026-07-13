import { computed } from "vue";

/**
 * 钻取数据 composable：
 * 输入当前已加载的 topRated 全量电影 + 一个维度（genre / country / director / decade / ratingBucket），
 * 输出该维度子集的多维分布（评分段、年份段、国家数）。
 *
 * 纯前端聚合，零后端开销；数据源为 store 里的 topRated(20) + avgBy* 列表。
 * 数据量超过 ~500 后建议改为后端 drill-down 接口。
 */

const RATING_BUCKETS = [
  { key: "lt7", label: "7 分以下", min: 0,  max: 7  },
  { key: "7-8", label: "7-8 分",   min: 7,  max: 8  },
  { key: "8-9", label: "8-9 分",   min: 8,  max: 9  },
  { key: "9+",  label: "9 分以上", min: 9,  max: 11 },
];
const DECADE_BUCKETS = [
  { key: "<70",  label: "70 前",   min: 0,    max: 1970 },
  { key: "70s",  label: "70s",     min: 1970, max: 1980 },
  { key: "80s",  label: "80s",     min: 1980, max: 1990 },
  { key: "90s",  label: "90s",     min: 1990, max: 2000 },
  { key: "00s",  label: "00s",     min: 2000, max: 2010 },
  { key: "10s+", label: "10s+",    min: 2010, max: 9999 },
];

function bucketRating(r) {
  if (r == null) return null;
  for (const b of RATING_BUCKETS) if (r >= b.min && r < b.max) return b;
  return null;
}
function bucketDecade(y) {
  if (y == null) return null;
  for (const b of DECADE_BUCKETS) if (y >= b.min && y < b.max) return b;
  return null;
}
function splitTerms(s, sep = "/") {
  if (!s) return [];
  return String(s).split(sep).map(t => t.trim()).filter(Boolean);
}

export function useDrilldown(moviesRef, dimRef, valueRef) {
  // 命中电影子集
  const matched = computed(() => {
    const movies = moviesRef.value || [];
    const dim = dimRef.value;
    const val = valueRef.value;
    if (!dim || val == null || val === "") return [];
    return movies.filter((m) => {
      if (dim === "genre")    return splitTerms(m.genre).includes(val);
      if (dim === "country")  return splitTerms(m.country).includes(val);
      if (dim === "director") return splitTerms(m.director).includes(val);
      if (dim === "year")     return m.year === val;
      if (dim === "decade")   return m.year != null && Math.floor(m.year / 10) * 10 === val;
      if (dim === "ratingBucket") {
        const b = bucketRating(m.rating);
        return b && b.label === val;
      }
      return false;
    });
  });

  // 评分段分布
  const ratingDist = computed(() => {
    const items = matched.value;
    return RATING_BUCKETS.map((b) => ({
      name: b.label,
      value: items.filter((m) => bucketRating(m.rating)?.key === b.key).length,
    })).filter((d) => d.value > 0);
  });

  // 年代段分布
  const decadeDist = computed(() => {
    const items = matched.value;
    return DECADE_BUCKETS.map((b) => ({
      name: b.label,
      value: items.filter((m) => bucketDecade(m.year)?.key === b.key).length,
    })).filter((d) => d.value > 0);
  });

  // 国家分布（top 6 + 其他）
  const countryDist = computed(() => {
    const map = new Map();
    for (const m of matched.value) {
      for (const c of splitTerms(m.country)) {
        map.set(c, (map.get(c) || 0) + 1);
      }
    }
    const arr = [...map.entries()].map(([name, value]) => ({ name, value }));
    arr.sort((a, b) => b.value - a.value);
    if (arr.length <= 6) return arr;
    const head = arr.slice(0, 6);
    const rest = arr.slice(6).reduce((s, x) => s + x.value, 0);
    return [...head, { name: "其他", value: rest }];
  });

  return { matched, ratingDist, decadeDist, countryDist };
}