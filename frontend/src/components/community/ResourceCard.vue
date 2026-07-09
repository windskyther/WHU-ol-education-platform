<template>
  <article class="community-card">
    <template v-if="!editing">
      <div class="card-head">
        <h3>{{ resource.title }}</h3>
        <div v-if="resource.is_mine" class="table-actions">
          <el-button text :icon="Edit" @click="startEdit">编辑</el-button>
          <el-button text type="danger" :icon="Delete" :loading="deleting" @click="handleDelete">删除</el-button>
        </div>
      </div>
      <p v-if="resource.description" class="card-content">{{ resource.description }}</p>

      <div class="resource-link-row">
        <a v-if="resource.url" class="go-button" :href="resource.url" target="_blank" rel="noopener">
          GO
        </a>
        <a v-else-if="resource.file_url" class="attachment-chip" :href="resource.file_url" target="_blank" rel="noopener">
          📎 {{ resource.original_name || '下载资料' }}
        </a>
      </div>

      <div class="card-meta">
        <span>{{ resource.author?.username || '用户' }}</span>
        <span>{{ formatTime(resource.created_at) }}</span>
      </div>

      <div class="card-actions">
        <el-button :type="resource.is_liked ? 'primary' : 'default'" plain :icon="Star" :loading="liking" @click="handleLike">
          点赞 {{ resource.likes_count }}
        </el-button>
        <el-button :type="resource.is_favorited ? 'primary' : 'default'" plain :icon="Collection" :loading="favoriting" @click="handleFavorite">
          收藏 {{ resource.favorites_count }}
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
      <el-input v-model.trim="editForm.title" maxlength="128" show-word-limit placeholder="资料标题" />
      <el-input v-model.trim="editForm.description" type="textarea" :rows="3" maxlength="2000" show-word-limit placeholder="资料说明" />
      <el-input v-if="resource.url" v-model.trim="editForm.url" placeholder="资料网址" />
      <div class="table-actions">
        <el-button type="primary" :loading="saving" @click="submitEdit">保存</el-button>
        <el-button @click="cancelEdit">取消</el-button>
      </div>
    </form>
  </article>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Collection, Delete, Edit, Star } from '@element-plus/icons-vue'
import CommentSection from './CommentSection.vue'
import { deleteResource, toggleFavorite, toggleLike, updateResource } from '../../api/community'
import { getCommonErrorMessage } from '../../utils/errorMessage'

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
    ElMessage.error(getCommonErrorMessage(error, '点赞失败'))
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
    ElMessage.error(getCommonErrorMessage(error, '收藏失败'))
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
    ElMessage.warning('请填写资料标题')
    return
  }
  saving.value = true
  try {
    const updated = await updateResource(props.resource.id, {
      title: editForm.title,
      description: editForm.description,
      url: editForm.url
    })
    emit('updated', updated)
    ElMessage.success('资料已更新')
    editing.value = false
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '资料更新失败'))
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除这条资料吗？', '删除资料', { type: 'warning' })
  } catch {
    return
  }
  deleting.value = true
  try {
    await deleteResource(props.resource.id)
    ElMessage.success('资料已删除')
    emit('deleted', props.resource.id)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '资料删除失败'))
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

.edit-form {
  display: grid;
  gap: 10px;
}
</style>
