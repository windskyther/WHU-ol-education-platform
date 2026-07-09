<template>
  <main class="page-shell">
    <AppNav>
      <template #actions>
        <el-button plain @click="$router.push(`/teacher/exams/${examId}/submissions`)">{{ t('teacher.questions.submissionsBtn') }}</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">{{ t('teacher.questions.createBtn') }}</el-button>
      </template>
    </AppNav>

    <BreadcrumbNav :items="breadcrumbItems" />

    <section class="question-manager-shell">
      <header class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">{{ t('teacher.questions.eyebrow') }}</p>
          <h1>{{ exam?.title || 'Exam questions' }}</h1>
          <p>{{ t('teacher.questions.description') }}</p>
        </div>
      </header>

      <section class="surface table-panel">
        <el-table v-loading="loading" :data="orderedQuestions" row-key="id">
          <el-table-column :label="t('teacher.questions.colOrder')" width="90">
            <template #default="{ row }">{{ row.order_no ?? row.order ?? 0 }}</template>
          </el-table-column>
          <el-table-column :label="t('teacher.questions.colQuestion')" min-width="260">
            <template #default="{ row }">
              <div class="question-cell">
                <strong>{{ row.content }}</strong>
                <span>{{ questionTypeText(row.type) }} · {{ row.score }} {{ t('teacher.questions.scoreSuffix') }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('teacher.questions.colOptions')" min-width="220">
            <template #default="{ row }">{{ optionSummary(row) }}</template>
          </el-table-column>
          <el-table-column :label="t('teacher.questions.colActions')" width="180" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button size="small" text :icon="Edit" @click="openEditDialog(row)">{{ t('teacher.questions.editBtn') }}</el-button>
                <el-button size="small" type="danger" plain :icon="Delete" :loading="deletingId === row.id" @click="confirmDelete(row)">{{ t('teacher.questions.deleteBtn') }}</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="!loading && orderedQuestions.length === 0" class="empty-state">{{ t('teacher.questions.emptyState') }}</div>
      </section>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingQuestion?.id ? t('teacher.questions.dialogEditTitle') : t('teacher.questions.dialogCreateTitle')" width="720px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <div class="dialog-grid">
          <el-form-item :label="t('teacher.questions.typeLabel')" prop="type">
            <el-select v-model="form.type" :placeholder="t('teacher.questions.typePlaceholder')">
              <el-option :label="t('teacher.questions.typeSingle')" value="single" />
              <el-option :label="t('teacher.questions.typeMultiple')" value="multiple" />
              <el-option :label="t('teacher.questions.typeJudge')" value="judge" />
              <el-option :label="t('teacher.questions.typeBlank')" value="blank" />
              <el-option :label="t('teacher.questions.typeShort')" value="short" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('teacher.questions.scoreLabel')" prop="score">
            <el-input-number v-model="form.score" :min="0" :max="1000" />
          </el-form-item>
        </div>
        <el-form-item :label="t('teacher.questions.contentLabel')" prop="content">
          <el-input v-model.trim="form.content" type="textarea" :rows="4" :placeholder="t('teacher.questions.contentPlaceholder')" />
        </el-form-item>
        <el-form-item v-if="needsOptions" :label="t('teacher.questions.optionsLabel')">
          <el-input v-model="form.optionsText" type="textarea" :rows="5" :placeholder="t('teacher.questions.optionsPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('teacher.questions.answerLabel')" prop="answerText">
          <el-input v-model.trim="form.answerText" type="textarea" :rows="3" :placeholder="t('teacher.questions.answerPlaceholder')" />
        </el-form-item>
        <div class="dialog-grid">
          <el-form-item :label="t('teacher.questions.orderLabel')">
            <el-input-number v-model="form.order_no" :min="0" :max="999" />
          </el-form-item>
          <el-form-item :label="t('teacher.questions.analysisLabel')">
            <el-input v-model.trim="form.analysis" :placeholder="t('teacher.questions.analysisPlaceholder')" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('teacher.questions.cancelBtn') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSaveQuestion">{{ t('teacher.questions.saveBtn') }}</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import AppNav from '../../components/AppNav.vue'
import BreadcrumbNav from '../../components/BreadcrumbNav.vue'
import {
  createExamQuestion,
  deleteExamQuestion,
  fetchExamDetail,
  fetchExamQuestions,
  updateExamQuestion
} from '../../api/exam'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()
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

const rules = computed(() => ({
  type: [{ required: true, message: t('teacher.questions.typeRequired'), trigger: 'change' }],
  content: [{ required: true, message: t('teacher.questions.contentRequired'), trigger: 'blur' }],
  answerText: [{ required: true, message: t('teacher.questions.answerRequired'), trigger: 'blur' }],
  score: [{ required: true, message: t('teacher.questions.scoreRequired'), trigger: 'blur' }]
}))

const courseId = computed(() => exam.value?.course_id || exam.value?.course?.id || exam.value?.course)
const orderedQuestions = computed(() => [...questions.value].sort((a, b) => questionOrder(a) - questionOrder(b)))
const needsOptions = computed(() => ['single', 'multiple'].includes(form.type))

const breadcrumbItems = computed(() => {
  const items = [{ label: t('teacher.questions.breadcrumbCourseManage'), to: '/teacher/courses' }]
  if (courseId.value) {
    items.push({
      label: exam.value?.course_title || exam.value?.course?.title || t('teacher.questions.breadcrumbCourse'),
      to: `/teacher/courses/${courseId.value}/exams`
    })
  }
  items.push({ label: exam.value?.title || t('teacher.questions.breadcrumbExam'), to: courseId.value ? `/teacher/courses/${courseId.value}/exams` : undefined })
  items.push({ label: t('teacher.questions.breadcrumbQuestions') })
  return items
})

function questionOrder(question) {
  return question.order_no ?? question.order ?? 0
}

function questionTypeText(type) {
  const map = {
    single: t('teacher.questions.typeSingle'),
    multiple: t('teacher.questions.typeMultiple'),
    judge: t('teacher.questions.typeJudge'),
    blank: t('teacher.questions.typeBlank'),
    short: t('teacher.questions.typeShort')
  }
  return map[type] || t('teacher.questions.typeDefault')
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
    ElMessage.error(getCommonErrorMessage(error, t('teacher.questions.loadFailed')))
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
      ElMessage.success(t('teacher.questions.updated'))
    } else {
      await createExamQuestion(examId.value, buildPayload())
      ElMessage.success(t('teacher.questions.created'))
    }
    dialogVisible.value = false
    loadPage()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('teacher.questions.saveFailed')))
  } finally {
    submitting.value = false
  }
}

async function confirmDelete(question) {
  await ElMessageBox.confirm(
    t('teacher.questions.confirmDeleteMsg'),
    t('teacher.questions.confirmDeleteTitle'),
    {
      type: 'warning',
      confirmButtonText: t('teacher.questions.confirmDeleteBtn'),
      cancelButtonText: t('teacher.questions.confirmCancelBtn')
    }
  )

  deletingId.value = question.id
  try {
    await deleteExamQuestion(question.id)
    ElMessage.success(t('teacher.questions.deleted'))
    loadPage()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('teacher.questions.deleteFailed')))
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
