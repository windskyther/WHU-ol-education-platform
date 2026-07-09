<template>
  <main class="auth-page">
    <LearningPathPanel :title="t('auth.learningFlowTitle')" />

    <section class="auth-card" aria-label="登录表单">
      <div class="auth-card__header">
        <RouterLink class="back-link" to="/">{{ t('auth.backHome') }}</RouterLink>
        <p class="eyebrow">{{ t('auth.secureAccess') }}</p>
        <h2>{{ t('auth.loginTitle') }}</h2>
        <p>{{ t('auth.loginSubtitle') }}</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item :label="t('auth.accountLabel')" prop="account">
          <el-input v-model.trim="form.account" size="large" :placeholder="t('auth.accountPlaceholder')" autocomplete="username" />
        </el-form-item>
        <el-form-item :label="t('auth.passwordLabel')" prop="password">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            :placeholder="t('auth.passwordPlaceholder')"
            autocomplete="current-password"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button class="auth-submit" type="primary" size="large" :loading="submitting" @click="handleLogin">
          {{ t('auth.loginSubmit') }}
        </el-button>
      </el-form>

      <p class="auth-switch">{{ t('auth.noAccount') }}<RouterLink to="/register">{{ t('auth.createAccount') }}</RouterLink></p>
    </section>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import LearningPathPanel from '../../components/LearningPathPanel.vue'
import { useUserStore } from '../../stores/user'
import { getLoginErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const submitting = ref(false)

const form = reactive({
  account: '',
  password: ''
})

const rules = computed(() => ({
  account: [{ required: true, message: t('auth.accountRequired'), trigger: 'blur' }],
  password: [{ required: true, message: t('auth.passwordRequired'), trigger: 'blur' }]
}))

async function handleLogin() {
  await formRef.value.validate()
  submitting.value = true

  try {
    const nextPath = await userStore.loginUser(form)
    ElMessage.success(t('auth.loginSuccess'))
    router.push(route.query.redirect || nextPath)
  } catch (error) {
    ElMessage.error(getLoginErrorMessage(error))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(360px, 0.92fr) minmax(360px, 1.08fr);
  padding: 0;
}

.auth-card {
  align-self: center;
  width: min(560px, calc(100% - 48px));
  margin: 48px auto;
  padding: 42px;
}

.auth-card__header {
  margin-bottom: 28px;
}

.auth-card__header h2 {
  margin-top: 12px;
}

.auth-submit {
  width: 100%;
  margin-top: 8px;
}

.auth-switch {
  margin: 24px 0 0;
  color: var(--muted);
  font-weight: 900;
  text-align: center;
}

.auth-switch a {
  border-bottom: 2px solid currentColor;
}

@media (max-width: 900px) {
  .auth-page {
    grid-template-columns: 1fr;
  }

  .auth-card {
    width: calc(100% - 32px);
    padding: 30px;
  }
}
</style>
