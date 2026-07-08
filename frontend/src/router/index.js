import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/common/HomeView.vue'),
    meta: {
      title: '首页'
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/auth/LoginView.vue'),
    meta: {
      title: '登录',
      guestOnly: true
    }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/auth/RegisterView.vue'),
    meta: {
      title: '注册',
      guestOnly: true
    }
  },
  {
    path: '/courses',
    name: 'course-list',
    component: () => import('../views/course/CourseListView.vue'),
    meta: {
      title: '课程列表'
    }
  },
  {
    path: '/courses/:id',
    name: 'course-detail',
    component: () => import('../views/course/CourseDetailView.vue'),
    meta: {
      title: '课程详情'
    }
  },
  {
    path: '/student/dashboard',
    name: 'student-dashboard',
    component: () => import('../views/dashboard/RoleDashboard.vue'),
    meta: {
      title: '学生首页',
      requiresAuth: true,
      roles: ['student']
    }
  },
  {
    path: '/teacher/dashboard',
    name: 'teacher-dashboard',
    component: () => import('../views/dashboard/RoleDashboard.vue'),
    meta: {
      title: '教师首页',
      requiresAuth: true,
      roles: ['teacher']
    }
  },
  {
    path: '/teacher/courses',
    name: 'teacher-courses',
    component: () => import('../views/teacher/TeacherCoursesView.vue'),
    meta: {
      title: '课程管理',
      requiresAuth: true,
      roles: ['teacher', 'admin']
    }
  },
  {
    path: '/teacher/courses/:id/chapters',
    name: 'teacher-course-chapters',
    component: () => import('../views/teacher/TeacherChaptersView.vue'),
    meta: {
      title: '章节管理',
      requiresAuth: true,
      roles: ['teacher', 'admin']
    }
  },
  {
    path: '/admin/dashboard',
    name: 'admin-dashboard',
    component: () => import('../views/dashboard/RoleDashboard.vue'),
    meta: {
      title: '管理员首页',
      requiresAuth: true,
      roles: ['admin']
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const userStore = useUserStore()
  const pageTitle = to.meta?.title ? `${to.meta.title} - WHU 在线教育平台` : 'WHU 在线教育平台'
  document.title = pageTitle

  if (userStore.accessToken && !userStore.userInfo) {
    try {
      await userStore.fetchCurrentUser()
    } catch (error) {
      userStore.clearAuth()
    }
  }

  if (to.meta?.requiresAuth && !userStore.isLoggedIn) {
    return {
      path: '/login',
      query: {
        redirect: to.fullPath
      }
    }
  }

  if (to.meta?.guestOnly && userStore.isLoggedIn) {
    return userStore.redirectPathByRole()
  }

  if (to.meta?.roles?.length && !to.meta.roles.includes(userStore.role)) {
    return userStore.redirectPathByRole()
  }

  return true
})

window.addEventListener('auth:expired', () => {
  const currentPath = router.currentRoute.value.fullPath
  if (currentPath !== '/login') {
    router.push({
      path: '/login',
      query: {
        redirect: currentPath
      }
    })
  }
})

export default router
