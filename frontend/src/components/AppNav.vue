<template>
  <nav class="app-nav">
    <RouterLink class="brand-link" :to="brandPath">
      <span class="brand-mark">WHU</span>
      <span>{{ t('nav.brandSuffix') }}</span>
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
        <el-dropdown trigger="click" popper-class="user-capsule-dropdown">
          <UserCapsule :user-info="userStore.userInfo" show-caret />
          <template #dropdown>
            <div class="user-dropdown-panel">
              <div class="user-dropdown-head">
                <span>{{ t('nav.currentStatus') }}</span>
                <strong>{{ currentMood.text }}</strong>
              </div>
              <div class="mood-capsule-grid mood-capsule-grid--compact">
                <button
                  v-for="option in MOOD_OPTIONS"
                  :key="option.key"
                  type="button"
                  class="mood-capsule"
                  :class="{ 'is-active': userStore.mood === option.key }"
                  :disabled="moodUpdating === option.key"
                  @click="handleMoodChange(option.key)"
                >
                  <span>{{ option.emoji }}</span>
                  <span>{{ option.label }}</span>
                </button>
              </div>
              <div class="user-dropdown-actions">
                <button type="button" class="user-dropdown-link" @click="goSettings">{{ t('nav.personalSettings') }}</button>
                <button type="button" class="user-dropdown-link is-danger" @click="handleLogout">{{ t('nav.logout') }}</button>
              </div>
            </div>
          </template>
        </el-dropdown>
      </template>
      <template v-else>
        <RouterLink to="/login">{{ t('nav.login') }}</RouterLink>
        <RouterLink to="/register">{{ t('nav.register') }}</RouterLink>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import UserCapsule from './UserCapsule.vue'
import { MOOD_OPTIONS, getMoodDisplay } from '../constants/userMood'
import { useUserStore } from '../stores/user'
import { getCommonErrorMessage, getProfileErrorMessage } from '../utils/errorMessage'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const moodUpdating = ref('')

const brandPath = computed(() => {
  if (userStore.isLoggedIn) {
    return userStore.redirectPathByRole()
  }
  return '/'
})

const currentMood = computed(() => getMoodDisplay(userStore.mood))

const mainLinks = computed(() => {
  const links = [{ label: t('nav.coursesSquare'), to: '/courses' }]

  if (userStore.role === 'student') {
    links.unshift(
      { label: t('nav.workspace'), to: '/student/dashboard' },
      { label: t('nav.myCourses'), to: '/student/courses' },
      { label: t('nav.myScores'), to: '/student/scores' }
    )
  } else if (userStore.role === 'teacher' || userStore.role === 'admin') {
    links.unshift(
      { label: t('nav.workspace'), to: userStore.redirectPathByRole() },
      { label: t('nav.courseManagement'), to: '/teacher/courses' }
    )
  }

  if (userStore.role === 'student' || userStore.role === 'teacher') {
    links.push({ label: t('nav.community'), to: '/community/forum' })
  }

  if (userStore.role === 'student') {
    links.push({ label: t('nav.myCertificates'), to: '/certificates' })
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

  if (path === '/community/forum') {
    return route.path.startsWith('/community')
  }

  if (path === '/certificates') {
    return route.path.startsWith('/certificates')
  }

  return route.path === path || route.path.startsWith(`${path}/`)
}

function goSettings() {
  router.push('/settings')
}

async function handleMoodChange(moodKey) {
  if (moodUpdating.value || userStore.mood === moodKey) return
  moodUpdating.value = moodKey
  try {
    await userStore.updateProfile({ mood: moodKey })
    ElMessage.success(t('nav.statusUpdated'))
  } catch (error) {
    ElMessage.error(getProfileErrorMessage(error, t('nav.statusUpdateFailed')))
  } finally {
    moodUpdating.value = ''
  }
}

async function handleLogout() {
  await userStore.logoutUser()
  ElMessage.success(t('nav.loggedOut'))
  router.push('/login')
}
</script>

<style scoped>
.user-dropdown-panel {
  min-width: 260px;
  padding: 14px;
}

.user-dropdown-head {
  display: grid;
  gap: 6px;
  margin-bottom: 12px;
}

.user-dropdown-head span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.user-dropdown-head strong {
  font-size: 14px;
  font-weight: 900;
}

.user-dropdown-actions {
  display: grid;
  gap: 8px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
}

.user-dropdown-link {
  width: 100%;
  padding: 8px 10px;
  color: var(--ink);
  background: transparent;
  border: 0;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 900;
  text-align: left;
  cursor: pointer;
}

.user-dropdown-link:hover {
  background: rgba(25, 25, 23, 0.06);
}

.user-dropdown-link.is-danger {
  color: var(--danger);
}
</style>
