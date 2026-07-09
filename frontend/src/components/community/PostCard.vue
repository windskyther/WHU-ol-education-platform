<template>
  <article class="community-card">
    <template v-if="!editing">
      <div class="card-head">
        <h3>{{ post.title }}</h3>
        <div v-if="post.is_mine" class="table-actions">
          <el-button text :icon="Edit" @click="startEdit">编辑</el-button>
          <el-button text type="danger" :icon="Delete" :loading="deleting" @click="handleDelete">删除</el-button>
        </div>
      </div>
      <p class="card-content">{{ post.content }}</p>

      <div v-if="post.attachments?.length" class="attachment-list">
        <a v-for="attachment in post.attachments" :key="attachment.id" :href="attachment.url" target="_blank" rel="noopener" class="attachment-chip">
          📎 {{ attachment.original_name }}
        </a>
      </div>

      <div class="card-meta">
        <span>{{ post.author?.username || '用户' }}</span>
        <span>{{ formatTime(post.created_at) }}</span>
      </div>

      <div class="card-actions">
        <el-button :type="post.is_liked ? 'primary' : 'default'" plain :icon="Star" :loading="liking" @click="handleLike">
          点赞 {{ post.likes_count }}
        </el-button>
        <el-button :type="post.is_favorited ? 'primary' : 'default'" plain :icon="Collection" :loading="favoriting" @click="handleFavorite">
          收藏 {{ post.favorites_count }}
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
      <el-input v-model.trim="editForm.title" maxlength="128" show-word-limit placeholder="帖子标题" />
      <el-input v-model.trim="editForm.content" type="textarea" :rows="4" maxlength="4000" show-word-limit placeholder="帖子内容" />
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
import { deletePost, toggleFavorite, toggleLike, updatePost } from '../../api/community'
import { getCommonErrorMessage } from '../../utils/errorMessage'

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
    ElMessage.error(getCommonErrorMessage(error, '点赞失败'))
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
    ElMessage.error(getCommonErrorMessage(error, '收藏失败'))
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
    ElMessage.warning('请填写标题和内容')
    return
  }
  saving.value = true
  try {
    const updated = await updatePost(props.post.id, { title: editForm.title, content: editForm.content })
    emit('updated', updated)
    ElMessage.success('帖子已更新')
    editing.value = false
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '帖子更新失败'))
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除这条帖子吗？', '删除帖子', { type: 'warning' })
  } catch {
    return
  }
  deleting.value = true
  try {
    await deletePost(props.post.id)
    ElMessage.success('帖子已删除')
    emit('deleted', props.post.id)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '帖子删除失败'))
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

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
