<template>
  <section class="author-profile-page">
    <div v-loading="loading" class="surface profile-card">
      <template v-if="user">
        <el-avatar :size="88" :src="user.avatar_url || undefined" class="profile-avatar">
          {{ initials }}
        </el-avatar>
        <div class="profile-info">
          <h2>{{ user.username }}</h2>
          <span class="role-pill">{{ roleLabel }}</span>
          <p v-if="user.bio" class="bio">{{ user.bio }}</p>
          <p v-else class="bio muted">这位用户还没有填写个人简介。</p>
          <p class="joined">加入时间：{{ formatTime(user.date_joined) }}</p>
        </div>
      </template>
      <div v-else-if="!loading" class="empty-state">未找到该用户信息。</div>
    </div>

    <div class="table-actions back-row">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { fetchPublicUser } from '../../api/auth'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const user = ref(null)

const roleLabelMap = {
  student: '学生',
  teacher: '教师',
  admin: '管理员'
}

const roleLabel = computed(() => roleLabelMap[user.value?.role] || '用户')

const initials = computed(() => {
  const name = user.value?.username || ''
  return name ? name.trim().charAt(0).toUpperCase() : '?'
})

function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('zh-CN')
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/community/forum')
  }
}

async function loadUser() {
  loading.value = true
  try {
    user.value = await fetchPublicUser(route.params.id)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '加载用户信息失败'))
    user.value = null
  } finally {
    loading.value = false
  }
}

onMounted(loadUser)
</script>

<style scoped>
.author-profile-page {
  display: grid;
  gap: 16px;
  max-width: 560px;
  margin: 0 auto;
}

.profile-card {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  padding: 28px;
}

.profile-avatar {
  flex-shrink: 0;
  background: var(--acid);
  color: var(--ink);
  font-weight: 900;
  font-size: 32px;
  border: 2px solid var(--line);
}

.profile-info {
  display: grid;
  gap: 8px;
}

.profile-info h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 900;
}

.role-pill {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 4px 14px;
  color: var(--ink);
  background: var(--hot);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.04em;
}

.bio {
  margin: 4px 0 0;
  color: var(--ink);
  font-weight: 600;
  line-height: 1.6;
  white-space: pre-wrap;
}

.bio.muted {
  color: var(--muted);
  font-weight: 500;
}

.joined {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.back-row {
  justify-content: flex-start;
}
</style>
