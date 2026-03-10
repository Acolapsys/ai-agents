import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component:  DashboardView
  },
  {
    path: '/agents',
    name: 'agents',
    component: () => import('@/views/AgentsView.vue') // ленивая загрузка
  },
  {
    path: '/chats',
    name: 'chats',
    component: () => import('@/views/ChatsView.vue') // ленивая загрузка
  },
  {
    path: '/logs',
    name: 'logs',
    component: () => import('@/views/LogsView.vue') // ленивая загрузка
  },
  {
    path: '/tasks',
    name: 'tasks',
    component: () => import('@/views/TasksView.vue') // ленивая загрузка
  },
  {
    path: '/stats',
    name: 'stats',
    component: () => import('@/views/StatsView.vue') // ленивая загрузка
  },
  {
    path: '/billing',
    name: 'billing',
    component: () => import('@/views/BillingView.vue') // ленивая загрузка
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue') // ленивая загрузка
  },
  {
    path: '/library',
    name: 'library',
    component: () => import('@/views/LibraryView.vue') // ленивая загрузка
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router