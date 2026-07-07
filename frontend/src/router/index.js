import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/common/HomeView.vue'),
    meta: {
      title: '首页'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const pageTitle = to.meta?.title ? `${to.meta.title} - WHU 在线教育平台` : 'WHU 在线教育平台'
  document.title = pageTitle
  return true
})

export default router
