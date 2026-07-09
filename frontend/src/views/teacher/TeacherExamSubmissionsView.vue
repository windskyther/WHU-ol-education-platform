<template>
  <main class="page-shell">
    <AppNav>
      <template #actions>
        <el-button plain @click="$router.push(`/teacher/exams/${examId}/questions`)">{{ t('teacher.submissions.questionsBtn') }}</el-button>
      </template>
    </AppNav>

    <BreadcrumbNav :items="breadcrumbItems" />

    <section class="submissions-shell">
      <header class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">{{ t('teacher.submissions.eyebrow') }}</p>
          <h1>{{ exam?.title || 'Exam submissions' }}</h1>
          <p>{{ t('teacher.submissions.description') }}</p>
        </div>
      </header>

      <section class="surface table-panel">
        <el-table v-loading="loading" :data="submissions" row-key="id">
          <el-table-column :label="t('teacher.submissions.colStudent')" min-width="180">
            <template #default="{ row }">{{ studentName(row) }}</template>
          </el-table-column>
          <el-table-column :label="t('teacher.submissions.colTotalScore')" width="110">
            <template #default="{ row }">{{ row.total_score ?? '-' }}</template>
          </el-table-column>
          <el-table-column :label="t('teacher.submissions.colObjectiveScore')" width="110">
            <template #default="{ row }">{{ row.objective_score ?? '-' }}</template>
          </el-table-column>
          <el-table-column :label="t('teacher.submissions.colSubjectiveScore')" width="110">
            <template #default="{ row }">{{ row.subjective_score ?? '-' }}</template>
          </el-table-column>
          <el-table-column :label="t('teacher.submissions.colStatus')" width="120">
            <template #default="{ row }">
              <el-tag effect="light">{{ row.status || 'submitted' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('teacher.submissions.colSubmittedAt')" min-width="180">
            <template #default="{ row }">{{ formatTime(row.submitted_at || row.created_at) }}</template>
          </el-table-column>
        </el-table>

        <div v-if="!loading && submissions.length === 0" class="empty-state">{{ t('teacher.submissions.emptyState') }}</div>
        <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadSubmissions" />
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import AppNav from '../../components/AppNav.vue'
import BreadcrumbNav from '../../components/BreadcrumbNav.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { fetchExamDetail, fetchExamSubmissions } from '../../api/exam'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()
const route = useRoute()
const examId = computed(() => route.params.examId)
const exam = ref(null)
const submissions = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const courseId = computed(() => exam.value?.course_id || exam.value?.course?.id || exam.value?.course)

const breadcrumbItems = computed(() => {
  const items = [{ label: t('teacher.submissions.breadcrumbCourseManage'), to: '/teacher/courses' }]
  if (courseId.value) {
    items.push({
      label: exam.value?.course_title || exam.value?.course?.title || t('teacher.submissions.breadcrumbCourse'),
      to: `/teacher/courses/${courseId.value}/exams`
    })
  }
  items.push({ label: exam.value?.title || t('teacher.submissions.breadcrumbExam'), to: `/teacher/exams/${examId.value}/questions` })
  items.push({ label: t('teacher.submissions.breadcrumbSubmissions') })
  return items
})

function normalizeList(data) {
  if (Array.isArray(data)) return data
  return data?.results || []
}

function studentName(row) {
  return row.student?.username || row.student_name || row.username || row.student?.email || t('teacher.submissions.studentFallback', { id: row.student_id || '-' })
}

function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

async function loadSubmissions(nextPage = page.value) {
  loading.value = true
  try {
    const [examData, submissionData] = await Promise.all([
      exam.value ? Promise.resolve(exam.value) : fetchExamDetail(examId.value),
      fetchExamSubmissions(examId.value, {
        page: nextPage,
        page_size: pageSize.value
      })
    ])
    exam.value = examData
    submissions.value = normalizeList(submissionData)
    total.value = submissionData?.count || submissions.value.length
    page.value = submissionData?.page || nextPage
    pageSize.value = submissionData?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('teacher.submissions.loadFailed')))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSubmissions(1)
})
</script>

<style scoped>
.submissions-shell {
  margin: 64px auto 0;
}

.manager-heading {
  display: grid;
  align-content: end;
  min-height: 340px;
  padding: 42px;
}

.manager-heading h1,
.manager-heading p {
  color: var(--paper);
}

.manager-heading p:not(.eyebrow) {
  max-width: 720px;
  color: rgba(246, 241, 230, 0.72);
}

.table-panel {
  margin-top: 18px;
  padding: 18px;
}
</style>
