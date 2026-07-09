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
        <el-dropdown trigger="click" popper-class="user-capsule-dropdown">
          <UserCapsule :user-info="userStore.userInfo" show-caret />
          <template #dropdown>
            <div class="user-dropdown-panel">
              <div class="user-dropdown-head">
                <span>当前状态</span>
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
                <button type="button" class="user-dropdown-link" @click="goSettings">个人设置</button>
                <button type="button" class="user-dropdown-link is-danger" @click="handleLogout">退出登录</button>
              </div>
            </div>
          </template>
        </el-dropdown>
      </template>
      <template v-else>
        <RouterLink to="/login">登录</RouterLink>
        <RouterLink to="/register">注册</RouterLink>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import UserCapsule from './UserCapsule.vue'
import { MOOD_OPTIONS, getMoodDisplay } from '../constants/userMood'
import { useUserStore } from '../stores/user'
import { getCommonErrorMessage, getProfileErrorMessage } from '../utils/errorMessage'

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

  if (userStore.role === 'student' || userStore.role === 'teacher') {
    links.push({ label: '社区中心', to: '/community/forum' })
    links.push({ label: '我的证书', to: '/certificates' })
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
    ElMessage.success('状态已更新')
  } catch (error) {
    ElMessage.error(getProfileErrorMessage(error, '状态更新失败，请稍后重试'))
  } finally {
    moodUpdating.value = ''
  }
}

async function handleLogout() {
  await userStore.logoutUser()
  ElMessage.success('已退出登录')
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
