<template>
  <main class="auth-page">
    <LearningPathPanel
      title="回到你的学习节奏。"
      description="登录后会根据身份进入对应工作区。学生继续学习，教师维护课程，每一次进入都更接近完成。"
    />

    <section class="auth-card" aria-label="登录表单">
      <div class="auth-card__header">
        <RouterLink class="back-link" to="/">返回首页</RouterLink>
        <p class="eyebrow">安全登录</p>
        <h2>登录</h2>
        <p>使用用户名或邮箱进入 WHU 在线教育平台。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item label="账号" prop="account">
          <el-input v-model.trim="form.account" size="large" placeholder="用户名或邮箱" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button class="auth-submit" type="primary" size="large" :loading="submitting" @click="handleLogin">
          登录并进入平台
        </el-button>
      </el-form>

      <p class="auth-switch">还没有账号？<RouterLink to="/register">创建账号</RouterLink></p>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { ElMessage } from 'element-plus'
import LearningPathPanel from '../../components/LearningPathPanel.vue'
import { useUserStore } from '../../stores/user'
import { getLoginErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const submitting = ref(false)

const form = reactive({
  account: '',
  password: ''
})

const rules = {
  account: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  await formRef.value.validate()
  submitting.value = true

  try {
    const nextPath = await userStore.loginUser(form)
    ElMessage.success('登录成功')
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
