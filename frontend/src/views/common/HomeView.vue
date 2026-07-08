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

    <section class="hero">
      <div class="hero-content">
        <p class="eyebrow">P2 Course ready</p>
        <h1>让课程像枝条一样清楚生长</h1>
        <p class="summary">
          平台已接入课程浏览、课程详情、教师课程管理、章节维护和视频资料上传。P2 聚焦内容建设，学生端只浏览已发布课程。
        </p>
        <p class="health-message">{{ healthMessage }}</p>
        <div class="actions">
          <el-button type="primary" size="large" :icon="Reading" @click="$router.push('/courses')">浏览课程</el-button>
          <el-button size="large" plain :icon="Refresh" @click="refreshHealth">刷新状态</el-button>
        </div>
      </div>

      <div class="status-panel">
        <div class="mini-path" aria-hidden="true">
          <span></span>
          <i></i>
          <span></span>
          <i></i>
          <span></span>
        </div>
        <h2>P2 前端能力</h2>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="课程">分页、搜索、分类和难度筛选</el-descriptions-item>
          <el-descriptions-item label="详情">课程信息与章节目录展示</el-descriptions-item>
          <el-descriptions-item label="教师">创建、编辑、发布、下架、删除课程</el-descriptions-item>
          <el-descriptions-item label="章节">章节增删改与视频/资料上传</el-descriptions-item>
        </el-descriptions>
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
  color: var(--ink-900);
  background:
    linear-gradient(180deg, rgba(232, 246, 238, 0.78), rgba(246, 251, 248, 0.88) 420px),
    var(--mint-050);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1120px;
  min-height: 44px;
  margin: 0 auto;
  padding: 24px;
}

.topbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.topbar-actions a {
  color: var(--ink-900);
  font-weight: 700;
  text-decoration: none;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.18fr) minmax(320px, 0.82fr);
  gap: 30px;
  align-items: center;
  max-width: 1120px;
  margin: 0 auto;
  padding: 68px 24px;
}

.hero-content {
  max-width: 720px;
}

h1 {
  max-width: 720px;
  margin: 0;
  font-size: clamp(42px, 6vw, 62px);
  line-height: 1.05;
}

.summary {
  max-width: 680px;
  margin: 22px 0 0;
  font-size: 18px;
  line-height: 1.8;
  color: var(--slate-600);
}

.health-message {
  margin: 18px 0 0;
  color: var(--slate-500);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 30px;
}

.status-panel {
  padding: 22px;
  background: var(--white);
  border: 1px solid var(--border-green);
  border-radius: 8px;
  box-shadow: var(--shadow-card);
}

.mini-path {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
}

.mini-path span {
  width: 12px;
  height: 12px;
  background: var(--green-700);
  border-radius: 999px;
}

.mini-path i {
  width: 58px;
  height: 2px;
  background: var(--green-300);
}

.status-panel h2 {
  margin: 0 0 18px;
  font-size: 20px;
}

@media (max-width: 820px) {
  .hero {
    grid-template-columns: 1fr;
    padding-top: 40px;
  }

  .topbar {
    align-items: flex-start;
    gap: 16px;
    flex-direction: column;
  }
}
</style>
