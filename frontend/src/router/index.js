import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'chart',
      component: () => import('@/views/ChartView.vue')
    },
    {
      path: '/entry',
      name: 'entry',
      component: () => import('@/views/EntryView.vue')
    },
    {
      path: '/import',
      name: 'import',
      component: () => import('@/views/ImportView.vue')
    },
    {
      path: '/style-preview',
      name: 'style-preview',
      component: () => import('@/views/StylePreview.vue')
    },
    {
      path: '/design-preview',
      name: 'design-preview',
      component: () => import('@/views/DesignPreview.vue')
    }
  ]
})

export default router
