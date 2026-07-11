<template>
  <div>
    <h2>高分榜 TOP 50</h2>
    <div class="card" style="padding:0;">
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#1f2937;">
            <th style="text-align:left;padding:10px 8px;">排名</th>
            <th style="text-align:left;padding:10px 8px;">片名</th>
            <th style="text-align:left;padding:10px 8px;">导演</th>
            <th style="text-align:left;padding:10px 8px;">年份</th>
            <th style="text-align:left;padding:10px 8px;">评分</th>
            <th style="text-align:left;padding:10px 8px;">评价数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in items" :key="m.douban_id" style="border-top:1px solid #1f2937;">
            <td style="padding:10px 8px;font-weight:bold;color:var(--primary);">{{ m.rank }}</td>
            <td style="padding:10px 8px;">
              <router-link :to="`/movie/${m.douban_id}`">{{ m.title }}</router-link>
              <div v-if="m.quote" class="muted" style="font-size:12px;margin-top:4px;">"{{ m.quote }}"</div>
            </td>
            <td style="padding:10px 8px;font-size:13px;color:#cbd5e1;">{{ m.director }}</td>
            <td style="padding:10px 8px;">{{ m.year }}</td>
            <td style="padding:10px 8px;color:var(--primary);font-weight:bold;">{{ m.rating?.toFixed?.(1) }}</td>
            <td style="padding:10px 8px;font-size:13px;color:#cbd5e1;">{{ m.rating_count?.toLocaleString?.() }}</td>
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