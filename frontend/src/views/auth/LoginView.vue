<template>
  <main class="auth-page">
    <LearningPathPanel title="从一个清晰入口开始学习" description="登录后会根据你的角色进入对应工作台，后续课程、考试和论坛都会从这里展开。" />

    <section class="auth-card" aria-label="登录表单">
      <div class="auth-card__header">
        <RouterLink class="back-link" to="/">返回首页</RouterLink>
        <h2>登录</h2>
        <p>使用用户名或邮箱登录在线教育平台。</p>
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
    ElMessage.error(error.message || '登录失败，请检查账号和密码')
  } finally {
    submitting.value = false
  }
}
</script>
