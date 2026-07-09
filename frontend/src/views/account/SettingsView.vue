<template>
  <main class="page-shell settings-page">
    <AppNav />

    <BreadcrumbNav :items="[{ label: '个人设置' }]" />

    <section class="settings-workspace">
      <header class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">账号设置</p>
          <h1>个人设置</h1>
          <p>管理头像、资料、情绪状态和登录密码。Nav 右上角胶囊会实时反映你的展示状态。</p>
        </div>
      </header>

      <section class="surface settings-capsule-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">个人胶囊</p>
            <h2>展示预览</h2>
          </div>
        </div>
        <div class="settings-capsule-row">
          <UserCapsule :user-info="previewUser" preview :interactive="false" />
          <div class="settings-capsule-copy">
            <strong>当前状态：{{ currentMood.label }} {{ currentMood.emoji }}</strong>
            <p>这是你在导航栏里看到的胶囊样式。</p>
            <input ref="avatarInputRef" class="hidden-file-input" type="file" accept=".jpg,.jpeg,.png,.webp" @change="handleAvatarChange" />
            <el-button plain :loading="avatarUploading" @click="avatarInputRef?.click()">更换头像</el-button>
            <span class="settings-hint">支持 jpg / png / webp，最大 5 MB</span>
          </div>
        </div>
      </section>

      <section class="surface settings-form-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">基础资料</p>
            <h2>基本资料</h2>
          </div>
        </div>
        <el-form label-position="top" class="settings-form">
          <el-form-item label="用户名">
            <el-input v-model.trim="profileForm.username" maxlength="64" />
          </el-form-item>
          <el-form-item label="邮箱">
            <div class="readonly-field">{{ userStore.userInfo?.email || '-' }}</div>
          </el-form-item>
          <el-form-item label="角色">
            <span class="status-pill">{{ roleLabel }}</span>
          </el-form-item>
          <el-form-item label="个人简介">
            <el-input v-model="profileForm.bio" type="textarea" :rows="4" maxlength="500" show-word-limit />
          </el-form-item>
          <el-button type="primary" :loading="profileSaving" @click="saveProfile">保存资料</el-button>
        </el-form>
      </section>

      <section class="surface settings-form-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">心情状态</p>
            <h2>情绪状态</h2>
          </div>
        </div>
        <div class="mood-capsule-grid">
          <button
            v-for="option in MOOD_OPTIONS"
            :key="option.key"
            type="button"
            class="mood-capsule"
            :class="{ 'is-active': selectedMood === option.key }"
            @click="selectedMood = option.key"
          >
            <span>{{ option.emoji }}</span>
            <span>{{ option.label }}</span>
          </button>
        </div>
        <div class="settings-form-actions">
          <el-button type="primary" :loading="moodSaving" @click="saveMood">保存状态</el-button>
        </div>
      </section>

      <section class="surface settings-form-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">安全设置</p>
            <h2>修改密码</h2>
          </div>
        </div>
        <el-form label-position="top" class="settings-form">
          <el-form-item label="当前密码">
            <el-input v-model="passwordForm.old_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="passwordForm.new_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认新密码">
            <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
          </el-form-item>
          <el-button type="primary" :loading="passwordSaving" @click="savePassword">更新密码</el-button>
        </el-form>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import AppNav from '../../components/AppNav.vue'
import BreadcrumbNav from '../../components/BreadcrumbNav.vue'
import UserCapsule from '../../components/UserCapsule.vue'
import { MOOD_OPTIONS, getMoodDisplay } from '../../constants/userMood'
import { useUserStore } from '../../stores/user'
import { getCommonErrorMessage, getPasswordErrorMessage, getProfileErrorMessage } from '../../utils/errorMessage'

const userStore = useUserStore()
const avatarInputRef = ref(null)
const avatarUploading = ref(false)
const profileSaving = ref(false)
const moodSaving = ref(false)
const passwordSaving = ref(false)
const selectedMood = ref(userStore.mood)

const profileForm = reactive({
  username: '',
  bio: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirmPassword: ''
})

const roleLabelMap = {
  student: '学生',
  teacher: '教师',
  admin: '管理员'
}

