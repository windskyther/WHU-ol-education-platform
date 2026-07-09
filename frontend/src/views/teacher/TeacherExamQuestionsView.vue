<template>
  <main class="page-shell">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>Online Education</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink v-if="courseId" :to="`/teacher/courses/${courseId}/exams`">Course exams</RouterLink>
        <RouterLink :to="`/teacher/exams/${examId}/submissions`">Submissions</RouterLink>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">Create question</el-button>
      </div>
    </nav>

    <section class="question-manager-shell">
      <header class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">Question editor</p>
          <h1>{{ exam?.title || 'Exam questions' }}</h1>
          <p>维护题干、选项、标准答案和分值。学生作答页不会展示答案字段。</p>
        </div>
      </header>

      <section class="surface table-panel">
        <el-table v-loading="loading" :data="orderedQuestions" row-key="id">
          <el-table-column label="排序" width="90">
            <template #default="{ row }">{{ row.order_no ?? row.order ?? 0 }}</template>
          </el-table-column>
          <el-table-column label="题目" min-width="260">
            <template #default="{ row }">
              <div class="question-cell">
                <strong>{{ row.content }}</strong>
                <span>{{ questionTypeText(row.type) }} · {{ row.score }} 分</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="选项" min-width="220">
            <template #default="{ row }">{{ optionSummary(row) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button size="small" text :icon="Edit" @click="openEditDialog(row)">编辑</el-button>
                <el-button size="small" type="danger" plain :icon="Delete" :loading="deletingId === row.id" @click="confirmDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="!loading && orderedQuestions.length === 0" class="empty-state">暂无题目，先创建第一道题。</div>
      </section>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingQuestion?.id ? '编辑题目' : '创建题目'" width="720px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="dialog-grid">
          <el-form-item label="题型" prop="type">
            <el-select v-model="form.type" placeholder="选择题型">
              <el-option label="单选题" value="single" />
              <el-option label="多选题" value="multiple" />
              <el-option label="判断题" value="judge" />
              <el-option label="填空题" value="blank" />
              <el-option label="简答题" value="short" />
            </el-select>
          </el-form-item>
          <el-form-item label="分值" prop="score">
            <el-input-number v-model="form.score" :min="0" :max="1000" />
          </el-form-item>
        </div>
        <el-form-item label="题干" prop="content">
          <el-input v-model.trim="form.content" type="textarea" :rows="4" placeholder="输入题干" />
        </el-form-item>
        <el-form-item v-if="needsOptions" label="选项">
          <el-input v-model="form.optionsText" type="textarea" :rows="5" placeholder="每行一个选项，例如 A. python" />
        </el-form-item>
        <el-form-item label="标准答案" prop="answerText">
          <el-input v-model.trim="form.answerText" type="textarea" :rows="3" placeholder="多选题可用逗号分隔多个答案" />
        </el-form-item>
        <div class="dialog-grid">
          <el-form-item label="排序">
            <el-input-number v-model="form.order_no" :min="0" :max="999" />
          </el-form-item>
          <el-form-item label="解析">
            <el-input v-model.trim="form.analysis" placeholder="可选" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSaveQuestion">保存</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus } from '@element-plus/icons-vue'
import {
  createExamQuestion,
  deleteExamQuestion,
  fetchExamDetail,
  fetchExamQuestions,
  updateExamQuestion
} from '../../api/exam'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const examId = computed(() => route.params.examId)
const exam = ref(null)
const questions = ref([])
const loading = ref(false)
const submitting = ref(false)
const deletingId = ref(null)
const dialogVisible = ref(false)
const editingQuestion = ref(null)
const formRef = ref()

const form = reactive({
  type: 'single',
  content: '',
  optionsText: '',
  answerText: '',
  score: 5,
  analysis: '',
  order_no: 0
})

const rules = {
  type: [{ required: true, message: '请选择题型', trigger: 'change' }],
  content: [{ required: true, message: '请输入题干', trigger: 'blur' }],
  answerText: [{ required: true, message: '请输入标准答案', trigger: 'blur' }],
  score: [{ required: true, message: '请输入分值', trigger: 'blur' }]
}

