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
        <span class="card-label">{{ t('dashboard.currentUser') }}</span>
        <strong>{{ userStore.userInfo?.username || userStore.userInfo?.email || t('dashboard.loggedInUser') }}</strong>
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
import { useI18n } from 'vue-i18n'
import AppNav from '../../components/AppNav.vue'
import { useUserStore } from '../../stores/user'

const { t } = useI18n()
const userStore = useUserStore()

const roleText = computed(() => ({
  student: {
    eyebrow: t('dashboard.studentWorkspace'),
    title: t('dashboard.studentTitle'),
    description: t('dashboard.studentDescription'),
    roleName: t('dashboard.studentRoleName'),
    actions: [
      { label: t('dashboard.myCourses'), path: '/student/courses', primary: true },
      { label: t('dashboard.myScores'), path: '/student/scores' },
      { label: t('dashboard.coursesSquare'), path: '/courses' }
    ]
  },
  teacher: {
    eyebrow: t('dashboard.teacherWorkspace'),
    title: t('dashboard.teacherTitle'),
    description: t('dashboard.teacherDescription'),
    roleName: t('dashboard.teacherRoleName'),
    actions: [
      { label: t('dashboard.manageCourses'), path: '/teacher/courses', primary: true },
      { label: t('dashboard.coursesSquare'), path: '/courses' }
    ]
  },
  admin: {
    eyebrow: t('dashboard.adminWorkspace'),
    title: t('dashboard.adminTitle'),
    description: t('dashboard.adminDescription'),
    roleName: t('dashboard.adminRoleName'),
    actions: [
      { label: t('dashboard.courseManagement'), path: '/teacher/courses', primary: true },
      { label: t('dashboard.coursesSquare'), path: '/courses' }
    ]
  }
}))

const roleCopy = computed(() => roleText.value[userStore.role] || roleText.value.student)
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
