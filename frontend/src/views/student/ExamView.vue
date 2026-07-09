<template>
  <main class="page-shell exam-page">
    <AppNav />

    <BreadcrumbNav :items="breadcrumbItems" />

    <section v-loading="loading" class="exam-workspace">
      <template v-if="exam">
        <header class="exam-hero">
          <div>
            <p class="eyebrow">{{ t('student.exam.eyebrow') }}</p>
            <h1>{{ exam.title || t('student.exam.defaultTitle') }}</h1>
            <p>{{ exam.description || t('student.exam.defaultDesc') }}</p>
          </div>
          <aside class="exam-ticket">
            <span>{{ t('student.exam.questionsLabel') }}</span>
            <strong>{{ safeQuestions.length }}</strong>
            <span>{{ t('student.exam.totalScoreLabel') }}</span>
            <strong>{{ totalScore }}</strong>
            <span>{{ t('student.exam.durationLabel') }}</span>
            <strong>{{ exam.duration || exam.duration_minutes || '-' }} {{ t('student.exam.minutes') }}</strong>
          </aside>
        </header>

        <section class="surface exam-paper">
          <div class="paper-heading">
            <div>
              <p class="eyebrow">{{ t('student.exam.answerSheetEyebrow') }}</p>
              <h2>{{ t('student.exam.answerSheetHeading') }}</h2>
            </div>
            <el-tag effect="light">{{ t('student.exam.answeredProgress', { answered: answeredCount, total: safeQuestions.length }) }}</el-tag>
          </div>

          <article v-for="(question, index) in safeQuestions" :key="question.id" class="question-card">
            <div class="question-stem">
              <span>{{ index + 1 }}</span>
              <div>
                <h3>{{ question.content || question.title || t('student.exam.unnamedQuestion') }}</h3>
                <small>{{ questionTypeText(question.type) }} · {{ t('student.exam.scorePoints', { score: question.score || 0 }) }}</small>
              </div>
            </div>

            <el-radio-group v-if="question.type === 'single'" v-model="answerMap[question.id]" class="option-stack">
              <el-radio v-for="option in optionList(question)" :key="option.value" :label="option.value">
                {{ option.label }}
              </el-radio>
            </el-radio-group>

            <el-checkbox-group v-else-if="question.type === 'multiple'" v-model="answerMap[question.id]" class="option-stack">
              <el-checkbox v-for="option in optionList(question)" :key="option.value" :label="option.value">
                {{ option.label }}
              </el-checkbox>
            </el-checkbox-group>

            <el-radio-group v-else-if="question.type === 'judge'" v-model="answerMap[question.id]" class="option-stack">
              <el-radio label="true">{{ t('student.exam.judgeTrue') }}</el-radio>
              <el-radio label="false">{{ t('student.exam.judgeFalse') }}</el-radio>
            </el-radio-group>

            <el-input
              v-else-if="question.type === 'blank'"
              v-model.trim="answerMap[question.id]"
              :placeholder="t('student.exam.blankPlaceholder')"
              clearable
            />

            <el-input
              v-else
              v-model.trim="answerMap[question.id]"
              type="textarea"
              :rows="4"
              :placeholder="t('student.exam.textareaPlaceholder')"
            />
          </article>

          <div v-if="safeQuestions.length === 0" class="empty-state">{{ t('student.exam.noQuestions') }}</div>

          <div class="submit-bar">
            <span>{{ t('student.exam.submitWarning') }}</span>
            <el-button type="primary" :loading="submitting" :disabled="!safeQuestions.length || submitting" @click="confirmSubmit">
              {{ t('student.exam.submitButton') }}
            </el-button>
          </div>
        </section>
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import AppNav from '../../components/AppNav.vue'
import BreadcrumbNav from '../../components/BreadcrumbNav.vue'
import { fetchExamDetail, fetchExamQuestions, submitExam } from '../../api/exam'
import { getCommonErrorMessage, getExamErrorCode, getExamErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const examId = computed(() => route.params.examId)
const loading = ref(false)
const submitting = ref(false)
const exam = ref(null)
const questions = ref([])
const answerMap = reactive({})

const safeQuestions = computed(() => questions.value.map(({ answer, analysis, ...question }) => question))
const courseId = computed(() => exam.value?.course_id || exam.value?.course?.id || exam.value?.course)
const totalScore = computed(() => safeQuestions.value.reduce((sum, question) => sum + (Number(question.score) || 0), 0))
const answeredCount = computed(() => {
  return safeQuestions.value.filter((question) => {
    const value = answerMap[question.id]
    return Array.isArray(value) ? value.length > 0 : value !== undefined && value !== ''
  }).length
})

const breadcrumbItems = computed(() => {
  const items = [{ label: t('student.exam.breadcrumbMyCourses'), to: '/student/courses' }]
  if (courseId.value) {
    items.push({ label: exam.value?.course_title || exam.value?.course?.title || t('student.exam.breadcrumbLearnFallback'), to: `/student/learn/${courseId.value}` })
  }
  items.push({ label: exam.value?.title || t('student.exam.breadcrumbExamFallback') })
  return items
})

function questionTypeText(type) {
  const map = {
    single: t('student.exam.typeSingle'),
    multiple: t('student.exam.typeMultiple'),
    judge: t('student.exam.typeJudge'),
    blank: t('student.exam.typeBlank'),
    short: t('student.exam.typeShort')
  }
  return map[type] || t('student.exam.typeDefault')
}

function optionList(question) {
  const options = Array.isArray(question.options) ? question.options : []
  return options.map((option, index) => {
    if (option && typeof option === 'object') {
      const value = option.value ?? option.key ?? option.label ?? String(index)
      return {
        value,
        label: option.label ?? option.text ?? option.content ?? value
      }
    }
    return {
      value: String(option),
      label: String(option)
    }
  })
}

function normalizeQuestions(data) {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.results)) return data.results
  if (Array.isArray(data?.questions)) return data.questions
  return []
}