const courseId = computed(() => exam.value?.course_id || exam.value?.course?.id || exam.value?.course)
const orderedQuestions = computed(() => [...questions.value].sort((a, b) => questionOrder(a) - questionOrder(b)))
const needsOptions = computed(() => ['single', 'multiple'].includes(form.type))

function questionOrder(question) {
  return question.order_no ?? question.order ?? 0
}

function questionTypeText(type) {
  const map = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    blank: '填空题',
    short: '简答题'
  }
  return map[type] || '题目'
}

function normalizeQuestions(data) {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.results)) return data.results
  if (Array.isArray(data?.questions)) return data.questions
  return []
}

function optionSummary(question) {
  const options = Array.isArray(question.options) ? question.options : []
  if (!options.length) return '-'
  return options.map((option) => (typeof option === 'object' ? option.label || option.text || option.value : option)).join(' / ')
}

function resetForm(question = null) {
  editingQuestion.value = question
  form.type = question?.type || 'single'
  form.content = question?.content || ''
  form.optionsText = Array.isArray(question?.options)
    ? question.options.map((option) => (typeof option === 'object' ? option.label || option.text || option.value : option)).join('\n')
    : ''
  form.answerText = Array.isArray(question?.answer) ? question.answer.join(', ') : question?.answer || ''
  form.score = Number(question?.score) || 5
  form.analysis = question?.analysis || ''
  form.order_no = question?.order_no ?? question?.order ?? nextOrder()
}

function nextOrder() {
  return orderedQuestions.value.reduce((max, question) => Math.max(max, questionOrder(question)), 0) + 1
}

function buildPayload() {
  const options = form.optionsText
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
  const answer = form.type === 'multiple'
    ? form.answerText.split(/[,，\n]/).map((item) => item.trim()).filter(Boolean)
    : form.answerText

  return {
    type: form.type,
    content: form.content,
    options: needsOptions.value ? options : [],
    answer,
    score: form.score,
    analysis: form.analysis,
    order_no: form.order_no
  }
}

function openCreateDialog() {
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(question) {
  resetForm(question)
  dialogVisible.value = true
}

async function loadPage() {
  loading.value = true
  try {
    const examData = await fetchExamDetail(examId.value)
    exam.value = examData
    let questionItems = normalizeQuestions(examData)
    if (!questionItems.length) {
      const questionData = await fetchExamQuestions(examId.value)
      questionItems = normalizeQuestions(questionData)
    }
    questions.value = questionItems
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '题目信息加载失败'))
  } finally {
    loading.value = false
  }
}

async function handleSaveQuestion() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (editingQuestion.value?.id) {
      await updateExamQuestion(editingQuestion.value.id, buildPayload())
      ElMessage.success('题目已更新')
    } else {
      await createExamQuestion(examId.value, buildPayload())
      ElMessage.success('题目已创建')
    }
    dialogVisible.value = false
    loadPage()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '题目保存失败'))
  } finally {
    submitting.value = false
  }
}

async function confirmDelete(question) {
  await ElMessageBox.confirm('确认删除这道题吗？', '删除题目', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })

  deletingId.value = question.id
  try {
    await deleteExamQuestion(question.id)
    ElMessage.success('题目已删除')
    loadPage()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '题目删除失败'))
  } finally {
    deletingId.value = null
  }
}

onMounted(() => {
  loadPage()
})
</script>

<style scoped>
.question-manager-shell {
  margin: 64px auto 0;
}

.manager-heading {
  display: grid;
  align-content: end;
  min-height: 360px;
  padding: 42px;
}

.manager-heading h1,
.manager-heading p {
  color: var(--paper);
}

.manager-heading p:not(.eyebrow) {
  max-width: 760px;
  color: rgba(246, 241, 230, 0.72);
}

.table-panel {
  margin-top: 18px;
  padding: 18px;
}

.question-cell {
  display: grid;
  gap: 6px;
}

.question-cell strong {
  font-weight: 900;
}

.question-cell span {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.dialog-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 720px) {
  .dialog-grid {
    grid-template-columns: 1fr;
  }
}
</style>
