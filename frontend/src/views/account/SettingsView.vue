<template>
  <main class="page-shell settings-page">
    <AppNav />

    <BreadcrumbNav :items="[{ label: t('settings.breadcrumb') }]" />

    <section class="settings-workspace">
      <header class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">{{ t('settings.pageEyebrow') }}</p>
          <h1>{{ t('settings.pageTitle') }}</h1>
          <p>{{ t('settings.pageDesc') }}</p>
        </div>
      </header>

      <section class="surface settings-capsule-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('settings.capsuleEyebrow') }}</p>
            <h2>{{ t('settings.capsuleHeading') }}</h2>
          </div>
        </div>
        <div class="settings-capsule-row">
          <UserCapsule :user-info="previewUser" preview :interactive="false" />
          <div class="settings-capsule-copy">
            <strong>{{ t('settings.currentStatus', { label: currentMood.label, emoji: currentMood.emoji }) }}</strong>
            <p>{{ t('settings.capsuleHint') }}</p>
            <input ref="avatarInputRef" class="hidden-file-input" type="file" accept=".jpg,.jpeg,.png,.webp" @change="handleAvatarChange" />
            <el-button plain :loading="avatarUploading" @click="avatarInputRef?.click()">{{ t('settings.changeAvatar') }}</el-button>
            <span class="settings-hint">{{ t('settings.avatarHint') }}</span>
          </div>
        </div>
      </section>

      <section class="surface settings-form-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('settings.profileEyebrow') }}</p>
            <h2>{{ t('settings.profileHeading') }}</h2>
          </div>
        </div>
        <el-form label-position="top" class="settings-form">
          <el-form-item :label="t('settings.usernameLabel')">
            <el-input v-model.trim="profileForm.username" maxlength="64" />
          </el-form-item>
          <el-form-item :label="t('settings.emailLabel')">
            <div class="readonly-field">{{ userStore.userInfo?.email || '-' }}</div>
          </el-form-item>
          <el-form-item :label="t('settings.roleLabel')">
            <span class="status-pill">{{ roleLabel }}</span>
          </el-form-item>
          <el-form-item :label="t('settings.bioLabel')">
            <el-input v-model="profileForm.bio" type="textarea" :rows="4" maxlength="500" show-word-limit />
          </el-form-item>
          <el-button type="primary" :loading="profileSaving" @click="saveProfile">{{ t('settings.saveProfile') }}</el-button>
        </el-form>
      </section>

      <section class="surface settings-form-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('settings.moodEyebrow') }}</p>
            <h2>{{ t('settings.moodHeading') }}</h2>
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
          <el-button type="primary" :loading="moodSaving" @click="saveMood">{{ t('settings.saveMood') }}</el-button>
        </div>
      </section>

      <section class="surface settings-form-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{{ t('settings.securityEyebrow') }}</p>
            <h2>{{ t('settings.securityHeading') }}</h2>
          </div>
        </div>
        <el-form label-position="top" class="settings-form">
          <el-form-item :label="t('settings.oldPasswordLabel')">
            <el-input v-model="passwordForm.old_password" type="password" show-password />
          </el-form-item>
          <el-form-item :label="t('settings.newPasswordLabel')">
            <el-input v-model="passwordForm.new_password" type="password" show-password />
          </el-form-item>
          <el-form-item :label="t('settings.confirmNewPasswordLabel')">
            <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
          </el-form-item>
          <el-button type="primary" :loading="passwordSaving" @click="savePassword">{{ t('settings.updatePassword') }}</el-button>
        </el-form>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import AppNav from '../../components/AppNav.vue'
import BreadcrumbNav from '../../components/BreadcrumbNav.vue'
import UserCapsule from '../../components/UserCapsule.vue'
import { MOOD_OPTIONS, getMoodDisplay } from '../../constants/userMood'
import { useUserStore } from '../../stores/user'
import { getCommonErrorMessage, getPasswordErrorMessage, getProfileErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()
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

const roleLabel = computed(() => {
  const map = {
    student: t('settings.roleStudent'),
    teacher: t('settings.roleTeacher'),
    admin: t('settings.roleAdmin')
  }
  return map[userStore.role] || t('settings.roleUser')
})
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
    ElMessage.warning(t('settings.avatarTypeError'))
    return false
  }
  if (file.size > avatarMaxSizeMb * 1024 * 1024) {
    ElMessage.warning(t('settings.avatarSizeError'))
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
    ElMessage.success(t('settings.avatarUpdated'))
  } catch (error) {
    ElMessage.error(getProfileErrorMessage(error, t('settings.avatarUploadError')))
  } finally {
    avatarUploading.value = false
  }
}

async function saveProfile() {
  if (!profileForm.username.trim()) {
    ElMessage.warning(t('settings.usernameRequired'))
    return
  }

  profileSaving.value = true
  try {
    await userStore.updateProfile({
      username: profileForm.username.trim(),
      bio: profileForm.bio
    })
    ElMessage.success(t('settings.profileSaved'))
  } catch (error) {
    ElMessage.error(getProfileErrorMessage(error, t('settings.profileSaveError')))
  } finally {
    profileSaving.value = false
  }
}

async function saveMood() {
  moodSaving.value = true
  try {
    await userStore.updateProfile({ mood: selectedMood.value })
    ElMessage.success(t('settings.moodSaved'))
  } catch (error) {
    ElMessage.error(getProfileErrorMessage(error, t('settings.moodSaveError')))
  } finally {
    moodSaving.value = false
  }
}

async function savePassword() {
  if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirmPassword) {
    ElMessage.warning(t('settings.passwordIncomplete'))
    return
  }
  if (passwordForm.new_password !== passwordForm.confirmPassword) {
    ElMessage.warning(t('settings.passwordMismatch'))
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
    ElMessage.success(t('settings.passwordUpdated'))
  } catch (error) {
    ElMessage.error(getPasswordErrorMessage(error, t('settings.passwordUpdateError')))
  } finally {
    passwordSaving.value = false
  }
}

onMounted(async () => {
  if (!userStore.userInfo) {
    try {
      await userStore.fetchCurrentUser()
    } catch (error) {
      ElMessage.error(getCommonErrorMessage(error, t('settings.loadUserError')))
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
