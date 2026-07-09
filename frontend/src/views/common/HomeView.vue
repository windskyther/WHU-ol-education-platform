<template>
  <main class="home-page">
    <section class="topbar">
      <div class="brand">
        <span class="brand-mark">WHU</span>
        <span>{{ t('nav.brandSuffix') }}</span>
      </div>
      <div class="topbar-actions">
        <el-tag :type="healthTagType" effect="light">{{ healthText }}</el-tag>
        <RouterLink to="/courses">{{ t('home.coursesSquare') }}</RouterLink>
        <RouterLink to="/login">{{ t('home.login') }}</RouterLink>
        <el-button type="primary" @click="$router.push('/register')">{{ t('home.register') }}</el-button>
      </div>
    </section>

    <section class="home-stage">
      <aside class="home-index">
        <p class="eyebrow">{{ t('home.learningSystem') }}</p>
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
        <p class="eyebrow">{{ t('home.interactiveEducationPlatform') }}</p>
        <h1 class="mega-title">{{ t('home.heroTitle') }}</h1>
        <p class="summary">
          {{ t('home.heroSummary') }}
        </p>
        <p class="health-message">{{ healthMessage }}</p>
        <div class="actions">
          <el-button type="primary" size="large" :icon="Reading" @click="$router.push('/courses')">{{ t('home.browseCourses') }}</el-button>
          <el-button size="large" plain :icon="Refresh" @click="refreshHealth">{{ t('home.refreshStatus') }}</el-button>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Reading, Refresh } from '@element-plus/icons-vue'
import { getHealth } from '../../api/health'

const { t } = useI18n()
const healthStatus = ref('checking')
const healthMessageKey = ref('home.healthChecking')

const healthText = computed(() => {
  if (healthStatus.value === 'ok') return t('home.backendConnected')
  if (healthStatus.value === 'error') return t('home.backendDisconnected')
  return t('home.checking')
})

const healthMessage = computed(() => t(healthMessageKey.value))

const healthTagType = computed(() => {
  if (healthStatus.value === 'ok') return 'success'
  if (healthStatus.value === 'error') return 'warning'
  return 'info'
})

async function refreshHealth() {
  healthStatus.value = 'checking'
  healthMessageKey.value = 'home.healthChecking'

  try {
    const result = await getHealth()
    healthStatus.value = 'ok'
    healthMessageKey.value = result?.status === 'ok' ? 'home.healthOk' : 'home.healthResponded'
  } catch (error) {
    healthStatus.value = 'error'
    healthMessageKey.value = 'home.healthDown'
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
