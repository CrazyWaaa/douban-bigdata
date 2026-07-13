<template>
  <Teleport to="body">
    <transition name="cmdk">
      <div v-if="isOpen" class="cmdk-mask" @click.self="close">
        <div class="cmdk" @click.stop>
          <div class="cmdk__head">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            <input
              ref="inputEl"
              v-model="kw"
              type="text"
              placeholder="搜索电影 / 跳转页面 / 命令…"
              @keydown.down.prevent="move(1)"
              @keydown.up.prevent="move(-1)"
              @keydown.enter.prevent="commit"
              @keydown.esc="close"
            />
            <kbd>ESC</kbd>
          </div>
          <div class="cmdk__body">
            <div v-if="!kw" class="cmdk__section-title">快捷跳转</div>
            <ul v-if="!kw" class="cmdk__list">
              <li
                v-for="(it, i) in quickLinks"
                :key="it.path"
                :class="{ 'is-active': i === active }"
                @mouseenter="active = i"
                @click="goPath(it.path)"
              >
                <span class="cmdk__rank">{{ i + 1 }}</span>
                <span class="cmdk__title">{{ it.label }}</span>
                <span class="cmdk__meta">{{ it.hint }}</span>
              </li>
            </ul>

            <div v-if="kw" class="cmdk__section-title">
              搜索结果<span v-if="loading"> · 加载中</span>
            </div>
            <ul v-if="kw && results.length" class="cmdk__list">
              <li
                v-for="(m, i) in results.slice(0, 8)"
                :key="m.douban_id"
                :class="{ 'is-active': i === active }"
                @mouseenter="active = i"
                @click="goMovie(m.douban_id)"
              >
                <span class="cmdk__rank">★</span>
                <span class="cmdk__title" v-html="highlight(m.title)"></span>
                <span class="cmdk__meta">{{ m.year }} · {{ (m.director || '').split('/')[0] }}</span>
                <span class="cmdk__rating">{{ m.rating?.toFixed?.(1) ?? '-' }}</span>
              </li>
            </ul>
            <div v-else-if="kw && !loading" class="cmdk__hint">无匹配影片,按 <kbd>↵</kbd> 进入搜索页</div>
          </div>
          <div class="cmdk__foot">
            <span><kbd>↑</kbd><kbd>↓</kbd> 移动</span>
            <span><kbd>↵</kbd> 打开</span>
            <span><kbd>ESC</kbd> 关闭</span>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useCommandPalette } from "../composables/useCommandPalette";
import { api } from "../api";

const router = useRouter();
const { isOpen, close } = useCommandPalette();
const inputEl = ref(null);
const kw = ref("");
const results = ref([]);
const loading = ref(false);
const active = ref(0);

const quickLinks = [
  { label: "数据大屏",     hint: "Dashboard",       path: "/" },
  { label: "高分榜单",     hint: "Top 列表",        path: "/top" },
  { label: "类型分布",     hint: "Genre",           path: "/genre" },
  { label: "地区分布",     hint: "Country",         path: "/country" },
  { label: "年代趋势",     hint: "Year",            path: "/year" },
  { label: "搜索影片",     hint: "Search",          path: "/search" },
  { label: "影片雷达",     hint: "Radar",           path: "/radar" },
  { label: "流量桑基",     hint: "Sankey",          path: "/sankey" },
  { label: "类型×地区 矩阵", hint: "Treemap",        path: "/treemap" },
  { label: "词云",         hint: "WordCloud",       path: "/wordcloud" },
  { label: "品质仪表盘",   hint: "Gauge",           path: "/gauge" },
  { label: "评分漏斗",     hint: "Funnel",          path: "/funnel" },
  { label: "日历热力",     hint: "Calendar",        path: "/calendar" },
  { label: "合作网络",     hint: "Network",         path: "/network" },
  { label: "世界地图",     hint: "Map",             path: "/map" },
];

let debounceTimer = 0;
function onKwChange(v) {
  clearTimeout(debounceTimer);
  if (!v) { results.value = []; active.value = 0; return; }
  debounceTimer = setTimeout(async () => {
    loading.value = true;
    try {
      const data = await api.search(v, 8);
      results.value = data?.data || [];
      active.value = 0;
    } catch (e) {
      results.value = [];
    } finally {
      loading.value = false;
    }
  }, 200);
}

watch(kw, onKwChange);

