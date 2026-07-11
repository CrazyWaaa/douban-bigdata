import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/genre', name: 'genre', component: () => import('../views/Genre.vue') },
  { path: '/country', name: 'country', component: () => import('../views/Country.vue') },
  { path: '/year', name: 'year', component: () => import('../views/Year.vue') },
  { path: '/top', name: 'top', component: () => import('../views/Top.vue') },
  { path: '/movie/:id', name: 'movie', component: () => import('../views/Movie.vue') }
]

export default createRouter({
  history: createWebHistory(),
  routes
})