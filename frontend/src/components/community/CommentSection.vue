<template>
  <div class="comment-section">
    <button type="button" class="comment-toggle" @click="toggleOpen">
      {{ open ? '收起评论' : `查看评论 (${commentsCount})` }}
    </button>

    <div v-if="open" class="comment-body">
      <div v-loading="loading" class="comment-list">
        <div v-for="comment in comments" :key="comment.id" class="comment-item">
          <strong>{{ comment.author?.username || '用户' }}</strong>
          <span>{{ comment.content }}</span>
          <small>{{ formatTime(comment.created_at) }}</small>
        </div>
        <p v-if="!loading && comments.length === 0" class="comment-empty">还没有评论，来说两句吧。</p>
      </div>

      <form class="comment-form" @submit.prevent="submitComment">
        <el-input v-model.trim="draft" maxlength="1000" show-word-limit placeholder="写下你的评论…" />
        <el-button type="primary" :loading="submitting" @click="submitComment">评论</el-button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createComment, fetchComments } from '../../api/community'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const props = defineProps({
  targetType: {
    type: String,
    required: true
  },
  targetId: {
    type: [String, Number],
    required: true
  },
  commentsCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['comment-added'])

const open = ref(false)
const loading = ref(false)
const submitting = ref(false)
const comments = ref([])
const draft = ref('')
const loaded = ref(false)

function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

async function loadComments() {
  loading.value = true
  try {
    const data = await fetchComments(props.targetType, props.targetId, { page_size: 50 })
    comments.value = data?.results || []
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '评论加载失败'))
  } finally {
    loading.value = false
    loaded.value = true
  }
}

function toggleOpen() {
  open.value = !open.value
  if (open.value && !loaded.value) {
    loadComments()
  }
}

async function submitComment() {
  if (!draft.value) {
    ElMessage.warning('请输入评论内容')
    return
  }
  submitting.value = true
  try {
    await createComment(props.targetType, props.targetId, draft.value)
    draft.value = ''
    await loadComments()
    emit('comment-added')
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '评论失败'))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.comment-section {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px dashed var(--line);
}

.comment-toggle {
  padding: 0;
  color: var(--muted);
  background: transparent;
  border: 0;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
}

.comment-toggle:hover {
  color: var(--ink);
}

.comment-body {
  display: grid;
  gap: 12px;
  margin-top: 12px;
}

.comment-list {
  display: grid;
  gap: 8px;
  min-height: 20px;
}

.comment-item {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(25, 25, 23, 0.04);
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.comment-item strong {
  color: var(--ink);
}

.comment-item span {
  color: var(--ink);
  font-weight: 600;
}

.comment-item small {
  margin-left: auto;
  color: var(--muted);
}

.comment-empty {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.comment-form {
  display: flex;
  gap: 10px;
}
</style>
