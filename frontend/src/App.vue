<template>
  <div class="app-shell">
    <!-- 顶部精简栏：品牌 + 搜索 + 主题 -->
    <header class="app-top">
      <div class="app-top__inner">
        <div class="app-top__brand">
          <span class="app-top__name">豆瓣电影大数据分析平台</span>
          <span class="app-top__sub">DOUBAN · BIGDATA</span>
        </div>
        <div class="app-top__actions">
          <button class="app-top__search" @click="openPalette" aria-label="打开搜索面板">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="7"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
            <span>搜索电影 / 跳转</span>
            <kbd>{{ isMac ? '⌘' : 'Ctrl' }} K</kbd>
          </button>
          <button class="app-top__iconbtn" @click="toggle" :aria-label="`切换到${theme === 'dark' ? '浅色' : '深色'}主题`">
            <svg v-if="theme === 'dark'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <div class="app-body">
      <!-- 左侧导航栏 -->
      <aside class="app-sidebar">
        <div class="app-sidebar__inner">
          <nav class="app-nav">
            <div class="app-nav__group-title">核心</div>
            <router-link to="/" class="app-nav__item" active-class="is-active" exact-active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">大屏</span>
              <span class="app-nav__desc">数据总览</span>
            </router-link>
            <router-link to="/top" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">高分榜</span>
              <span class="app-nav__desc">TOP 250</span>
            </router-link>
            <router-link to="/search" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">搜索</span>
              <span class="app-nav__desc">关键词</span>
            </router-link>

            <div class="app-nav__group-title">维度</div>
            <router-link to="/genre" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">类型</span>
              <span class="app-nav__desc">按题材</span>
            </router-link>
            <router-link to="/country" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">地区</span>
              <span class="app-nav__desc">按国别</span>
            </router-link>
            <router-link to="/year" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">年代</span>
              <span class="app-nav__desc">按年份</span>
            </router-link>

            <div class="app-nav__group-title">高级可视化</div>
            <router-link to="/radar" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">雷达</span>
              <span class="app-nav__desc">影片能力</span>
            </router-link>
            <router-link to="/sankey" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">桑基</span>
              <span class="app-nav__desc">流量链路</span>
            </router-link>
            <router-link to="/treemap" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">矩阵树</span>
              <span class="app-nav__desc">类型×地区</span>
            </router-link>
            <router-link to="/wordcloud" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">词云</span>
              <span class="app-nav__desc">词频可视化</span>
            </router-link>
            <router-link to="/gauge" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">仪表盘</span>
              <span class="app-nav__desc">核心指针</span>
            </router-link>
            <router-link to="/funnel" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">漏斗</span>
              <span class="app-nav__desc">评分分层</span>
            </router-link>
            <router-link to="/calendar" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">日历热力</span>
              <span class="app-nav__desc">年度分布</span>
            </router-link>
            <router-link to="/network" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">关系网络</span>
              <span class="app-nav__desc">合作图</span>
            </router-link>
            <router-link to="/map" class="app-nav__item" active-class="is-active">
              <span class="app-nav__dot" aria-hidden="true"></span>
              <span class="app-nav__label">世界地图</span>
              <span class="app-nav__desc">国家分布</span>
            </router-link>
          </nav>
          <div class="app-sidebar__foot">
            <span class="app-sidebar__tip">快捷：<kbd>⌘/Ctrl</kbd> + <kbd>K</kbd> 搜索</span>
          </div>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="app-main">
        <router-view v-slot="{ Component, route }">
          <transition name="page" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </main>
    </div>

    <CommandPalette />
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useTheme } from './composables/useTheme';
import { useCommandPalette } from './composables/useCommandPalette';
import { useNProgress } from './composables/useNProgress';
import CommandPalette from './components/CommandPalette.vue';
import httpClient from './api/httpClient';

const router = useRouter();
const { theme, toggle } = useTheme();
const { open: openPalette } = useCommandPalette();
const { start, done, inc } = useNProgress();

const isMac = computed(() => {
  if (typeof navigator === 'undefined') return false;
  return /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent || '');
});

// 在 axios 客户端上挂一个轻量计数器：多个并发请求叠加 inc，
// 直到全部完成才 done()，这样 Dashboard / Detail 的多次并发请求
// 不会让进度条反复闪。
let inflight = 0;
let reqId = null;
let respId = null;
let removeBeforeEach = null;
let removeAfterEach = null;
onMounted(() => {
  reqId = httpClient.interceptors.request.use((cfg) => {
    if (inflight === 0) start();
    inflight++;
    cfg.__npInflight = true;
    return cfg;
  });
  // 单一响应拦截器同时处理成功与失败，避免双调用
  respId = httpClient.interceptors.response.use(
    (r) => { finishOne(); return r; },
    (err) => { finishOne(); return Promise.reject(err); }
  );
  removeBeforeEach = router.beforeEach((to, from) => {
    if (to.fullPath !== from.fullPath) start();
  });
  removeAfterEach = router.afterEach(() => {
    if (inflight === 0) done();
  });
});

function finishOne() {
  if (inflight > 0) inflight--;
  inc(0.3);
  if (inflight === 0) done();
}

onBeforeUnmount(() => {
  if (removeAfterEach) removeAfterEach();
  if (removeBeforeEach) removeBeforeEach();
  if (reqId !== null) httpClient.interceptors.request.eject(reqId);
  if (respId !== null) httpClient.interceptors.response.eject(respId);
});
</script>

