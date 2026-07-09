<template>
  <main class="home-page">
    <section class="topbar">
      <div class="brand">
        <span class="brand-mark">WHU</span>
        <span>Online Education</span>
      </div>
      <div class="topbar-actions">
        <el-tag :type="healthTagType" effect="light">{{ healthText }}</el-tag>
        <RouterLink to="/courses">Courses</RouterLink>
        <RouterLink to="/login">Login</RouterLink>
        <el-button type="primary" @click="$router.push('/register')">Register</el-button>
      </div>
    </section>

    <section class="home-stage">
      <aside class="home-index">
        <p class="eyebrow">WHU learning system</p>
        <ul class="rally-index">
          <li class="index-row is-active">
            <span class="index-letter">C</span>
            <span class="index-name">Courses</span>
          </li>
          <li class="index-row">
            <span class="index-letter">V</span>
            <span class="index-name">Video</span>
          </li>
          <li class="index-row">
            <span class="index-letter">E</span>
            <span class="index-name">Exams</span>
          </li>
          <li class="index-row">
            <span class="index-letter">P</span>
            <span class="index-name">Progress</span>
          </li>
        </ul>
      </aside>

      <section class="hero-copy">
        <p class="eyebrow">Interactive education platform</p>
        <h1 class="mega-title">Make learning feel kinetic.</h1>
        <p class="summary">
          课程、章节、视频、资料、学习进度和考试成绩被组织成一条清晰的学习轨迹。界面像作品集一样醒目，逻辑仍然稳定地连接后端。
        </p>
        <p class="health-message">{{ healthMessage }}</p>
        <div class="actions">
          <el-button type="primary" size="large" :icon="Reading" @click="$router.push('/courses')">浏览课程</el-button>
          <el-button size="large" plain :icon="Refresh" @click="refreshHealth">刷新状态</el-button>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Reading, Refresh } from '@element-plus/icons-vue'
import { getHealth } from '../../api/health'

const healthStatus = ref('checking')
const healthMessage = ref('正在检查后端健康状态')

const healthText = computed(() => {
  if (healthStatus.value === 'ok') return '后端已连接'
  if (healthStatus.value === 'error') return '后端未连接'
  return '检查中'
})

const healthTagType = computed(() => {
  if (healthStatus.value === 'ok') return 'success'
  if (healthStatus.value === 'error') return 'warning'
  return 'info'
})

async function refreshHealth() {
  healthStatus.value = 'checking'
  healthMessage.value = '正在检查后端健康状态'

  try {
    const result = await getHealth()
    healthStatus.value = 'ok'
    healthMessage.value = result?.status === 'ok' ? '后端健康检查通过' : '后端已响应'
  } catch (error) {
    healthStatus.value = 'error'
    healthMessage.value = '后端暂未启动，前端页面仍可正常查看'
  }
}

onMounted(() => {
  refreshHealth()
})
</script>

<style scoped>
.home-stage {
  display: grid;
  grid-template-columns: minmax(260px, 0.42fr) minmax(0, 0.58fr);
  gap: clamp(28px, 6vw, 96px);
  align-items: center;
  min-height: calc(100vh - 130px);
  padding-top: 34px;
}

.home-index {
  align-self: center;
}

.hero-copy {
  max-width: 880px;
  justify-self: end;
}

.summary {
  max-width: 720px;
  margin: 30px 0 0;
}

.health-message {
  margin: 22px 0 0;
  color: var(--muted);
  font-weight: 900;
}

.actions {
  margin-top: 34px;
}

@media (max-width: 960px) {
  .home-stage {
    grid-template-columns: 1fr;
    align-items: start;
    min-height: auto;
    padding-top: 54px;
  }

  .hero-copy {
    justify-self: start;
  }
}
</style>
