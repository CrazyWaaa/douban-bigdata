<template>
  <div>
    <nav class="nav">
      <router-link to="/">大屏</router-link>
      <router-link to="/top">榜单</router-link>
      <router-link to="/genre">类型</router-link>
      <router-link to="/country">地区</router-link>
      <router-link to="/year">年代</router-link>
      <router-link to="/search">搜索</router-link>
      <div class="nav-search">
        <input
          v-model="searchKw"
          @keyup.enter="goSearch"
          placeholder="搜片名 / 导演 / 演员"
        />
      </div>
    </nav>
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchKw = ref('')

function goSearch() {
  const q = searchKw.value.trim()
  if (!q) return
  router.push({ path: '/search', query: { q } })
}
</script>

<style scoped>
.nav-search { margin-left: auto; }
.nav-search input {
  background: #0b1220; border: 1px solid #1f2937; color: var(--text);
  padding: 4px 10px; border-radius: 4px; font-size: 13px; width: 220px;
}
.nav-search input:focus { outline: none; border-color: var(--primary); }
</style>