watch(isOpen, async (open) => {
  if (open) {
    kw.value = "";
    results.value = [];
    active.value = 0;
    await nextTick();
    inputEl.value?.focus();
  }
});

function move(d) {
  const len = kw.value ? Math.min(results.value.length, 8) : quickLinks.length;
  if (!len) return;
  active.value = (active.value + d + len) % len;
}

function commit() {
  if (kw.value) {
    if (results.value[active.value]) goMovie(results.value[active.value].douban_id);
    else goPath("/search", { q: kw.value });
  } else {
    if (quickLinks[active.value]) goPath(quickLinks[active.value].path);
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"'']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "''": "&#39;" }[c]));
}
function highlight(text) {
  if (!text || !kw.value) return escapeHtml(text);
  const safe = escapeHtml(text);
  const q = escapeHtml(kw.value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return safe.replace(new RegExp(q, "gi"), m => `<mark>${m}</mark>`);
}

function goMovie(id) { close(); router.push(`/movie/${id}`); }
function goPath(p, q) { close(); router.push({ path: p, query: q || undefined }); }
</script>

<style scoped>
.cmdk-mask {
  position: fixed; inset: 0; z-index: 200;
  background: color-mix(in srgb, #000 50%, transparent);
  backdrop-filter: blur(6px);
  display: flex; align-items: flex-start; justify-content: center;
  padding-top: 12vh;
  animation: fadeIn .15s var(--ease-out);
}
.cmdk {
  width: min(640px, 92vw);
  background: var(--c-surface);
  border: 1px solid var(--c-border-strong);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  animation: fadeUp .22s var(--ease-out) both;
}
.cmdk__head {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--c-border);
  color: var(--c-muted);
}
.cmdk__head input {
  flex: 1; background: transparent; border: 0; outline: 0;
  color: var(--c-text); font-size: 15px; padding: 4px 0;
}
.cmdk__head kbd {
  font-family: inherit; font-size: 10px;
  padding: 2px 6px; border-radius: 4px;
  background: var(--c-surface-2); color: var(--c-muted);
  border: 1px solid var(--c-border);
}
.cmdk__body { max-height: 50vh; overflow-y: auto; padding: 6px; }
.cmdk__hint { padding: 24px 12px; text-align: center; color: var(--c-muted); font-size: var(--fs-sm); }
.cmdk__hint kbd {
  font-family: inherit; font-size: 10px;
  padding: 1px 5px; border-radius: 3px;
  background: var(--c-surface-2); color: var(--c-muted);
  border: 1px solid var(--c-border);
  margin: 0 2px;
}
.cmdk__section-title {
  padding: 8px 12px 4px;
  font-size: 10px; color: var(--c-muted);
  letter-spacing: 1.5px; text-transform: uppercase;
}
.cmdk__list { list-style: none; padding: 0; margin: 0; }
.cmdk__list li {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 12px; border-radius: 6px;
  cursor: pointer;
  transition: background var(--t-fast) var(--ease-out);
}
.cmdk__list li.is-active { background: var(--c-primary-tint); }
.cmdk__rank {
  width: 28px; text-align: center; font-size: 14px; color: var(--c-muted);
  flex-shrink: 0;
}
.cmdk__list li.is-active .cmdk__rank { color: var(--c-primary); }
.cmdk__title { flex: 1; min-width: 0; font-size: var(--fs-md); color: var(--c-text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cmdk__title :deep(mark) { background: color-mix(in srgb, var(--c-warning) 35%, transparent); color: var(--c-text); border-radius: 3px; padding: 0 2px; }
.cmdk__meta { font-size: var(--fs-sm); color: var(--c-muted); max-width: 40%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cmdk__rating { font-weight: 700; color: var(--c-primary); font-size: var(--fs-md); min-width: 30px; text-align: right; }
.cmdk__foot {
  display: flex; gap: 16px; justify-content: flex-end;
  padding: 8px 14px;
  border-top: 1px solid var(--c-border);
  background: var(--c-surface-2);
  color: var(--c-muted); font-size: 10px;
}
.cmdk__foot kbd {
  font-family: inherit; font-size: 10px;
  padding: 1px 5px; border-radius: 3px;
  background: var(--c-surface); color: var(--c-muted);
  border: 1px solid var(--c-border);
  margin-right: 3px;
}
.cmdk-enter-active, .cmdk-leave-active { transition: opacity .15s var(--ease-out); }
.cmdk-enter-from, .cmdk-leave-to { opacity: 0; }
</style>
