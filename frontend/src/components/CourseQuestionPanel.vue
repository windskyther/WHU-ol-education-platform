<template>
  <section class="surface question-panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">课程问答</p>
        <h2>{{ heading }}</h2>
      </div>
      <div class="question-toolbar">
        <el-select v-if="canManage" v-model="filters.status" clearable placeholder="状态" @change="loadQuestions(1)">
          <el-option label="待回答" value="open" />
          <el-option label="已回答" value="answered" />
          <el-option label="已解决" value="resolved" />
        </el-select>
        <el-button :icon="Refresh" :loading="loading" @click="loadQuestions(page)">刷新</el-button>
      </div>
    </div>

    <div v-if="!canUseQuestions" class="locked-panel">
      <strong>加入课程后参与问答</strong>
      <p>课程问答只对已选课学生、课程教师和管理员开放。</p>
    </div>

    <template v-else>
      <el-form v-if="canAsk" class="question-form" label-position="top" @submit.prevent>
        <el-form-item label="问题标题">
          <el-input v-model.trim="questionForm.title" maxlength="128" show-word-limit placeholder="例如：第二章矩阵秩怎么理解？" />
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input v-model.trim="questionForm.content" type="textarea" :rows="4" maxlength="2000" show-word-limit placeholder="描述你卡住的步骤、章节或报错信息。" />
        </el-form-item>
        <div class="table-actions">
          <el-button type="primary" :icon="ChatDotSquare" :loading="submittingQuestion" @click="submitQuestion">提交问题</el-button>
        </div>
      </el-form>

      <div v-loading="loading" class="question-list">
        <article v-for="question in questions" :key="question.id" class="question-card">
          <div class="question-main">
            <div class="question-title-row">
              <h3>{{ question.title }}</h3>
              <el-tag :type="statusTagType(question.status)" effect="light">{{ statusText(question.status) }}</el-tag>
            </div>
            <p class="question-content">{{ question.content }}</p>
            <div class="question-meta">
              <span>{{ question.student?.username || '学生' }}</span>
              <span>{{ formatTime(question.created_at) }}</span>
            </div>
          </div>

          <div v-if="question.answer" class="answer-block">
            <div>
              <span>教师回复</span>
              <strong>{{ question.answer.teacher?.username || '教师' }}</strong>
            </div>
            <p>{{ question.answer.content }}</p>
            <small>{{ formatTime(question.answer.updated_at || question.answer.created_at) }}</small>
          </div>

          <el-form v-if="canManage" class="answer-form" @submit.prevent>
            <el-input v-model.trim="answerDrafts[question.id]" type="textarea" :rows="3" maxlength="2000" show-word-limit :placeholder="question.answer ? '更新回答内容' : '输入回答内容'" />
            <div class="table-actions">
              <el-button type="primary" :loading="answeringId === question.id" @click="submitAnswer(question)">回答</el-button>
              <el-button v-if="question.status !== 'resolved'" plain :icon="Check" :loading="resolvingId === question.id" @click="markResolved(question)">标记解决</el-button>
            </div>
          </el-form>

          <div v-else-if="canAsk && question.status !== 'resolved'" class="table-actions">
            <el-button plain :icon="Check" :loading="resolvingId === question.id" @click="markResolved(question)">我的问题已解决</el-button>
          </div>
        </article>
      </div>

      <div v-if="!loading && questions.length === 0" class="empty-state">
        {{ canAsk ? '还没有提问，遇到卡点时可以在这里记录。' : '暂无课程问题。' }}
      </div>

      <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadQuestions" />
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotSquare, Check, Refresh } from '@element-plus/icons-vue'
import PaginationBar from './PaginationBar.vue'
import { answerCourseQuestion, createCourseQuestion, fetchCourseQuestions, resolveCourseQuestion } from '../api/qa'
import { getCommonErrorMessage } from '../utils/errorMessage'

const props = defineProps({
  courseId: {
    type: [String, Number],
    required: true
  },
  canAsk: {
    type: Boolean,
    default: false
  },
  canManage: {
    type: Boolean,
    default: false
  },
  heading: {
    type: String,
    default: 'Learning questions'
  }
})

