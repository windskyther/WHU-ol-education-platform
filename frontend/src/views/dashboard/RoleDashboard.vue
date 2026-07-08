<template>
  <main class="dashboard-page">
    <nav class="dashboard-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </RouterLink>
      <div class="dashboard-actions">
        <el-button v-if="userStore.role === 'student'" type="primary" :icon="Reading" @click="$router.push('/student/courses')">
          我的课程
        </el-button>
        <el-button v-if="userStore.role === 'teacher' || userStore.role === 'admin'" type="primary" :icon="Collection" @click="$router.push('/teacher/courses')">
          课程管理
        </el-button>
        <el-button plain @click="$router.push('/courses')">课程列表</el-button>
        <el-button plain @click="handleLogout">退出登录</el-button>
      </div>
    </nav>

    <section class="dashboard-hero">
      <div class="hero-card momentum-ribbon">
        <p class="eyebrow">{{ roleCopy.eyebrow }}</p>
        <h1>{{ roleCopy.title }}</h1>
        <p>{{ roleCopy.description }}</p>
        <div class="quick-actions">
          <el-button v-for="action in roleCopy.actions" :key="action.path" :type="action.primary ? 'primary' : ''" @click="$router.push(action.path)">
            {{ action.label }}
          </el-button>
        </div>
      </div>
      <div class="dashboard-card">
        <span class="card-label">当前用户</span>
        <strong>{{ userStore.userInfo?.username || userStore.userInfo?.email || '已登录用户' }}</strong>
        <span class="status-pill">{{ roleCopy.roleName }}</span>
        <div class="momentum-ticks" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Collection, Reading } from '@element-plus/icons-vue'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()

const roleText = {
  student: {
    eyebrow: 'Student workspace',
    title: '继续你正在推进的课程',
    description: '查看已加入课程，回到视频学习页，系统会持续记录章节进度。P3 阶段聚焦学习闭环，不包含考试和论坛。',
    roleName: '学生',
    actions: [
      { label: '我的课程', path: '/student/courses', primary: true },
      { label: '发现课程', path: '/courses' }
    ]
  },
  teacher: {
    eyebrow: 'Teacher workspace',
    title: '让课程内容保持清晰可学',
    description: '创建课程、维护章节、上传视频和资料，并控制课程发布状态。学生端会基于这些内容进入学习页。',
    roleName: '教师',
    actions: [
      { label: '管理课程', path: '/teacher/courses', primary: true },
      { label: '公开课程', path: '/courses' }
    ]
  },
  admin: {
    eyebrow: 'Admin workspace',
    title: '协助检查课程与权限边界',
    description: '管理员可辅助查看课程数据和教师内容管理入口，具体后台治理能力由后续阶段扩展。',
    roleName: '管理员',
    actions: [
      { label: '课程管理', path: '/teacher/courses', primary: true },
      { label: '课程列表', path: '/courses' }
    ]
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
.hero-card {
  position: relative;
  padding: 36px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.hero-card > * {
  position: relative;
  z-index: 1;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 26px;
}
</style>
