<template>
  <main class="page-shell">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>Online Education</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink to="/teacher/courses">Course manager</RouterLink>
        <RouterLink :to="`/teacher/courses/${courseId}/chapters`">Chapters</RouterLink>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">Create exam</el-button>
      </div>
    </nav>

    <section class="teacher-exams-shell">
      <header class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">Exam manager</p>
          <h1>{{ course?.title || 'Course exams' }}</h1>
          <p>创建课程考试并进入题目维护。学生端只会展示已发布考试和不含答案的题目。</p>
        </div>
      </header>

      <section class="surface table-panel">
        <el-table v-loading="loading" :data="exams" row-key="id">
          <el-table-column label="考试" min-width="240">
            <template #default="{ row }">
              <div class="exam-cell">
                <strong>{{ row.title }}</strong>
                <span>{{ row.description || '暂无考试说明' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_published ? 'success' : 'warning'" effect="light">
                {{ row.is_published ? '已发布' : '草稿' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="时长/及格" width="140">
            <template #default="{ row }">{{ row.duration || row.duration_minutes || '-' }} 分 / {{ row.pass_score ?? '-' }}</template>
          </el-table-column>
          <el-table-column label="时间" min-width="230">
            <template #default="{ row }">
              <div class="time-cell">
                <span>{{ formatTime(row.start_time) }}</span>
                <span>{{ formatTime(row.end_time) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="240" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button
                  size="small"
                  text
                  :type="row.is_published ? 'warning' : 'success'"
                  :loading="publishingId === row.id"
                  @click="togglePublish(row)"
                >
                  {{ row.is_published ? '下架' : '发布' }}
                </el-button>
                <el-button size="small" text :icon="Edit" @click="$router.push(`/teacher/exams/${row.id}/questions`)">题目</el-button>
                <el-button size="small" text :icon="Tickets" @click="$router.push(`/teacher/exams/${row.id}/submissions`)">答卷</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="!loading && exams.length === 0" class="empty-state">暂无考试，先创建一场课程考试。</div>
      </section>
    </section>

    <el-dialog v-model="dialogVisible" title="创建考试" width="640px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="考试标题" prop="title">
          <el-input v-model.trim="form.title" placeholder="例如：Python 阶段测验" />
        </el-form-item>
        <el-form-item label="考试说明">
          <el-input v-model.trim="form.description" type="textarea" :rows="3" placeholder="说明考试范围和提交要求" />
        </el-form-item>
        <div class="dialog-grid">
          <el-form-item label="时长（分钟）" prop="duration">
            <el-input-number v-model="form.duration" :min="1" :max="600" />
          </el-form-item>
          <el-form-item label="及格线" prop="pass_score">
            <el-input-number v-model="form.pass_score" :min="0" :max="1000" />
          </el-form-item>
        </div>
        <div class="dialog-grid">
          <el-form-item label="开始时间">
            <el-date-picker
              v-model="form.start_time"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="选择开始时间"
              :disabled-date="disablePastDate"
            />
          </el-form-item>
          <el-form-item label="结束时间">
            <el-date-picker
              v-model="form.end_time"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="选择结束时间"
              :disabled-date="disablePastDate"
            />
          </el-form-item>
        </div>
        <el-form-item label="发布状态">
          <el-switch v-model="form.is_published" active-text="已发布" inactive-text="草稿" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreateExam">保存</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Plus, Tickets } from '@element-plus/icons-vue'
import { fetchCourseDetail } from '../../api/course'
import { createCourseExam, fetchCourseExams, updateCourseExam } from '../../api/exam'
import { getCommonErrorMessage, getExamErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const courseId = computed(() => route.params.id)
const course = ref(null)
const exams = ref([])
const loading = ref(false)
const submitting = ref(false)
const publishingId = ref(null)
const dialogVisible = ref(false)
const formRef = ref()

const form = reactive({
  title: '',
  description: '',
  duration: 60,
  pass_score: 60,
  start_time: '',
  end_time: '',
  is_published: false
})

const rules = {
  title: [{ required: true, message: '请输入考试标题', trigger: 'blur' }],
  duration: [{ required: true, message: '请输入考试时长', trigger: 'blur' }],
  pass_score: [{ required: true, message: '请输入及格线', trigger: 'blur' }]
}

function normalizeList(data) {
  if (Array.isArray(data)) return data
  return data?.results || []
}

function resetForm() {
  form.title = ''
  form.description = ''
  form.duration = 60
  form.pass_score = 60
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
  const now = Date.now()
  const startTime = form.start_time ? new Date(form.start_time).getTime() : null
  const endTime = form.end_time ? new Date(form.end_time).getTime() : null

  if (startTime && startTime <= now) {
    ElMessage.error('开始时间必须晚于当前时间')
    return false
  }

  if (endTime && endTime <= now) {
    ElMessage.error('截止时间必须晚于当前时间')
    return false
  }

  if (startTime && endTime && endTime <= startTime) {
    ElMessage.error('截止时间必须晚于开始时间')
    return false
  }

  return true
}

function openCreateDialog() {
  resetForm()
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
    ElMessage.error(getCommonErrorMessage(error, '考试信息加载失败'))
  } finally {
    loading.value = false
  }
}

async function handleCreateExam() {
  await formRef.value?.validate()
  if (!validateExamTime()) return

  submitting.value = true
  try {
    await createCourseExam(courseId.value, { ...form })
    ElMessage.success('考试已创建')
    dialogVisible.value = false
    loadPage()
  } catch (error) {
    ElMessage.error(getExamErrorMessage(error, '考试创建失败'))
  } finally {
    submitting.value = false
  }
}

async function togglePublish(row) {
  const nextPublished = !row.is_published
  await ElMessageBox.confirm(
    nextPublished ? '确认发布这场考试吗？发布后学生可见。' : '确认下架这场考试吗？下架后学生不可见。',
    nextPublished ? '发布考试' : '下架考试',
    {
      type: 'warning',
      confirmButtonText: nextPublished ? '发布' : '下架',
      cancelButtonText: '取消'
    }
  )

  publishingId.value = row.id
  try {
    await updateCourseExam(row.id, {
      is_published: nextPublished
    })
    ElMessage.success(nextPublished ? '考试已发布' : '考试已下架')
    await loadPage()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, nextPublished ? '考试发布失败' : '考试下架失败'))
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