function seedAnswers(items) {
  items.forEach((question) => {
    if (question.type === 'multiple') {
      answerMap[question.id] = []
    } else {
      answerMap[question.id] = ''
    }
  })
}

function buildAnswers() {
  return safeQuestions.value.map((question) => ({
    question_id: question.id,
    answer: answerMap[question.id]
  }))
}

function resetExamState() {
  exam.value = null
  questions.value = []
  Object.keys(answerMap).forEach((key) => {
    delete answerMap[key]
  })
}

function courseIdFromError(error) {
  const data = error?.rawData?.data || error?.response?.data?.data || {}
  return data.course_id || data.course?.id || route.query.course_id || ''
}

function handleExamLoadError(error) {
  const code = getExamErrorCode(error)
  const message = getExamErrorMessage(error, t('student.exam.loadError'))
  resetExamState()
  ElMessage.error(message)

  if (code === 'EXAM_ALREADY_SUBMITTED') {
    router.push('/student/scores')
    return
  }

  if (code === 'EXAM_ENDED') {
    const targetCourseId = courseIdFromError(error)
    if (targetCourseId) {
      router.push(`/student/learn/${targetCourseId}`)
    } else {
      router.push('/student/courses')
    }
  }
}

async function loadExam() {
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
    seedAnswers(questionItems)
  } catch (error) {
    handleExamLoadError(error)
  } finally {
    loading.value = false
  }
}

async function confirmSubmit() {
  await ElMessageBox.confirm(t('student.exam.confirmMessage'), t('student.exam.confirmTitle'), {
    type: 'warning',
    confirmButtonText: t('student.exam.confirmOk'),
    cancelButtonText: t('student.exam.confirmCancel')
  })

  submitting.value = true
  try {
    const result = await submitExam(examId.value, buildAnswers())
    const msg = result?.total_score !== undefined
      ? t('student.exam.submitSuccessWithScore', { score: result.total_score })
      : t('student.exam.submitSuccess')
    ElMessage.success(msg)
    router.push({
      path: '/student/scores',
      query: {
        course_id: courseId.value || undefined
      }
    })
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('student.exam.submitError')))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadExam()
})
</script>

<style scoped>
.exam-workspace {
  margin: 64px auto 0;
}

.exam-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 260px;
  gap: 18px;
  align-items: stretch;
}

.exam-hero > div {
  display: grid;
  align-content: end;
  min-height: 360px;
  padding: 42px;
  background: rgba(255, 250, 240, 0.88);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.exam-hero h1 {
  margin: 0;
  font-size: clamp(48px, 8vw, 118px);
  font-weight: 900;
  line-height: 0.84;
  letter-spacing: -0.07em;
}

.exam-hero p:not(.eyebrow) {
  max-width: 720px;
  color: var(--muted);
  font-size: clamp(17px, 1.8vw, 24px);
  font-weight: 800;
  line-height: 1.18;
}

.exam-ticket {
  display: grid;
  align-content: end;
  gap: 8px;
  padding: 28px;
  color: var(--paper);
  background: var(--ink);
  border-radius: var(--radius-md);
}

.exam-ticket span {
  color: rgba(246, 241, 230, 0.62);
  font-size: 12px;
  font-weight: 900;
}

.exam-ticket strong {
  margin-bottom: 12px;
  font-size: 34px;
  font-weight: 900;
  line-height: 0.9;
}

.exam-paper {
  display: grid;
  gap: 16px;
  margin-top: 18px;
  padding: 18px;
}

.paper-heading,
.submit-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
}

.paper-heading h2 {
  margin: 0;
  font-size: clamp(34px, 5vw, 64px);
  font-weight: 900;
  line-height: 0.86;
  letter-spacing: -0.06em;
}

.question-card {
  display: grid;
  gap: 16px;
  padding: 22px;
  background: var(--paper-soft);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
}

.question-stem {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.question-stem > span {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  color: var(--paper);
  background: var(--ink);
  border-radius: var(--radius-sm);
  font-weight: 900;
}

.question-stem h3 {
  margin: 0 0 8px;
  font-size: 20px;
  line-height: 1.28;
}

.question-stem small {
  color: var(--muted);
  font-weight: 900;
}

.option-stack {
  display: grid;
  gap: 10px;
}

.option-stack :deep(.el-radio),
.option-stack :deep(.el-checkbox) {
  min-height: 42px;
  margin-right: 0;
  padding: 10px 12px;
  background: rgba(25, 25, 23, 0.04);
  border: 2px solid var(--line);
  border-radius: var(--radius-sm);
}

.submit-bar {
  position: sticky;
  bottom: 12px;
  padding: 14px;
  background: rgba(255, 250, 240, 0.95);
  border: 2px solid var(--line);
  border-radius: var(--radius-md);
  backdrop-filter: blur(12px);
}

.submit-bar span {
  color: var(--muted);
  font-weight: 900;
}

@media (max-width: 820px) {
  .exam-hero {
    grid-template-columns: 1fr;
  }
}
</style>
