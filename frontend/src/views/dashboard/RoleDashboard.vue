<template>
  <main class="dashboard-page">
    <AppNav />

    <section class="dashboard-hero">
      <div class="hero-card kinetic-panel">
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
        <span class="card-label">Current user</span>
        <strong>{{ userStore.userInfo?.username || userStore.userInfo?.email || '已登录用户' }}</strong>
        <span class="status-pill">{{ roleCopy.roleName }}</span>
        <div class="mini-index" aria-hidden="true">
          <span>01</span>
          <span>02</span>
          <span>03</span>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import AppNav from '../../components/AppNav.vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

const roleText = {
  student: {
    eyebrow: 'Student workspace',
    title: 'Keep the course moving.',
    description: '查看已加入课程，回到视频学习页，系统会持续记录章节进度。P4 阶段已接入考试和成绩能力。',
    roleName: '学生',
    actions: [
      { label: '我的课程', path: '/student/courses', primary: true },
      { label: '我的成绩', path: '/student/scores' },
      { label: '课程广场', path: '/courses' }
    ]
  },
  teacher: {
    eyebrow: 'Teacher workspace',
    title: 'Shape the learning material.',
    description: '创建课程、维护章节、上传视频资料，并控制课程发布状态。学生端会基于这些内容进入学习和考试流程。',
    roleName: '教师',
    actions: [
      { label: '管理课程', path: '/teacher/courses', primary: true },
      { label: '课程广场', path: '/courses' }
    ]
  },
  admin: {
    eyebrow: 'Admin workspace',
    title: 'Audit the system boundary.',
    description: '管理员可辅助查看课程数据和教师内容管理入口，检查课程、权限、考试与提交记录的边界。',
    roleName: '管理员',
    actions: [
      { label: '课程管理', path: '/teacher/courses', primary: true },
      { label: '课程广场', path: '/courses' }
    ]
  }
}

const roleCopy = computed(() => roleText[userStore.role] || roleText.student)
</script>

<style scoped>
.dashboard-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 28px;
  align-items: stretch;
  min-height: calc(100vh - 150px);
  margin: 64px auto 0;
}

.hero-card {
  display: grid;
  align-content: end;
  min-height: 520px;
  padding: 42px;
}

.hero-card h1,
.hero-card p {
  color: var(--paper);
}

.hero-card p:not(.eyebrow) {
  max-width: 740px;
  color: rgba(246, 241, 230, 0.72);
}

.quick-actions {
  margin-top: 34px;
}

.dashboard-card {
  display: grid;
  gap: 18px;
  align-content: center;
  padding: 32px;
}

.card-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.dashboard-card strong {
  font-size: clamp(36px, 4vw, 62px);
  font-weight: 900;
  line-height: 0.9;
  letter-spacing: -0.07em;
}

.mini-index {
  display: flex;
  gap: 10px;
  margin-top: 30px;
  color: var(--hot);
  font-weight: 900;
}

@media (max-width: 960px) {
  .dashboard-hero {
    grid-template-columns: 1fr;
  }
}
</style>
