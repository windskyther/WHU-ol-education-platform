<template>
  <article class="community-card">
    <template v-if="!editing">
      <div class="card-head">
        <h3>{{ post.title }}</h3>
        <div class="card-head-right">
          <div v-if="post.is_mine" class="table-actions">
            <el-button text :icon="Edit" @click="startEdit">{{ t('community.postCard.edit') }}</el-button>
            <el-button text type="danger" :icon="Delete" :loading="deleting" @click="handleDelete">{{ t('community.postCard.delete') }}</el-button>
          </div>
          <AuthorAvatar :author="post.author" />
        </div>
      </div>
      <p class="card-content">{{ post.content }}</p>

      <div v-if="post.attachments?.length" class="attachment-list">
        <template v-for="attachment in post.attachments" :key="attachment.id">
          <el-image
            v-if="attachment.is_image"
            class="attachment-image"
            :src="attachment.url"
            :preview-src-list="imageAttachmentUrls"
            :initial-index="imageAttachmentUrls.indexOf(attachment.url)"
            fit="cover"
            preview-teleported
          />
          <a v-else :href="attachment.url" target="_blank" rel="noopener" class="attachment-chip">
            📎 {{ attachment.original_name }}
          </a>
        </template>
      </div>

      <div class="card-meta">
        <span>{{ post.author?.username || t('community.postCard.unknownUser') }}</span>
        <span>{{ formatTime(post.created_at) }}</span>
      </div>

      <div class="card-actions">
        <el-button class="reaction-btn" :class="{ 'is-active': post.is_liked }" plain :loading="liking" @click="handleLike">
          <span class="reaction-icon">👍</span> {{ post.likes_count }}
        </el-button>
        <el-button class="reaction-btn" :class="{ 'is-active': post.is_favorited }" plain :icon="post.is_favorited ? StarFilled : Star" :loading="favoriting" @click="handleFavorite">
          {{ t('community.postCard.favoriteCount', { n: post.favorites_count }) }}
        </el-button>
      </div>

      <CommentSection
        target-type="post"
        :target-id="post.id"
        :comments-count="post.comments_count"
        @comment-added="post.comments_count += 1"
      />
    </template>

    <form v-else class="edit-form" @submit.prevent="submitEdit">
      <el-input v-model.trim="editForm.title" maxlength="128" show-word-limit :placeholder="t('community.postCard.titlePlaceholder')" />
      <el-input v-model.trim="editForm.content" type="textarea" :rows="4" maxlength="4000" show-word-limit :placeholder="t('community.postCard.contentPlaceholder')" />
      <div class="table-actions">
        <el-button type="primary" :loading="saving" @click="submitEdit">{{ t('community.postCard.save') }}</el-button>
        <el-button @click="cancelEdit">{{ t('community.postCard.cancel') }}</el-button>
      </div>
    </form>
  </article>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Delete, Edit, Star, StarFilled } from '@element-plus/icons-vue'
import CommentSection from './CommentSection.vue'
import AuthorAvatar from './AuthorAvatar.vue'
import { deletePost, toggleFavorite, toggleLike, updatePost } from '../../api/community'
import { getCommunityErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()

const props = defineProps({
  post: {
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
const editForm = reactive({ title: '', content: '' })

const imageAttachmentUrls = computed(() =>
  (props.post.attachments || []).filter((item) => item.is_image).map((item) => item.url)
)


function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

async function handleLike() {
  liking.value = true
  try {
    const data = await toggleLike('post', props.post.id)
    props.post.is_liked = data.liked
    props.post.likes_count = data.likes_count
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.postCard.likeFailed')))
  } finally {
    liking.value = false
  }
}

async function handleFavorite() {
  favoriting.value = true
  try {
    const data = await toggleFavorite('post', props.post.id)
    props.post.is_favorited = data.favorited
    props.post.favorites_count = data.favorites_count
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.postCard.favoriteFailed')))
  } finally {
    favoriting.value = false
  }
}

function startEdit() {
  editForm.title = props.post.title
  editForm.content = props.post.content
  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

async function submitEdit() {
  if (!editForm.title || !editForm.content) {
    ElMessage.warning(t('community.postCard.requiredFields'))
    return
  }
  saving.value = true
  try {
    const updated = await updatePost(props.post.id, { title: editForm.title, content: editForm.content })
    emit('updated', updated)
    ElMessage.success(t('community.postCard.updateSuccess'))
    editing.value = false
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.postCard.updateFailed')))
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm(t('community.postCard.deleteConfirm'), t('community.postCard.deleteTitle'), { type: 'warning' })
  } catch {
    return
  }
  deleting.value = true
  try {
    await deletePost(props.post.id)
    ElMessage.success(t('community.postCard.deleteSuccess'))
    emit('deleted', props.post.id)
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.postCard.deleteFailed')))
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

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.attachment-image {
  width: 96px;
  height: 96px;
  border-radius: 8px;
  overflow: hidden;
  cursor: zoom-in;
  border: 1px solid var(--line);
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
