<template>
  <main class="home-page">
    <section class="topbar">
      <div class="brand">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </div>
      <div class="topbar-actions">
        <el-tag :type="healthTagType" effect="light">{{ healthText }}</el-tag>
        <RouterLink to="/login">登录</RouterLink>
        <el-button type="primary" @click="$router.push('/register')">注册</el-button>
      </div>
    </section>

    <section class="hero">
      <div class="hero-content">
        <p class="eyebrow">P1 Auth Ready</p>
        <h1>清晰登录，进入自己的学习路径</h1>
        <p class="summary">
          前端已接入注册、邮箱验证码、登录、角色跳转和路由权限拦截。学生与教师会进入不同入口，为后续课程、考试和论坛联调留好位置。
        </p>
        <p class="health-message">{{ healthMessage }}</p>
        <div class="actions">
          <el-button type="primary" size="large" :icon="Refresh" @click="refreshHealth">刷新状态</el-button>
          <el-button size="large" plain :icon="Reading" @click="$router.push('/login')">进入平台</el-button>
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
        <h2>P1 前端能力</h2>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="注册">邮箱验证码与角色选择</el-descriptions-item>
          <el-descriptions-item label="登录">Token 保存与当前用户恢复</el-descriptions-item>
          <el-descriptions-item label="权限">按 student / teacher / admin 拦截路由</el-descriptions-item>
          <el-descriptions-item label="接口">统一处理 code/message/data 响应</el-descriptions-item>
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
  color: var(--ink-900);
  background: var(--blue-050);
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
  background: var(--blue-700);
  border-radius: 6px;
}

.topbar-actions {
  display: flex;
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
  font-size: 64px;
  line-height: 1.04;
}

.summary {
  max-width: 680px;
  margin: 24px 0 0;
  font-size: 18px;
  line-height: 1.8;
  color: var(--slate-500);
}

.health-message {
  margin: 18px 0 0;
  color: var(--slate-500);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 32px;
}

.status-panel {
  padding: 24px;
  background: var(--white);
  border: 1px solid var(--border-blue);
  border-radius: 8px;
  box-shadow: 0 16px 48px rgba(23, 32, 51, 0.08);
}

.mini-path {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.mini-path span {
  width: 14px;
  height: 14px;
  background: var(--blue-700);
  border-radius: 999px;
}

.mini-path i {
  width: 64px;
  height: 2px;
  background: var(--blue-500);
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
