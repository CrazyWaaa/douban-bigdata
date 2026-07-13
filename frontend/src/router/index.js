import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/',           name: 'dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/top',        name: 'top',       component: () => import('../views/Top.vue') },
  { path: '/genre',      name: 'genre',     component: () => import('../views/Genre.vue') },
  { path: '/country',    name: 'country',   component: () => import('../views/Country.vue') },
  { path: '/year',       name: 'year',      component: () => import('../views/Year.vue') },
  { path: '/search',     name: 'search',    component: () => import('../views/Search.vue') },
  { path: '/movie/:id',  name: 'movie',     component: () => import('../views/Movie.vue') },

  // 高级可视化页面
  { path: '/radar',      name: 'radar',     component: () => import('../views/Radar.vue') },
  { path: '/sankey',     name: 'sankey',    component: () => import('../views/Sankey.vue') },
  { path: '/treemap',    name: 'treemap',   component: () => import('../views/Treemap.vue') },
  { path: '/wordcloud',  name: 'wordcloud', component: () => import('../views/WordCloud.vue') },
  { path: '/gauge',      name: 'gauge',     component: () => import('../views/Gauge.vue') },
  { path: '/funnel',     name: 'funnel',    component: () => import('../views/Funnel.vue') },
  { path: '/calendar',   name: 'calendar',  component: () => import('../views/Calendar.vue') },
  { path: '/network',    name: 'network',   component: () => import('../views/Network.vue') },
  { path: '/map',        name: 'map',       component: () => import('../views/MapView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
