<template>
  <main class="home-page">
    <section class="topbar">
      <div class="brand">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </div>
      <div class="topbar-actions">
        <el-tag :type="healthTagType" effect="light">{{ healthText }}</el-tag>
        <RouterLink to="/courses">课程列表</RouterLink>
        <RouterLink to="/login">登录</RouterLink>
        <el-button type="primary" @click="$router.push('/register')">注册</el-button>
      </div>
    </section>

    <section class="home-hero">
      <div class="hero-copy">
        <p class="eyebrow">P3 Learning flow</p>
        <h1>让每一段学习都有清晰的下一步</h1>
        <p class="summary">
          平台已支持课程浏览、教师课程管理、章节上传，以及学生选课、视频学习、资料下载和进度记录。学习过程更轻快，也更容易坚持。
        </p>
        <p class="health-message">{{ healthMessage }}</p>
        <div class="actions">
          <el-button type="primary" size="large" :icon="Reading" @click="$router.push('/courses')">浏览课程</el-button>
          <el-button size="large" plain :icon="Refresh" @click="refreshHealth">刷新状态</el-button>
        </div>
      </div>

      <div class="hero-board momentum-ribbon">
        <div class="momentum-ticks" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <h2>学习主流程</h2>
        <div class="flow-list">
          <div>
            <strong>01</strong>
            <span>选择课程</span>
          </div>
          <div>
            <strong>02</strong>
            <span>加入学习</span>
          </div>
          <div>
            <strong>03</strong>
            <span>观看章节视频</span>
          </div>
          <div>
            <strong>04</strong>
            <span>保存学习进度</span>
          </div>
        </div>
      </div>
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
.home-page {
  min-height: 100vh;
  padding: 24px;
  overflow: hidden;
  color: var(--ink-900);
  background:
    radial-gradient(circle at 14% 12%, rgba(245, 158, 11, 0.2), transparent 28%),
    radial-gradient(circle at 88% 10%, rgba(99, 102, 241, 0.22), transparent 32%),
    var(--bg-warm);
}

.home-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
  gap: 34px;
  align-items: center;
  max-width: 1180px;
  margin: 0 auto;
  padding: 74px 0 40px;
}

.hero-copy {
  max-width: 760px;
}

h1 {
  max-width: 760px;
  margin: 0;
  font-size: clamp(44px, 6vw, 70px);
  line-height: 1.02;
}

.summary {
  max-width: 680px;
  margin: 22px 0 0;
  color: var(--slate-600);
  font-size: 18px;
  line-height: 1.8;
}

.health-message {
  margin: 18px 0 0;
  color: var(--slate-500);
  font-weight: 700;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 30px;
}

.hero-board {
  position: relative;
  padding: 28px;
  overflow: hidden;
  background: var(--white);
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.hero-board > * {
  position: relative;
  z-index: 1;
}

.hero-board h2 {
  margin: 20px 0 18px;
  font-size: 26px;
}

.flow-list {
  display: grid;
  gap: 12px;
}

.flow-list div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  background: rgba(99, 102, 241, 0.07);
  border-radius: var(--radius-md);
}

.flow-list strong {
  color: var(--accent-orange);
  font-size: 24px;
}

.flow-list span {
  color: var(--ink-700);
  font-weight: 800;
}

@media (max-width: 860px) {
  .home-hero {
    grid-template-columns: 1fr;
    padding-top: 44px;
  }
}
</style>
