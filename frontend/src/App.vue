<template>
  <div class="app-shell">
    <header class="app-nav">
      <div class="app-nav__inner">
        <router-link to="/" class="app-brand">
          <span class="app-brand__text">
            <span class="app-brand__name">豆瓣 · 数据透视</span>
            <span class="app-brand__sub">DOUBAN BIGDATA</span>
          </span>
        </router-link>
        <nav class="app-links">
          <router-link to="/" class="app-link" active-class="is-active" exact-active-class="is-active">大屏</router-link>
          <router-link to="/top" class="app-link" active-class="is-active">高分榜</router-link>
          <router-link to="/genre" class="app-link" active-class="is-active">类型</router-link>
          <router-link to="/country" class="app-link" active-class="is-active">地区</router-link>
          <router-link to="/year" class="app-link" active-class="is-active">年代</router-link>
          <router-link to="/search" class="app-link" active-class="is-active">搜索</router-link>
        </nav>
        <div class="app-actions">
          <button class="app-search" @click="openPalette" aria-label="打开搜索面板">
            <span>搜索电影 · 跳转</span>
            <kbd>{{ isMac ? '⌘' : 'Ctrl' }} K</kbd>
          </button>
          <button class="app-iconbtn" @click="toggle" :aria-label="`切换到${theme === 'dark' ? '浅色' : '深色'}主题`">
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

    <main class="app-main">
      <router-view v-slot="{ Component, route }">
        <transition name="page" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </transition>
      </router-view>
    </main>

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

const router = useRouter();
const { theme, toggle } = useTheme();
const { open: openPalette } = useCommandPalette();
const { start, done } = useNProgress();

const isMac = computed(() => {
  if (typeof navigator === 'undefined') return false;
  return /Mac|iPhone|iPad/i.test(navigator.platform);
});

router.beforeEach(() => { start() });
router.afterEach(() => { done() });

function onKey(e) {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    openPalette();
  }
}
onMounted(() => window.addEventListener('keydown', onKey));
onBeforeUnmount(() => window.removeEventListener('keydown', onKey));
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex; flex-direction: column;
  background:
    radial-gradient(900px 600px at 0% 0%, var(--c-primary-tint), transparent 60%),
    radial-gradient(700px 500px at 100% 0%, color-mix(in srgb, var(--c-info) 12%, transparent), transparent 60%),
    var(--c-bg);
  background-attachment: fixed;
}

.app-nav {
  position: sticky; top: 0; z-index: 100;
  border-bottom: 1px solid var(--c-border);
  backdrop-filter: saturate(180%) blur(14px);
  background: color-mix(in srgb, var(--c-bg) 70%, transparent);
}
.app-nav__inner {
  max-width: 1480px; margin: 0 auto;
  display: flex; align-items: center; gap: 16px;
  padding: 10px 20px;
}

.app-brand {
  display: inline-flex; align-items: center; gap: 8px;
  color: var(--c-primary); text-decoration: none;
  transition: transform var(--t-fast) var(--ease-out);
}
.app-brand:hover { color: var(--c-primary-soft); transform: translateY(-1px); }
.app-brand__text { display: inline-flex; flex-direction: column; line-height: 1; }
.app-brand__name { font-size: 15px; font-weight: 700; color: var(--c-text); letter-spacing: 0.5px; }
.app-brand__sub  { font-size: 10px; color: var(--c-muted); margin-top: 2px; letter-spacing: 1px; }

.app-links { display: flex; gap: 4px; }
.app-link {
  padding: 6px 12px; border-radius: 6px;
  font-size: var(--fs-md); color: var(--c-text-soft);
  text-decoration: none;
  transition: background var(--t-fast) var(--ease-out), color var(--t-fast) var(--ease-out);
}
.app-link:hover { background: var(--c-surface-2); color: var(--c-text); }
.app-link.is-active {
  color: var(--c-primary);
  background: var(--c-primary-tint);
}

.app-actions { margin-left: auto; display: flex; align-items: center; gap: 8px; }

.app-iconbtn {
  width: 34px; height: 34px; display: inline-flex; align-items: center; justify-content: center;
  background: transparent; border: 1px solid var(--c-border); border-radius: 8px;
  color: var(--c-text-soft); cursor: pointer;
  transition: background var(--t-fast) var(--ease-out), color var(--t-fast) var(--ease-out), border-color var(--t-fast) var(--ease-out);
}
.app-iconbtn:hover { color: var(--c-primary); border-color: var(--c-primary); background: var(--c-primary-tint); }

.app-search {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--c-surface-2); border: 1px solid var(--c-border);
  color: var(--c-muted); border-radius: 8px;
  padding: 6px 10px; font-size: var(--fs-sm); cursor: pointer;
  transition: background var(--t-fast) var(--ease-out), color var(--t-fast) var(--ease-out), border-color var(--t-fast) var(--ease-out);
}
.app-search:hover { color: var(--c-text); border-color: var(--c-primary); }
.app-search kbd {
  font-family: inherit; font-size: 10px;
  padding: 1px 5px; border-radius: 4px;
  background: var(--c-surface); color: var(--c-muted);
  border: 1px solid var(--c-border);
}

.app-main {
  max-width: 1480px; width: 100%;
  margin: 0 auto; padding: 20px 20px 64px;
  flex: 1;
}

.page-enter-active, .page-leave-active { transition: opacity var(--t) var(--ease-out), transform var(--t) var(--ease-out); }
.page-enter-from { opacity: 0; transform: translateY(6px); }
.page-leave-to   { opacity: 0; transform: translateY(-6px); }

@media (max-width: 720px) {
  .app-links { display: none; }
  .app-search span { display: none; }
  .app-brand__sub { display: none; }
}
</style>
