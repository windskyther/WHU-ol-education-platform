<template>
  <main class="auth-page">
    <LearningPathPanel
      title="Start with one verified identity."
      description="选择学生或教师身份，平台会开放对应的学习与课程管理入口。角色清晰，协作更顺畅。"
    />

    <section class="auth-card" aria-label="注册表单">
      <div class="auth-card__header">
        <RouterLink class="back-link" to="/">Back home</RouterLink>
        <p class="eyebrow">Create account</p>
        <h2>Register</h2>
        <p>邮箱验证码用于确认账号归属。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item label="用户名" prop="username">
          <el-input v-model.trim="form.username" size="large" placeholder="请输入用户名" autocomplete="username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model.trim="form.email" size="large" placeholder="name@example.com" autocomplete="email" />
        </el-form-item>
        <el-form-item label="验证码" prop="email_code">
          <div class="code-row">
            <el-input v-model.trim="form.email_code" size="large" placeholder="6 位验证码" />
            <el-button size="large" :disabled="codeDisabled" :loading="sendingCode" @click="handleSendCode">
              {{ codeButtonText }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-segmented v-model="form.role" :options="roleOptions" block />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" size="large" type="password" placeholder="至少 6 位" autocomplete="new-password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            size="large"
            type="password"
            placeholder="再次输入密码"
            autocomplete="new-password"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <el-button class="auth-submit" type="primary" size="large" :loading="submitting" @click="handleRegister">
          创建账号
        </el-button>
      </el-form>

      <p class="auth-switch">已有账号？<RouterLink to="/login">去登录</RouterLink></p>
    </section>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import LearningPathPanel from '../../components/LearningPathPanel.vue'
import { sendEmailCode } from '../../api/auth'
import { useUserStore } from '../../stores/user'
import { getEmailCodeErrorMessage, getRegisterErrorMessage } from '../../utils/errorMessage'

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

const roleOptions = [
  { label: '学生', value: 'student' },
  { label: '教师', value: 'teacher' }
]

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效邮箱', trigger: ['blur', 'change'] }
  ],
  email_code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const codeDisabled = computed(() => countdown.value > 0)
const codeButtonText = computed(() => (countdown.value > 0 ? `${countdown.value}s 后重发` : '发送验证码'))

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
    ElMessage.success('验证码已发送')
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
    ElMessage.success('注册成功，请登录')
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
