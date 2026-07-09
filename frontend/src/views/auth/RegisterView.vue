<template>
  <main class="auth-page">
    <LearningPathPanel
      :title="t('auth.identityFlowTitle')"
      :description="t('auth.identityFlowDesc')"
    />

    <section class="auth-card" aria-label="注册表单">
      <div class="auth-card__header">
        <RouterLink class="back-link" to="/">{{ t('auth.backHome') }}</RouterLink>
        <p class="eyebrow">{{ t('auth.registerEyebrow') }}</p>
        <h2>{{ t('auth.registerTitle') }}</h2>
        <p>{{ t('auth.registerSubtitle') }}</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item :label="t('auth.usernameLabel')" prop="username">
          <el-input v-model.trim="form.username" size="large" :placeholder="t('auth.usernamePlaceholder')" autocomplete="username" />
        </el-form-item>
        <el-form-item :label="t('auth.emailLabel')" prop="email">
          <el-input v-model.trim="form.email" size="large" placeholder="name@example.com" autocomplete="email" />
        </el-form-item>
        <el-form-item :label="t('auth.codeLabel')" prop="email_code">
          <div class="code-row">
            <el-input v-model.trim="form.email_code" size="large" :placeholder="t('auth.codePlaceholder')" />
            <el-button size="large" :disabled="codeDisabled" :loading="sendingCode" @click="handleSendCode">
              {{ codeButtonText }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item :label="t('auth.roleLabel')" prop="role">
          <el-segmented v-model="form.role" :options="roleOptions" block />
        </el-form-item>
        <el-form-item :label="t('auth.passwordLabel')" prop="password">
          <el-input v-model="form.password" size="large" type="password" :placeholder="t('auth.passwordMinPlaceholder')" autocomplete="new-password" show-password />
        </el-form-item>
        <el-form-item :label="t('auth.confirmPasswordLabel')" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            size="large"
            type="password"
            :placeholder="t('auth.confirmPasswordPlaceholder')"
            autocomplete="new-password"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <el-button class="auth-submit" type="primary" size="large" :loading="submitting" @click="handleRegister">
          {{ t('auth.submitCreateAccount') }}
        </el-button>
      </el-form>

      <p class="auth-switch">{{ t('auth.alreadyHaveAccount') }}<RouterLink to="/login">{{ t('auth.goLogin') }}</RouterLink></p>
    </section>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import LearningPathPanel from '../../components/LearningPathPanel.vue'
import { sendEmailCode } from '../../api/auth'
import { useUserStore } from '../../stores/user'
import { getEmailCodeErrorMessage, getRegisterErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const submitting = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
let timer = null

const form = reactive({
  username: '',
  email: '',
  email_code: '',
  role: 'student',
  password: '',
  confirmPassword: ''
})

const roleOptions = computed(() => [
  { label: t('auth.roleStudent'), value: 'student' },
  { label: t('auth.roleTeacher'), value: 'teacher' }
])

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error(t('auth.passwordMismatch')))
    return
  }
  callback()
}

const rules = computed(() => ({
  username: [{ required: true, message: t('auth.usernameRequired'), trigger: 'blur' }],
  email: [
    { required: true, message: t('auth.emailRequired'), trigger: 'blur' },
    { type: 'email', message: t('auth.emailInvalid'), trigger: ['blur', 'change'] }
  ],
  email_code: [{ required: true, message: t('auth.codeRequired'), trigger: 'blur' }],
  role: [{ required: true, message: t('auth.roleRequired'), trigger: 'change' }],
  password: [
    { required: true, message: t('auth.passwordRequired'), trigger: 'blur' },
    { min: 6, message: t('auth.passwordMin6'), trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: t('auth.confirmPasswordRequired'), trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}))

const codeDisabled = computed(() => countdown.value > 0)
const codeButtonText = computed(() => (countdown.value > 0 ? t('auth.resendCountdown', { n: countdown.value }) : t('auth.sendCode')))

function startCountdown() {
  countdown.value = 60
  timer = window.setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0 && timer) {
      window.clearInterval(timer)
      timer = null
    }
  }, 1000)
}

async function handleSendCode() {
  await formRef.value.validateField('email')
  sendingCode.value = true

  try {
    await sendEmailCode({ registerEmail: form.email, purpose: 'register' })
    ElMessage.success(t('auth.codeSent'))
    startCountdown()
  } catch (error) {
    ElMessage.error(getEmailCodeErrorMessage(error))
  } finally {
    sendingCode.value = false
  }
}

async function handleRegister() {
  await formRef.value.validate()
  submitting.value = true

  try {
    await userStore.registerUser({ ...form })
    ElMessage.success(t('auth.registerSuccess'))
    router.push('/login')
  } catch (error) {
    ElMessage.error(getRegisterErrorMessage(error))
  } finally {
    submitting.value = false
  }
}

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer)
  }
})
</script>

<style scoped>
.auth-page {
  display: grid;
  grid-template-columns: minmax(360px, 0.92fr) minmax(360px, 1.08fr);
  padding: 0;
}

.auth-card {
  align-self: center;
  width: min(600px, calc(100% - 48px));
  margin: 48px auto;
  padding: 42px;
}

.auth-card__header {
  margin-bottom: 28px;
}

.code-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px;
  gap: 12px;
  width: 100%;
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

  .code-row {
    grid-template-columns: 1fr;
  }

  .auth-card {
    width: calc(100% - 32px);
    padding: 30px;
  }
}
</style>
