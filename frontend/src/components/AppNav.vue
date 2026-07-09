<template>
  <nav class="app-nav">
    <RouterLink class="brand-link" :to="brandPath">
      <span class="brand-mark">WHU</span>
      <span>Online Education</span>
    </RouterLink>

    <div class="nav-actions">
      <RouterLink
        v-for="link in mainLinks"
        :key="link.to"
        :to="link.to"
        :class="{ 'is-nav-active': isActiveLink(link.to) }"
      >
        {{ link.label }}
      </RouterLink>

      <slot name="actions" />

      <template v-if="userStore.isLoggedIn">
        <span class="nav-user">{{ displayName }}</span>
        <el-button plain size="small" @click="handleLogout">退出</el-button>
      </template>
      <template v-else>
        <RouterLink to="/login">登录</RouterLink>
        <RouterLink to="/register">注册</RouterLink>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const brandPath = computed(() => {
  if (userStore.isLoggedIn) {
    return userStore.redirectPathByRole()
  }
  return '/'
})

const displayName = computed(() => {
  return userStore.userInfo?.username || userStore.userInfo?.email || '已登录用户'
})

const mainLinks = computed(() => {
  const links = [{ label: '课程广场', to: '/courses' }]

  if (userStore.role === 'student') {
    links.unshift(
      { label: '工作台', to: '/student/dashboard' },
      { label: '我的课程', to: '/student/courses' },
      { label: '我的成绩', to: '/student/scores' }
    )
  } else if (userStore.role === 'teacher' || userStore.role === 'admin') {
    links.unshift(
      { label: '工作台', to: userStore.redirectPathByRole() },
      { label: '课程管理', to: '/teacher/courses' }
    )
  }

  return links
})

function isActiveLink(path) {
  if (path === '/courses') {
    return route.path === '/courses' || route.name === 'course-detail'
  }

  if (path === '/student/dashboard' || path === '/teacher/dashboard' || path === '/admin/dashboard') {
    return route.path.endsWith('/dashboard')
  }

  return route.path === path || route.path.startsWith(`${path}/`)
}

async function handleLogout() {
  await userStore.logoutUser()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>
