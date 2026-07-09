<template>
  <main class="page-shell">
    <AppNav>
      <template #actions>
        <el-button plain @click="$router.push(`/teacher/courses/${courseId}/chapters`)">{{ t('teacher.exams.chaptersManageBtn') }}</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">{{ t('teacher.exams.createBtn') }}</el-button>
      </template>
    </AppNav>

    <BreadcrumbNav :items="breadcrumbItems" />

    <section class="teacher-exams-shell">
      <header class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">{{ t('teacher.exams.eyebrow') }}</p>
          <h1>{{ course?.title || 'Course exams' }}</h1>
          <p>{{ t('teacher.exams.description') }}</p>
        </div>
      </header>

      <section class="surface table-panel">
        <el-table v-loading="loading" :data="exams" row-key="id">
          <el-table-column :label="t('teacher.exams.colExam')" min-width="240">
            <template #default="{ row }">
              <div class="exam-cell">
                <strong>{{ row.title }}</strong>
                <span>{{ row.description || t('teacher.exams.noDescription') }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('teacher.exams.colStatus')" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_published ? 'success' : 'warning'" effect="light">
                {{ row.is_published ? t('teacher.exams.published') : t('teacher.exams.draft') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('teacher.exams.colDurationScore')" width="170">
            <template #default="{ row }">{{ row.duration || row.duration_minutes || '-' }} {{ t('teacher.exams.minuteSuffix') }} / {{ row.pass_score ?? '-' }} / {{ row.excellent_score ?? t('teacher.exams.excellentNotSet') }}</template>
          </el-table-column>
          <el-table-column :label="t('teacher.exams.colTime')" min-width="230">
            <template #default="{ row }">
              <div class="time-cell">
                <span>{{ formatTime(row.start_time) }}</span>
                <span>{{ formatTime(row.end_time) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('teacher.exams.colActions')" min-width="240" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button
                  size="small"
                  text
                  :type="row.is_published ? 'warning' : 'success'"
                  :loading="publishingId === row.id"
                  @click="togglePublish(row)"
                >
                  {{ row.is_published ? t('teacher.exams.unpublishBtn') : t('teacher.exams.publishBtn') }}
                </el-button>
                <el-button size="small" text :icon="Edit" @click="openEditDialog(row)">{{ t('teacher.exams.editBtn') }}</el-button>
                <el-button size="small" text :icon="Edit" @click="$router.push(`/teacher/exams/${row.id}/questions`)">{{ t('teacher.exams.questionsBtn') }}</el-button>
                <el-button size="small" text :icon="Tickets" @click="$router.push(`/teacher/exams/${row.id}/submissions`)">{{ t('teacher.exams.submissionsBtn') }}</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="!loading && exams.length === 0" class="empty-state">{{ t('teacher.exams.emptyState') }}</div>
      </section>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingExamId ? t('teacher.exams.dialogEditTitle') : t('teacher.exams.dialogCreateTitle')" width="640px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item :label="t('teacher.exams.titleLabel')" prop="title">
          <el-input v-model.trim="form.title" :placeholder="t('teacher.exams.titlePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('teacher.exams.descriptionLabel')">
          <el-input v-model.trim="form.description" type="textarea" :rows="3" :placeholder="t('teacher.exams.descriptionPlaceholder')" />
        </el-form-item>
        <div class="dialog-grid">
          <el-form-item :label="t('teacher.exams.durationLabel')" prop="duration">
            <el-input-number v-model="form.duration" :min="1" :max="600" />
          </el-form-item>
          <el-form-item :label="t('teacher.exams.passScoreLabel')" prop="pass_score">
            <el-input-number v-model="form.pass_score" :min="0" :max="1000" />
          </el-form-item>
        </div>
        <el-form-item :label="t('teacher.exams.excellentScoreLabel')" prop="excellent_score">
          <el-input-number
            v-model="form.excellent_score"
            :min="0"
            :max="form.pass_score || 1000"
            :placeholder="t('teacher.exams.excellentScorePlaceholder')"
            clearable
          />
        </el-form-item>
        <div class="dialog-grid">
          <el-form-item :label="t('teacher.exams.startTimeLabel')">
            <el-date-picker
              v-model="form.start_time"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              :placeholder="t('teacher.exams.startTimePlaceholder')"
              :disabled-date="disablePastDate"
            />
          </el-form-item>
          <el-form-item :label="t('teacher.exams.endTimeLabel')">
            <el-date-picker
              v-model="form.end_time"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              :placeholder="t('teacher.exams.endTimePlaceholder')"
              :disabled-date="disablePastDate"
            />
          </el-form-item>
        </div>
        <el-form-item :label="t('teacher.exams.publishStatusLabel')">
          <el-switch v-model="form.is_published" :active-text="t('teacher.exams.publishedActiveText')" :inactive-text="t('teacher.exams.draftInactiveText')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ t('teacher.exams.cancelBtn') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitExam">{{ t('teacher.exams.saveBtn') }}</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Plus, Tickets } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import AppNav from '../../components/AppNav.vue'
import BreadcrumbNav from '../../components/BreadcrumbNav.vue'
import { fetchCourseDetail } from '../../api/course'
import { createCourseExam, fetchCourseExams, updateCourseExam } from '../../api/exam'
import { getCommonErrorMessage, getExamErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()
const route = useRoute()
const courseId = computed(() => route.params.id)
const course = ref(null)
const exams = ref([])
const loading = ref(false)
const submitting = ref(false)
const publishingId = ref(null)
const dialogVisible = ref(false)
const formRef = ref()
const editingExamId = ref(null)

const form = reactive({
  title: '',
  description: '',
  duration: 60,
  pass_score: 60,
  excellent_score: null,
  start_time: '',
  end_time: '',
  is_published: false
})

const rules = computed(() => ({
  title: [{ required: true, message: t('teacher.exams.titleRequired'), trigger: 'blur' }],
  duration: [{ required: true, message: t('teacher.exams.durationRequired'), trigger: 'blur' }],
  pass_score: [{ required: true, message: t('teacher.exams.passScoreRequired'), trigger: 'blur' }]
}))

const breadcrumbItems = computed(() => [
  { label: t('teacher.exams.breadcrumbCourseManage'), to: '/teacher/courses' },
  { label: course.value?.title || t('teacher.exams.breadcrumbCourse'), to: `/teacher/courses/${courseId.value}/chapters` },
  { label: t('teacher.exams.breadcrumbExams') }
])

function normalizeList(data) {
  if (Array.isArray(data)) return data
  return data?.results || []
}

function resetForm() {
  form.title = ''
  form.description = ''
  form.duration = 60
  form.pass_score = 60
  form.excellent_score = null
  form.start_time = ''
  form.end_time = ''
  form.is_published = false
}

function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function disablePastDate(date) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date.getTime() < today.getTime()
}

function validateExamTime() {
  if (editingExamId.value) return true
  const now = Date.now()
  const startTime = form.start_time ? new Date(form.start_time).getTime() : null
  const endTime = form.end_time ? new Date(form.end_time).getTime() : null

  if (startTime && startTime <= now) {
    ElMessage.error(t('teacher.exams.startTimeAfterNow'))
    return false
  }

  if (endTime && endTime <= now) {
    ElMessage.error(t('teacher.exams.endTimeAfterNow'))
    return false
  }

  if (startTime && endTime && endTime <= startTime) {
    ElMessage.error(t('teacher.exams.endTimeAfterStart'))
    return false
  }

  return true
}

function openCreateDialog() {
  editingExamId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row) {
  editingExamId.value = row.id
  form.title = row.title
  form.description = row.description || ''
  form.duration = row.duration || row.duration_minutes || 60
  form.pass_score = row.pass_score ?? 60
  form.excellent_score = row.excellent_score ?? null
  form.start_time = row.start_time || ''
  form.end_time = row.end_time || ''
  form.is_published = !!row.is_published
  dialogVisible.value = true
}

async function loadPage() {
  loading.value = true
  try {
    const [courseData, examData] = await Promise.all([
      fetchCourseDetail(courseId.value),
      fetchCourseExams(courseId.value)
    ])
    course.value = courseData
    exams.value = normalizeList(examData)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('teacher.exams.loadFailed')))
  } finally {
    loading.value = false
  }
}

async function handleSubmitExam() {
  await formRef.value?.validate()
  if (!validateExamTime()) return

  submitting.value = true
  try {
    if (editingExamId.value) {
      await updateCourseExam(editingExamId.value, { ...form })
      ElMessage.success(t('teacher.exams.updated'))
    } else {
      await createCourseExam(courseId.value, { ...form })
      ElMessage.success(t('teacher.exams.created'))
    }
    dialogVisible.value = false
    loadPage()
  } catch (error) {
    ElMessage.error(getExamErrorMessage(error, editingExamId.value ? t('teacher.exams.updateFailed') : t('teacher.exams.createFailed')))
  } finally {
    submitting.value = false
  }
}

async function togglePublish(row) {
  const nextPublished = !row.is_published
  await ElMessageBox.confirm(
    nextPublished ? t('teacher.exams.confirmPublishMsg') : t('teacher.exams.confirmUnpublishMsg'),
    nextPublished ? t('teacher.exams.confirmPublishTitle') : t('teacher.exams.confirmUnpublishTitle'),
    {
      type: 'warning',
      confirmButtonText: nextPublished ? t('teacher.exams.publishBtn') : t('teacher.exams.unpublishBtn'),
      cancelButtonText: t('teacher.exams.cancelBtn')
    }
  )

  publishingId.value = row.id
  try {
    await updateCourseExam(row.id, {
      is_published: nextPublished
    })
    ElMessage.success(nextPublished ? t('teacher.exams.publishedMsg') : t('teacher.exams.unpublishedMsg'))
    await loadPage()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, nextPublished ? t('teacher.exams.publishFailed') : t('teacher.exams.unpublishFailed')))
  } finally {
    publishingId.value = null
  }
}

onMounted(() => {
  loadPage()
})
</script>

<style scoped>
.teacher-exams-shell {
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

.exam-cell,
.time-cell {
  display: grid;
  gap: 6px;
}

.exam-cell strong {
  font-weight: 900;
}

.exam-cell span,
.time-cell span {
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
