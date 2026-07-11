<template>
  <div>
    <h2>影片详情</h2>
    <div v-if="data" class="card">
      <h3>{{ data.title }}</h3>
      <div class="muted">{{ data.director }} / {{ data.actors }} / {{ data.year }} / {{ data.country }} / {{ data.genre }}</div>
      <p style="margin-top:8px;">{{ data.summary }}</p>
    </div>
    <div v-else class="muted">加载中...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'

const data = ref(null)
const route = useRoute()
onMounted(async () => { data.value = (await api.detail(route.params.id)).data })
</script>