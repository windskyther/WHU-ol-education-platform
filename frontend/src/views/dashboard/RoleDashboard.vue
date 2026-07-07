<template>
  <main class="dashboard-page">
    <nav class="dashboard-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </RouterLink>
      <el-button plain @click="handleLogout">退出登录</el-button>
    </nav>

    <section class="dashboard-hero">
      <div>
        <p class="eyebrow">{{ roleCopy.eyebrow }}</p>
        <h1>{{ roleCopy.title }}</h1>
        <p>{{ roleCopy.description }}</p>
      </div>
      <div class="dashboard-card">
        <span class="card-label">当前用户</span>
        <strong>{{ userStore.userInfo?.username || userStore.userInfo?.email || '已登录用户' }}</strong>
        <span>{{ roleCopy.roleName }}</span>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()

const roleText = {
  student: {
    eyebrow: 'Student workspace',
    title: '学生学习入口已准备',
    description: 'P2-P4 阶段会在这里接入我的课程、课程学习、考试与成绩。',
    roleName: '学生'
  },
  teacher: {
    eyebrow: 'Teacher workspace',
    title: '教师工作台已准备',
    description: '后续会在这里接入课程管理、章节资料、考试题目和成绩管理。',
    roleName: '教师'
  },
  admin: {
    eyebrow: 'Admin workspace',
    title: '管理入口已准备',
    description: '管理员入口用于后续维护用户、课程和平台基础数据。',
    roleName: '管理员'
  }
}

const roleCopy = computed(() => roleText[userStore.role] || roleText.student)

async function handleLogout() {
  await userStore.logoutUser()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>
