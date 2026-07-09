<template>
  <article class="community-card">
    <template v-if="!editing">
      <div class="card-head">
        <h3>{{ resource.title }}</h3>
        <div class="card-head-right">
          <div v-if="resource.is_mine" class="table-actions">
            <el-button text :icon="Edit" @click="startEdit">{{ t('community.resourceCard.edit') }}</el-button>
            <el-button text type="danger" :icon="Delete" :loading="deleting" @click="handleDelete">{{ t('community.resourceCard.delete') }}</el-button>
          </div>
          <AuthorAvatar :author="resource.author" />
        </div>
      </div>
      <p v-if="resource.description" class="card-content">{{ resource.description }}</p>

      <el-image
        v-if="resource.file_url && resource.is_image"
        class="resource-image"
        :src="resource.file_url"
        :preview-src-list="[resource.file_url]"
        fit="cover"
        preview-teleported
      />

      <div class="resource-link-row">
        <a v-if="resource.url" class="go-button" :href="resource.url" target="_blank" rel="noopener">
          GO
        </a>
        <a v-else-if="resource.file_url && !resource.is_image" class="attachment-chip" :href="resource.file_url" target="_blank" rel="noopener">
          📎 {{ resource.original_name || t('community.resourceCard.downloadLabel') }}
        </a>
      </div>

      <div class="card-meta">
        <span>{{ resource.author?.username || t('community.resourceCard.unknownUser') }}</span>
        <span>{{ formatTime(resource.created_at) }}</span>
      </div>

      <div class="card-actions">
        <el-button class="reaction-btn" :class="{ 'is-active': resource.is_liked }" plain :loading="liking" @click="handleLike">
          <span class="reaction-icon">👍</span> {{ resource.likes_count }}
        </el-button>
        <el-button class="reaction-btn" :class="{ 'is-active': resource.is_favorited }" plain :icon="resource.is_favorited ? StarFilled : Star" :loading="favoriting" @click="handleFavorite">
          {{ t('community.resourceCard.favoriteCount', { n: resource.favorites_count }) }}
        </el-button>
      </div>

      <CommentSection
        target-type="resource"
        :target-id="resource.id"
        :comments-count="resource.comments_count"
        @comment-added="resource.comments_count += 1"
      />
    </template>

    <form v-else class="edit-form" @submit.prevent="submitEdit">
      <el-input v-model.trim="editForm.title" maxlength="128" show-word-limit :placeholder="t('community.resourceCard.titlePlaceholder')" />
      <el-input v-model.trim="editForm.description" type="textarea" :rows="3" maxlength="2000" show-word-limit :placeholder="t('community.resourceCard.descPlaceholder')" />
      <el-input v-if="resource.url" v-model.trim="editForm.url" :placeholder="t('community.resourceCard.urlPlaceholder')" />
      <div class="table-actions">
        <el-button type="primary" :loading="saving" @click="submitEdit">{{ t('community.resourceCard.save') }}</el-button>
        <el-button @click="cancelEdit">{{ t('community.resourceCard.cancel') }}</el-button>
      </div>
    </form>
  </article>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Delete, Edit, Star, StarFilled } from '@element-plus/icons-vue'
import CommentSection from './CommentSection.vue'
import AuthorAvatar from './AuthorAvatar.vue'
import { deleteResource, toggleFavorite, toggleLike, updateResource } from '../../api/community'
import { getCommunityErrorMessage } from '../../utils/errorMessage'
import { normalizeUrl } from '../../utils/url'

const { t } = useI18n()

const props = defineProps({
  resource: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['deleted', 'updated'])

const liking = ref(false)
const favoriting = ref(false)
const deleting = ref(false)
const editing = ref(false)
const saving = ref(false)
const editForm = reactive({ title: '', description: '', url: '' })

function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

async function handleLike() {
  liking.value = true
  try {
    const data = await toggleLike('resource', props.resource.id)
    props.resource.is_liked = data.liked
    props.resource.likes_count = data.likes_count
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.resourceCard.likeFailed')))
  } finally {
    liking.value = false
  }
}

async function handleFavorite() {
  favoriting.value = true
  try {
    const data = await toggleFavorite('resource', props.resource.id)
    props.resource.is_favorited = data.favorited
    props.resource.favorites_count = data.favorites_count
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.resourceCard.favoriteFailed')))
  } finally {
    favoriting.value = false
  }
}

function startEdit() {
  editForm.title = props.resource.title
  editForm.description = props.resource.description
  editForm.url = props.resource.url
  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

async function submitEdit() {
  if (!editForm.title) {
    ElMessage.warning(t('community.resourceCard.titleRequired'))
    return
  }
  saving.value = true
  try {
    const updated = await updateResource(props.resource.id, {
      title: editForm.title,
      description: editForm.description,
      url: editForm.url ? normalizeUrl(editForm.url) : ''
    })
    emit('updated', updated)
    ElMessage.success(t('community.resourceCard.updateSuccess'))
    editing.value = false
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.resourceCard.updateFailed')))
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm(t('community.resourceCard.deleteConfirm'), t('community.resourceCard.deleteTitle'), { type: 'warning' })
  } catch {
    return
  }
  deleting.value = true
  try {
    await deleteResource(props.resource.id)
    ElMessage.success(t('community.resourceCard.deleteSuccess'))
    emit('deleted', props.resource.id)
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.resourceCard.deleteFailed')))
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.community-card {
  display: grid;
  gap: 14px;
  padding: 20px;
  background: rgba(255, 250, 240, 0.82);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.card-head-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.card-head h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
  letter-spacing: -0.02em;
}

.card-content {
  margin: 0;
  color: var(--ink);
  font-weight: 600;
  line-height: 1.5;
  white-space: pre-wrap;
}

.resource-image {
  width: 100%;
  max-height: 220px;
  border-radius: 8px;
  overflow: hidden;
  cursor: zoom-in;
  border: 1px solid var(--line);
}

.resource-link-row {
  display: flex;
}

.go-button {
  display: inline-flex;
  align-items: center;
  padding: 8px 22px;
  color: var(--ink);
  background: var(--acid);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.06em;
}

.attachment-chip {
  padding: 6px 12px;
  color: var(--ink);
  background: rgba(45, 140, 202, 0.12);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
}

.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.reaction-btn {
  font-size: 14px;
}

.reaction-btn.is-active {
  color: var(--el-color-warning);
  border-color: var(--el-color-warning);
  background-color: var(--el-color-warning-light-9);
}

.reaction-icon {
  font-size: 14px;
  line-height: 1;
}

.edit-form {
  display: grid;
  gap: 10px;
}
</style>
