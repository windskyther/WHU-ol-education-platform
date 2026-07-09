<template>
  <main class="page-shell">
    <AppNav>
      <template #actions>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">{{ t('teacher.courses.createBtn') }}</el-button>
      </template>
    </AppNav>

    <section class="manager-shell">
      <div class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">{{ t('teacher.courses.eyebrow') }}</p>
          <h1>Build the catalog.</h1>
          <p>{{ t('teacher.courses.description') }}</p>
        </div>
      </div>

      <section class="surface filter-panel">
        <div class="filter-row">
          <el-input v-model.trim="filters.keyword" clearable :placeholder="t('teacher.courses.searchPlaceholder')" @keyup.enter="loadCourses(1)" />
          <el-input v-model.trim="filters.category" clearable :placeholder="t('teacher.courses.categoryPlaceholder')" @keyup.enter="loadCourses(1)" />
          <el-select v-model="filters.is_published" clearable :placeholder="t('teacher.courses.publishStatusPlaceholder')">
            <el-option :label="t('teacher.courses.published')" value="true" />
            <el-option :label="t('teacher.courses.draft')" value="false" />
          </el-select>
          <el-button type="primary" :icon="Search" :loading="loading" @click="loadCourses(1)">{{ t('teacher.courses.filterBtn') }}</el-button>
        </div>
      </section>

      <section class="surface table-panel">
        <el-table v-loading="loading" :data="courses" row-key="id">
          <el-table-column :label="t('teacher.courses.colCourse')" min-width="260">
            <template #default="{ row }">
              <div class="course-cell">
                <strong>{{ row.title }}</strong>
                <span>{{ row.category || t('teacher.courses.uncategorized') }} · {{ levelText(row.level) }} · {{ t('teacher.courses.chapterCount', { n: row.chapter_count || 0 }) }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('teacher.courses.colStatus')" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_published ? 'success' : 'warning'" effect="light">
                {{ row.is_published ? t('teacher.courses.published') : t('teacher.courses.draft') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('teacher.courses.colUpdatedAt')" width="190">
            <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
          </el-table-column>
          <el-table-column :label="t('teacher.courses.colActions')" min-width="360" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button size="small" text :icon="View" @click="$router.push(`/courses/${row.id}`)">{{ t('teacher.courses.viewBtn') }}</el-button>
                <el-button size="small" text :icon="Edit" @click="openEditDialog(row)">{{ t('teacher.courses.editBtn') }}</el-button>
                <el-button size="small" text :icon="Collection" @click="$router.push(`/teacher/courses/${row.id}/chapters`)">{{ t('teacher.courses.chaptersBtn') }}</el-button>
                <el-button size="small" text :icon="Tickets" @click="$router.push(`/teacher/courses/${row.id}/exams`)">{{ t('teacher.courses.examsBtn') }}</el-button>
                <el-button size="small" plain :loading="publishingId === row.id" @click="togglePublish(row)">
                  {{ row.is_published ? t('teacher.courses.unpublishBtn') : t('teacher.courses.publishBtn') }}
                </el-button>
                <el-button size="small" type="danger" plain :icon="Delete" :loading="deletingId === row.id" @click="confirmDelete(row)">{{ t('teacher.courses.deleteBtn') }}</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="!loading && courses.length === 0" class="empty-state">{{ t('teacher.courses.emptyState') }}</div>
        <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadCourses" />
      </section>
    </section>

    <CourseFormDialog v-model="dialogVisible" :course="editingCourse" :submitting="submitting" @submit="handleSaveCourse" />
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Collection, Delete, Edit, Plus, Search, Tickets, View } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import AppNav from '../../components/AppNav.vue'
import CourseFormDialog from '../../components/CourseFormDialog.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { createCourse, deleteCourse, fetchCourses, publishCourse, updateCourse } from '../../api/course'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingCourse = ref(null)
const courses = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const publishingId = ref(null)
const deletingId = ref(null)

const filters = reactive({
  keyword: '',
  category: '',
  is_published: ''
})

function levelText(level) {
  const map = {
    beginner: t('teacher.courses.levelBeginner'),
    intermediate: t('teacher.courses.levelIntermediate'),
    advanced: t('teacher.courses.levelAdvanced')
  }
  return map[level] || t('teacher.courses.levelBeginner')
}

function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function buildParams(nextPage) {
  return {
    page: nextPage,
    page_size: pageSize.value,
    keyword: filters.keyword || undefined,
    category: filters.category || undefined,
    is_published: filters.is_published || undefined
  }
}

async function loadCourses(nextPage = page.value) {
  loading.value = true
  try {
    const data = await fetchCourses(buildParams(nextPage))
    courses.value = data?.results || []
    total.value = data?.count || courses.value.length
    page.value = data?.page || nextPage
    pageSize.value = data?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('teacher.courses.loadFailed')))
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  editingCourse.value = null
  dialogVisible.value = true
}

function openEditDialog(course) {
  editingCourse.value = course
  dialogVisible.value = true
}

async function handleSaveCourse(payload) {
  submitting.value = true
  try {
    if (editingCourse.value?.id) {
      await updateCourse(editingCourse.value.id, payload)
      ElMessage.success(t('teacher.courses.updated'))
    } else {
      await createCourse(payload)
      ElMessage.success(t('teacher.courses.created'))
    }
    dialogVisible.value = false
    loadCourses(editingCourse.value?.id ? page.value : 1)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('teacher.courses.saveFailed')))
  } finally {
    submitting.value = false
  }
}

async function togglePublish(course) {
  publishingId.value = course.id
  try {
    await publishCourse(course.id, !course.is_published)
    ElMessage.success(course.is_published ? t('teacher.courses.unpublishedMsg') : t('teacher.courses.publishedMsg'))
    loadCourses(page.value)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('teacher.courses.publishFailed')))
  } finally {
    publishingId.value = null
  }
}

async function confirmDelete(course) {
  await ElMessageBox.confirm(
    t('teacher.courses.confirmDeleteMsg', { name: course.title }),
    t('teacher.courses.confirmDeleteTitle'),
    {
      type: 'warning',
      confirmButtonText: t('teacher.courses.confirmDeleteBtn'),
      cancelButtonText: t('teacher.courses.confirmCancelBtn')
    }
  )

  deletingId.value = course.id
  try {
    await deleteCourse(course.id)
    ElMessage.success(t('teacher.courses.deleted'))
    loadCourses(page.value)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, t('teacher.courses.deleteFailed')))
  } finally {
    deletingId.value = null
  }
}

onMounted(() => {
  loadCourses(1)
})
</script>

<style scoped>
.manager-shell {
  margin: 64px auto 0;
}

.manager-heading {
  min-height: 360px;
  padding: 42px;
  display: grid;
  align-content: end;
}

.manager-heading h1,
.manager-heading p {
  color: var(--paper);
}

.manager-heading p:not(.eyebrow) {
  max-width: 720px;
  color: rgba(246, 241, 230, 0.72);
}

.filter-panel,
.table-panel {
  padding: 16px;
}

.filter-panel {
  margin-top: 18px;
}

.table-panel {
  margin-top: 16px;
}

.course-cell {
  display: grid;
  gap: 8px;
}

.course-cell strong {
  font-size: 22px;
  font-weight: 900;
}

.course-cell span {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}
</style>
