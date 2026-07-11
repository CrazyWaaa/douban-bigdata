<template>
  <div>
    <h2>电影数据大屏</h2>
    <div v-if="loading" class="muted">加载中...</div>
    <div v-else-if="error" class="muted">暂无数据：{{ error }}</div>
    <div v-else class="card">
      <div class="muted">总影片数：{{ data?.total ?? '-' }}　平均评分：{{ data?.avg_rating?.toFixed?.(2) ?? '-' }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const data = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    data.value = await api.dashboard()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>