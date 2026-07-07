<template>
  <main class="home-page">
    <section class="topbar">
      <div class="brand">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </div>
      <el-tag :type="healthTagType" effect="light">{{ healthText }}</el-tag>
    </section>

    <section class="hero">
      <div class="hero-content">
        <p class="eyebrow">P0 Frontend Skeleton</p>
        <h1>在线教育平台前端骨架已就绪</h1>
        <p class="summary">
          当前工程已接入 Vue Router、Pinia、Axios 与 Element Plus，可作为后续登录注册、课程学习、考试和论坛页面的基础。
        </p>
        <p class="health-message">{{ healthMessage }}</p>
        <div class="actions">
          <el-button type="primary" size="large" :icon="Refresh" @click="refreshHealth">刷新状态</el-button>
          <el-button size="large" plain :icon="Reading">课程入口</el-button>
        </div>
      </div>

      <div class="status-panel">
        <h2>基础能力</h2>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="路由">Vue Router 已配置首页</el-descriptions-item>
          <el-descriptions-item label="状态">Pinia 用户状态骨架已创建</el-descriptions-item>
          <el-descriptions-item label="请求">Axios 默认使用 /api 前缀</el-descriptions-item>
          <el-descriptions-item label="组件">Element Plus 已全局接入</el-descriptions-item>
        </el-descriptions>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
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
    healthMessage.value = result?.message || '后端健康检查通过'
  } catch (error) {
    healthStatus.value = 'error'
    healthMessage.value = '后端暂未启动，前端骨架仍可正常运行'
  }
}

onMounted(() => {
  refreshHealth()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  color: #172033;
  background:
    linear-gradient(135deg, rgba(9, 92, 142, 0.12), transparent 34%),
    linear-gradient(315deg, rgba(31, 111, 82, 0.12), transparent 38%),
    #f6f8fb;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1120px;
  margin: 0 auto;
  padding: 24px;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  font-weight: 700;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 32px;
  color: #ffffff;
  background: #1f6f52;
  border-radius: 6px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.7fr);
  gap: 32px;
  align-items: center;
  max-width: 1120px;
  margin: 0 auto;
  padding: 72px 24px;
}

.hero-content {
  max-width: 720px;
}

.eyebrow {
  margin: 0 0 16px;
  font-size: 14px;
  font-weight: 700;
  color: #1f6f52;
  text-transform: uppercase;
}

h1 {
  max-width: 720px;
  margin: 0;
  font-size: 72px;
  line-height: 1.04;
}

.summary {
  max-width: 680px;
  margin: 24px 0 0;
  font-size: 18px;
  line-height: 1.8;
  color: #4f5d75;
}

.health-message {
  margin: 18px 0 0;
  color: #637083;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 32px;
}

.status-panel {
  padding: 24px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid #dfe6ef;
  border-radius: 8px;
  box-shadow: 0 16px 48px rgba(23, 32, 51, 0.08);
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

  h1 {
    font-size: 40px;
  }
}
</style>
