<template>
  <div>
    <h2>高分榜 TOP 50</h2>
    <div class="card" style="padding:0;">
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#1f2937;">
            <th style="text-align:left;padding:8px;">排名</th>
            <th style="text-align:left;padding:8px;">片名</th>
            <th style="text-align:left;padding:8px;">导演</th>
            <th style="text-align:left;padding:8px;">年份</th>
            <th style="text-align:left;padding:8px;">评分</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in items" :key="m.douban_id" style="border-top:1px solid #1f2937;">
            <td style="padding:8px;">{{ m.rank }}</td>
            <td style="padding:8px;"><router-link :to="`/movie/${m.douban_id}`">{{ m.title }}</router-link></td>
            <td style="padding:8px;">{{ m.director }}</td>
            <td style="padding:8px;">{{ m.year }}</td>
            <td style="padding:8px;">{{ m.rating?.toFixed?.(1) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const items = ref([])
onMounted(async () => { items.value = (await api.topRated(50)).data || [] })
</script>