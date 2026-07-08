<template>
  <main class="dashboard-page">
    <nav class="dashboard-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </RouterLink>
      <div class="dashboard-actions">
        <el-button v-if="userStore.role === 'teacher' || userStore.role === 'admin'" type="primary" :icon="Collection" @click="$router.push('/teacher/courses')">
          课程管理
        </el-button>
        <el-button plain @click="$router.push('/courses')">课程列表</el-button>
        <el-button plain @click="handleLogout">退出登录</el-button>
      </div>
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
import { Collection } from '@element-plus/icons-vue'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()

const roleText = {
  student: {
    eyebrow: 'Student workspace',
    title: '学生学习入口已准备',
    description: 'P2 阶段可以浏览已发布课程和课程章节。选课、学习进度和考试会在后续阶段接入。',
    roleName: '学生'
  },
  teacher: {
    eyebrow: 'Teacher workspace',
    title: '教师课程工作台已准备',
    description: '你可以创建课程、维护章节、上传视频和资料，并控制课程发布状态。',
    roleName: '教师'
  },
  admin: {
    eyebrow: 'Admin workspace',
    title: '管理入口已准备',
    description: '管理员可以辅助检查课程数据和权限边界，具体后台治理能力由后续阶段扩展。',
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

<style scoped>
.dashboard-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
</style>