const roleLabel = computed(() => roleLabelMap[userStore.role] || '用户')
const currentMood = computed(() => getMoodDisplay(selectedMood.value))
const previewUser = computed(() => ({
  ...userStore.userInfo,
  username: profileForm.username || userStore.userInfo?.username,
  mood: selectedMood.value
}))

const avatarAllowedExtensions = ['.jpg', '.jpeg', '.png', '.webp']
const avatarMaxSizeMb = 5

function syncProfileForm() {
  profileForm.username = userStore.userInfo?.username || ''
  profileForm.bio = userStore.userInfo?.bio || ''
  selectedMood.value = userStore.mood
}

watch(
  () => userStore.userInfo,
  () => syncProfileForm(),
  { deep: true }
)

function validateAvatarFile(file) {
  const extension = `.${file.name.split('.').pop()?.toLowerCase() || ''}`
  if (!avatarAllowedExtensions.includes(extension)) {
    ElMessage.warning('头像仅支持 jpg、jpeg、png、webp')
    return false
  }
  if (file.size > avatarMaxSizeMb * 1024 * 1024) {
    ElMessage.warning('头像大小不能超过 5 MB')
    return false
  }
  return true
}

async function handleAvatarChange(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file || !validateAvatarFile(file)) return

  avatarUploading.value = true
  try {
    const formData = new FormData()
    formData.append('avatar', file)
    await userStore.updateProfile(formData)
    ElMessage.success('头像已更新')
  } catch (error) {
    ElMessage.error(getProfileErrorMessage(error, '头像上传失败，请稍后重试'))
  } finally {
    avatarUploading.value = false
  }
}

async function saveProfile() {
  if (!profileForm.username.trim()) {
    ElMessage.warning('用户名不能为空')
    return
  }

  profileSaving.value = true
  try {
    await userStore.updateProfile({
      username: profileForm.username.trim(),
      bio: profileForm.bio
    })
    ElMessage.success('资料已保存')
  } catch (error) {
    ElMessage.error(getProfileErrorMessage(error, '资料保存失败，请稍后重试'))
  } finally {
    profileSaving.value = false
  }
}

async function saveMood() {
  moodSaving.value = true
  try {
    await userStore.updateProfile({ mood: selectedMood.value })
    ElMessage.success('状态已保存')
  } catch (error) {
    ElMessage.error(getProfileErrorMessage(error, '状态保存失败，请稍后重试'))
  } finally {
    moodSaving.value = false
  }
}

async function savePassword() {
  if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirmPassword) {
    ElMessage.warning('请完整填写密码信息')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  passwordSaving.value = true
  try {
    await userStore.changeUserPassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
      new_password_confirm: passwordForm.confirmPassword
    })
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirmPassword = ''
    ElMessage.success('密码已更新')
  } catch (error) {
    ElMessage.error(getPasswordErrorMessage(error, '密码更新失败，请稍后重试'))
  } finally {
    passwordSaving.value = false
  }
}

onMounted(async () => {
  if (!userStore.userInfo) {
    try {
      await userStore.fetchCurrentUser()
    } catch (error) {
      ElMessage.error(getCommonErrorMessage(error, '加载用户信息失败'))
    }
  }
  syncProfileForm()
})
</script>

<style scoped>
.settings-workspace {
  display: grid;
  gap: 22px;
  margin-top: 28px;
}

.settings-capsule-panel,
.settings-form-panel {
  padding: 24px;
}

.settings-capsule-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 24px;
}

.settings-capsule-copy {
  display: grid;
  gap: 10px;
  max-width: 420px;
}

.settings-capsule-copy strong {
  font-size: 16px;
  font-weight: 900;
}

.settings-capsule-copy p,
.settings-hint {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
  font-weight: 700;
}

.settings-form {
  max-width: 560px;
}

.settings-form-actions {
  margin-top: 16px;
}

.readonly-field {
  min-height: 38px;
  padding: 8px 12px;
  color: var(--muted);
  background: rgba(25, 25, 23, 0.04);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
  font-weight: 700;
}

.hidden-file-input {
  display: none;
}
</style>
