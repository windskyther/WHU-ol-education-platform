<template>
  <main class="page-shell exam-page">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>Online Education</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink to="/student/courses">My courses</RouterLink>
        <RouterLink to="/student/scores">Scores</RouterLink>
        <RouterLink v-if="courseId" :to="`/student/learn/${courseId}`">Learning room</RouterLink>
      </div>
    </nav>

    <section v-loading="loading" class="exam-workspace">
      <template v-if="exam">
        <header class="exam-hero">
          <div>
            <p class="eyebrow">Exam room</p>
            <h1>{{ exam.title || '在线考试' }}</h1>
            <p>{{ exam.description || '按题目要求完成作答，提交后由后端统一判分。' }}</p>
          </div>
          <aside class="exam-ticket">
            <span>题目</span>
            <strong>{{ safeQuestions.length }}</strong>
            <span>总分</span>
            <strong>{{ totalScore }}</strong>
            <span>时长</span>
            <strong>{{ exam.duration || exam.duration_minutes || '-' }} 分钟</strong>
          </aside>
        </header>

        <section class="surface exam-paper">
          <div class="paper-heading">
            <div>
              <p class="eyebrow">Answer sheet</p>
              <h2>作答区</h2>
            </div>
            <el-tag effect="light">{{ answeredCount }} / {{ safeQuestions.length }} 已答</el-tag>
          </div>

          <article v-for="(question, index) in safeQuestions" :key="question.id" class="question-card">
            <div class="question-stem">
              <span>{{ index + 1 }}</span>
              <div>
                <h3>{{ question.content || question.title || '未命名题目' }}</h3>
                <small>{{ questionTypeText(question.type) }} · {{ question.score || 0 }} 分</small>
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
              <el-radio label="true">正确</el-radio>
              <el-radio label="false">错误</el-radio>
            </el-radio-group>

            <el-input
              v-else-if="question.type === 'blank'"
              v-model.trim="answerMap[question.id]"
              placeholder="填写答案"
              clearable
            />

            <el-input
              v-else
              v-model.trim="answerMap[question.id]"
              type="textarea"
              :rows="4"
              placeholder="写下你的回答"
            />
          </article>

          <div v-if="safeQuestions.length === 0" class="empty-state">这场考试暂未发布题目。</div>

          <div class="submit-bar">
            <span>提交后不能在前端修改答卷。</span>
            <el-button type="primary" :loading="submitting" :disabled="!safeQuestions.length || submitting" @click="confirmSubmit">
              提交考试
            </el-button>
          </div>
        </section>
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { fetchExamDetail, fetchExamQuestions, submitExam } from '../../api/exam'
import { getCommonErrorMessage } from '../../utils/errorMessage'

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
    ElMessage.error(getCommonErrorMessage(error, '考试加载失败'))
  } finally {
    loading.value = false
  }
}

async function confirmSubmit() {
  await ElMessageBox.confirm('确认提交本次考试吗？提交后将由后端判分并保存成绩。', '提交考试', {
    type: 'warning',
    confirmButtonText: '提交',
    cancelButtonText: '继续作答'
  })

  submitting.value = true
  try {
    const result = await submitExam(examId.value, buildAnswers())
    const scoreText = result?.total_score !== undefined ? `，得分 ${result.total_score}` : ''
    ElMessage.success(`考试已提交${scoreText}`)
    router.push({
      path: '/student/scores',
      query: {
        course_id: courseId.value || undefined
      }
    })
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '考试提交失败'))
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