<style>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(900px 600px at 0% 0%, var(--c-primary-tint), transparent 60%),
    radial-gradient(700px 500px at 100% 0%, color-mix(in srgb, var(--c-info) 12%, transparent), transparent 60%),
    var(--c-bg);
  background-attachment: fixed;
}

.app-top {
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--c-border);
  backdrop-filter: saturate(180%) blur(14px);
  background: color-mix(in srgb, var(--c-bg) 72%, transparent);
}

.app-top__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 24px;
}

.app-top__brand {
  display: inline-flex;
  align-items: baseline;
  gap: 10px;
}

.app-top__name {
  font-size: 14px;
  font-weight: 700;
  color: var(--c-text);
  letter-spacing: 0.5px;
}

.app-top__sub {
  font-size: 10px;
  color: var(--c-muted);
  letter-spacing: 2px;
}

.app-top__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.app-top__search {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--c-surface-2);
  border: 1px solid var(--c-border);
  color: var(--c-muted);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: var(--fs-sm);
  cursor: pointer;
  transition: background var(--t-fast) var(--ease-out), color var(--t-fast) var(--ease-out), border-color var(--t-fast) var(--ease-out);
}

.app-top__search:hover {
  color: var(--c-text);
  border-color: var(--c-primary);
}

.app-top__search kbd {
  font-family: inherit;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  background: var(--c-surface);
  color: var(--c-muted);
  border: 1px solid var(--c-border);
  margin-left: 4px;
}

.app-top__iconbtn {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--c-border);
  border-radius: 8px;
  color: var(--c-text-soft);
  cursor: pointer;
  transition: background var(--t-fast) var(--ease-out), color var(--t-fast) var(--ease-out), border-color var(--t-fast) var(--ease-out);
}

.app-top__iconbtn:hover {
  color: var(--c-primary);
  border-color: var(--c-primary);
  background: var(--c-primary-tint);
}

.app-body {
  flex: 1;
  display: flex;
  gap: 0;
}

.app-sidebar {
  width: 220px;
  flex-shrink: 0;
  position: sticky;
  top: calc(var(--fs-md) * 2 + 20px);
  height: calc(100vh - calc(var(--fs-md) * 2 + 20px));
  border-right: 1px solid var(--c-border);
  background: color-mix(in srgb, var(--c-bg) 90%, transparent);
  backdrop-filter: saturate(180%) blur(8px);
}

.app-sidebar__inner {
  padding: 8px 0;
  height: 100%;
  overflow-y: auto;
}

.app-nav {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}

.app-nav__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  color: var(--c-text-soft);
  text-decoration: none;
  transition: background var(--t-fast) var(--ease-out), color var(--t-fast) var(--ease-out);
  border-radius: 0 var(--r) var(--r) 0;
  margin-left: 4px;
}

.app-nav__item:hover {
  background: var(--c-surface-2);
  color: var(--c-text);
}

.app-nav__item.is-active {
  background: var(--c-primary-tint);
  color: var(--c-primary);
}

.app-nav__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--c-muted);
  flex-shrink: 0;
}

.app-nav__item.is-active .app-nav__dot {
  background: var(--c-primary);
}

.app-nav__label {
  font-size: var(--fs-sm);
  font-weight: 500;
}

.app-nav__desc {
  font-size: var(--fs-xs);
  color: var(--c-muted);
  margin-left: auto;
}

.app-nav__group-title {
  font-size: 10px;
  color: var(--c-muted);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  padding: 14px 12px 4px;
  font-weight: 600;
}

.app-nav__group-title:first-child {
  padding-top: 4px;
}

.app-sidebar__foot {
  padding: 12px;
  border-top: 1px solid var(--c-border);
  margin-top: 8px;
}

.app-sidebar__tip {
  font-size: 10px;
  color: var(--c-muted);
}

.app-sidebar__tip kbd {
  font-family: inherit;
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 3px;
  background: var(--c-surface);
  color: var(--c-muted);
  border: 1px solid var(--c-border);
  margin: 0 2px;
}

.app-main {
  flex: 1;
  padding: 16px 24px 32px;
  overflow-y: auto;
}

.page-enter-active,
.page-leave-active {
  transition: opacity var(--t) var(--ease-out), transform var(--t) var(--ease-out);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (max-width: 1000px) {
  .app-sidebar {
    width: 100%;
    height: auto;
    position: relative;
    top: auto;
    border-right: none;
    border-bottom: 1px solid var(--c-border);
  }

  .app-body {
    flex-direction: column;
  }

  .app-sidebar__inner {
    padding: 8px 12px;
    overflow-y: visible;
  }

  .app-nav {
    flex-direction: row;
    overflow-x: auto;
    gap: 4px;
  }

  .app-nav__group-title {
    display: none;
  }

  .app-nav__item {
    white-space: nowrap;
    padding: 8px 12px;
    margin-left: 0;
    border-radius: var(--r-sm);
  }

  .app-nav__desc,
  .app-nav__dot {
    display: none;
  }

  .app-sidebar__foot {
    display: none;
  }

  .app-main {
    padding: 12px 14px 32px;
  }
}

@media (max-width: 640px) {
  .app-top__search span {
    display: none;
  }

  .app-top__inner {
    padding: 10px 14px;
  }
}
</style>
