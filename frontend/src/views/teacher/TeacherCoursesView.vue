<template>
  <main class="page-shell">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink to="/teacher/dashboard">教师首页</RouterLink>
        <RouterLink to="/courses">公开课程</RouterLink>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">创建课程</el-button>
      </div>
    </nav>

    <section class="manager-shell">
      <div class="manager-heading">
        <div>
          <p class="eyebrow">Teacher course manager</p>
          <h1>课程管理</h1>
        </div>
        <p>维护自己的课程草稿和发布状态。课程发布后，学生和游客才能在公开列表中看到。</p>
      </div>

      <section class="surface filter-panel">
        <div class="filter-row">
          <el-input v-model.trim="filters.keyword" clearable placeholder="搜索课程标题" @keyup.enter="loadCourses(1)" />
          <el-input v-model.trim="filters.category" clearable placeholder="分类" @keyup.enter="loadCourses(1)" />
          <el-select v-model="filters.is_published" clearable placeholder="发布状态">
            <el-option label="已发布" value="true" />
            <el-option label="草稿" value="false" />
          </el-select>
          <el-button type="primary" :icon="Search" :loading="loading" @click="loadCourses(1)">筛选</el-button>
        </div>
      </section>

      <section class="surface table-panel">
        <el-table v-loading="loading" :data="courses" row-key="id">
          <el-table-column label="课程" min-width="260">
            <template #default="{ row }">
              <div class="course-cell">
                <strong>{{ row.title }}</strong>
                <span>{{ row.category || '未分类' }} · {{ levelText(row.level) }} · {{ row.chapter_count || 0 }} 章</span>
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
          <el-table-column label="更新时间" width="190">
            <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" min-width="360" fixed="right">
            <template #default="{ row }">
              <div class="table-actions">
                <el-button size="small" text :icon="View" @click="$router.push(`/courses/${row.id}`)">查看</el-button>
                <el-button size="small" text :icon="Edit" @click="openEditDialog(row)">编辑</el-button>
                <el-button size="small" text :icon="Collection" @click="$router.push(`/teacher/courses/${row.id}/chapters`)">章节</el-button>
                <el-button size="small" plain :loading="publishingId === row.id" @click="togglePublish(row)">
                  {{ row.is_published ? '下架' : '发布' }}
                </el-button>
                <el-button size="small" type="danger" plain :icon="Delete" :loading="deletingId === row.id" @click="confirmDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="!loading && courses.length === 0" class="empty-state">暂无课程，先创建一门课程。</div>
        <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadCourses" />
      </section>
    </section>

    <CourseFormDialog v-model="dialogVisible" :course="editingCourse" :submitting="submitting" @submit="handleSaveCourse" />
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Collection, Delete, Edit, Plus, Search, View } from '@element-plus/icons-vue'
import CourseFormDialog from '../../components/CourseFormDialog.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { createCourse, deleteCourse, fetchCourses, publishCourse, updateCourse } from '../../api/course'
import { getCommonErrorMessage } from '../../utils/errorMessage'

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

const levelMap = {
  beginner: '初级',
  intermediate: '中级',
  advanced: '高级'
}

function levelText(level) {
  return levelMap[level] || '初级'
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
    ElMessage.error(getCommonErrorMessage(error, '课程加载失败'))
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
      ElMessage.success('课程已更新')
    } else {
      await createCourse(payload)
      ElMessage.success('课程已创建')
    }
    dialogVisible.value = false
    loadCourses(editingCourse.value?.id ? page.value : 1)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '课程保存失败'))
  } finally {
    submitting.value = false
  }
}

async function togglePublish(course) {
  publishingId.value = course.id
  try {
    await publishCourse(course.id, !course.is_published)
    ElMessage.success(course.is_published ? '课程已下架' : '课程已发布')
    loadCourses(page.value)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '发布状态更新失败'))
  } finally {
    publishingId.value = null
  }
}

async function confirmDelete(course) {
  await ElMessageBox.confirm(`确认删除课程「${course.title}」吗？该操作会让课程不再出现在列表中。`, '删除课程', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })

  deletingId.value = course.id
  try {
    await deleteCourse(course.id)
    ElMessage.success('课程已删除')
    loadCourses(page.value)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '课程删除失败'))
  } finally {
    deletingId.value = null
  }
}

onMounted(() => {
  loadCourses(1)
})
</script>

<style scoped>
.nav-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  align-items: center;
}

.nav-actions a {
  color: var(--ink-900);
  font-weight: 700;
  text-decoration: none;
}

.manager-shell {
  max-width: 1180px;
  margin: 48px auto 0;
}

.manager-heading {
  display: grid;
  grid-template-columns: minmax(0, 0.72fr) minmax(280px, 0.48fr);
  gap: 28px;
  align-items: end;
  margin-bottom: 22px;
}

.manager-heading h1 {
  margin: 0;
  font-size: clamp(36px, 5vw, 46px);
  line-height: 1.1;
}

.manager-heading p:last-child {
  margin: 0;
  color: var(--slate-600);
  line-height: 1.75;
}

.filter-panel,
.table-panel {
  padding: 16px;
}

.table-panel {
  margin-top: 16px;
}

.course-cell {
  display: grid;
  gap: 6px;
}

.course-cell span {
  color: var(--slate-500);
  font-size: 13px;
}

.table-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

@media (max-width: 900px) {
  .manager-heading {
    grid-template-columns: 1fr;
  }
}
</style>
