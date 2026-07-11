<template>
  <div>
    <nav class="nav">
      <router-link to="/">大屏</router-link>
      <router-link to="/genre">类型</router-link>
      <router-link to="/country">地区</router-link>
      <router-link to="/year">年份</router-link>
      <router-link to="/top">高分榜</router-link>
    </nav>
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
// 全局布局
</script>