const loading = ref(false)
const submittingQuestion = ref(false)
const answeringId = ref(null)
const resolvingId = ref(null)
const questions = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const answerDrafts = reactive({})
const filters = reactive({
  status: ''
})
const questionForm = reactive({
  title: '',
  content: ''
})

const canUseQuestions = computed(() => props.canAsk || props.canManage)

function buildParams(nextPage) {
  return {
    page: nextPage,
    page_size: pageSize.value,
    status: filters.status || undefined
  }
}

function statusText(status) {
  const map = {
    open: '待回答',
    answered: '已回答',
    resolved: '已解决'
  }
  return map[status] || '待回答'
}

function statusTagType(status) {
  const map = {
    open: 'warning',
    answered: 'primary',
    resolved: 'success'
  }
  return map[status] || 'warning'
}

function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function resetQuestionForm() {
  questionForm.title = ''
  questionForm.content = ''
}

function hydrateAnswerDrafts(items) {
  items.forEach((question) => {
    if (!Object.prototype.hasOwnProperty.call(answerDrafts, question.id)) {
      answerDrafts[question.id] = question.answer?.content || ''
    }
  })
}

async function loadQuestions(nextPage = page.value) {
  if (!canUseQuestions.value || !props.courseId) return
  loading.value = true
  try {
    const data = await fetchCourseQuestions(props.courseId, buildParams(nextPage))
    questions.value = data?.results || []
    hydrateAnswerDrafts(questions.value)
    total.value = data?.count || questions.value.length
    page.value = data?.page || nextPage
    pageSize.value = data?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '问答加载失败'))
  } finally {
    loading.value = false
  }
}

async function submitQuestion() {
  if (!questionForm.title || !questionForm.content) {
    ElMessage.warning('请填写问题标题和描述')
    return
  }
  submittingQuestion.value = true
  try {
    await createCourseQuestion(props.courseId, {
      title: questionForm.title,
      content: questionForm.content
    })
    ElMessage.success('问题已提交')
    resetQuestionForm()
    await loadQuestions(1)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '问题提交失败'))
  } finally {
    submittingQuestion.value = false
  }
}

async function submitAnswer(question) {
  const content = answerDrafts[question.id]?.trim()
  if (!content) {
    ElMessage.warning('请填写回答内容')
    return
  }
  answeringId.value = question.id
  try {
    await answerCourseQuestion(question.id, { content })
    ElMessage.success('回答已保存')
    await loadQuestions(page.value)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '回答保存失败'))
  } finally {
    answeringId.value = null
  }
}

async function markResolved(question) {
  resolvingId.value = question.id
  try {
    await resolveCourseQuestion(question.id)
    ElMessage.success('问题已标记解决')
    await loadQuestions(page.value)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '状态更新失败'))
  } finally {
    resolvingId.value = null
  }
}

watch(
  () => [props.courseId, props.canAsk, props.canManage],
  () => {
    if (canUseQuestions.value) {
      loadQuestions(1)
    }
  }
)

onMounted(() => {
  loadQuestions(1)
})
</script>

<style scoped>
.question-panel {
  display: grid;
  gap: 18px;
  padding: 22px;
  margin-top: 22px;
}

.question-toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.question-toolbar .el-select {
  width: 140px;
}

.question-form,
.answer-form {
  display: grid;
  gap: 8px;
}

.question-list {
  display: grid;
  gap: 16px;
  min-height: 120px;
}

.question-card {
  display: grid;
  gap: 16px;
  padding: 18px;
  background: rgba(255, 250, 240, 0.74);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.question-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.question-title-row h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 900;
  letter-spacing: -0.04em;
}

.question-content,
.answer-block p {
  margin: 10px 0 0;
  color: var(--muted);
  font-weight: 800;
  line-height: 1.35;
  white-space: pre-wrap;
}

.question-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 900;
}

.answer-block {
  display: grid;
  gap: 8px;
  padding: 16px;
  background: rgba(200, 242, 58, 0.14);
  border: 2px solid rgba(25, 25, 23, 0.12);
  border-radius: var(--radius-sm);
}

.answer-block span,
.answer-block small {
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.answer-block strong {
  margin-left: 8px;
  font-size: 15px;
}

@media (max-width: 760px) {
  .question-title-row,
  .question-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .question-toolbar .el-select {
    width: 100%;
  }
}
</style>
