<template>
  <main class="page-shell">
    <AppNav>
      <template #actions>
        <el-button plain @click="$router.push(`/teacher/courses/${courseId}/exams`)">考试管理</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">创建章节</el-button>
      </template>
    </AppNav>

    <BreadcrumbNav :items="breadcrumbItems" />

    <section class="chapters-shell">
      <div class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">Chapter manager</p>
          <h1>{{ course?.title || 'Chapter index' }}</h1>
          <p>维护章节排序、简介、视频和资料。学生学习页会直接使用这些内容和资源。</p>
        </div>
      </div>

      <section v-loading="loading" class="surface chapter-panel">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Learning content</p>
            <h2>Content rail</h2>
          </div>
          <el-tag effect="light">{{ orderedChapters.length }} 章</el-tag>
        </div>

        <el-table :data="orderedChapters" row-key="id">
          <el-table-column label="排序" prop="order" width="90">
            <template #default="{ row }">{{ row.order ?? row.order_no }}</template>
          </el-table-column>
          <el-table-column label="章节" min-width="240">
            <template #default="{ row }">
              <div class="chapter-cell">
                <strong>{{ row.title }}</strong>
                <span>{{ row.description || '暂无章节简介' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="视频" min-width="220">
            <template #default="{ row }">
              <div class="asset-cell">
                <span>{{ row.video?.original_name || row.video?.file_name || (row.video || row.video_url ? '已上传视频' : '未上传') }}</span>
                <FileUpload
                  label="上传视频"
                  hint="mp4/webm/mov，200 MB"
                  accept=".mp4,.webm,.mov"
                  :allowed-extensions="['.mp4', '.webm', '.mov']"
                  :max-size-mb="200"
                  :upload-fn="(file) => uploadChapterVideo(row.id, file)"
                  @uploaded="loadChapters"
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="资料" min-width="240">
            <template #default="{ row }">
              <div class="asset-cell">
                <span>{{ row.material?.original_name || row.material?.file_name || (row.material || row.material_url ? '已上传资料' : '未上传') }}</span>
                <FileUpload
                  label="上传资料"
                  hint="pdf/doc/ppt/zip，20 MB"
                  accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.zip"
                  :allowed-extensions="materialExtensions"
                  :max-size-mb="20"
                  :upload-fn="(file) => uploadChapterMaterial(row.id, file)"
                  @uploaded="loadChapters"
                />
              </div>
            </template>
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

        <div v-if="!loading && orderedChapters.length === 0" class="empty-state">暂无章节，先创建第一章。</div>
      </section>
    </section>

    <ChapterFormDialog
      v-model="dialogVisible"
      :chapter="editingChapter"
      :next-order="nextOrder"
      :submitting="submitting"
      @submit="handleSaveChapter"
    />
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus } from '@element-plus/icons-vue'
import AppNav from '../../components/AppNav.vue'
import BreadcrumbNav from '../../components/BreadcrumbNav.vue'
import ChapterFormDialog from '../../components/ChapterFormDialog.vue'
import FileUpload from '../../components/FileUpload.vue'
import {
  createChapter,
  deleteChapter,
  fetchChapters,
  fetchCourseDetail,
  updateChapter,
  uploadChapterMaterial,
  uploadChapterVideo
} from '../../api/course'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const courseId = computed(() => route.params.id)
const course = ref(null)
const chapters = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingChapter = ref(null)
const submitting = ref(false)
const deletingId = ref(null)

const materialExtensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.zip']
const orderedChapters = computed(() => [...chapters.value].sort((a, b) => chapterOrder(a) - chapterOrder(b)))
const nextOrder = computed(() => {
  const maxOrder = orderedChapters.value.reduce((max, chapter) => Math.max(max, chapterOrder(chapter)), 0)
  return maxOrder + 1
})

const breadcrumbItems = computed(() => [
  { label: '课程管理', to: '/teacher/courses' },
  { label: course.value?.title || '课程', to: `/courses/${courseId.value}` },
  { label: '章节管理' }
])

function chapterOrder(chapter) {
  return chapter.order ?? chapter.order_no ?? 0
}

async function loadCourse() {
  course.value = await fetchCourseDetail(courseId.value)
}

async function loadChapters() {
  const data = await fetchChapters(courseId.value)
  chapters.value = Array.isArray(data) ? data : data?.results || []
}

async function loadPage() {
  loading.value = true
  try {
    await Promise.all([loadCourse(), loadChapters()])
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '章节信息加载失败'))
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  editingChapter.value = null
  dialogVisible.value = true
}

function openEditDialog(chapter) {
  editingChapter.value = chapter
  dialogVisible.value = true
}

async function handleSaveChapter(payload) {
  submitting.value = true
  try {
    if (editingChapter.value?.id) {
      await updateChapter(editingChapter.value.id, payload)
      ElMessage.success('章节已更新')
    } else {
      await createChapter(courseId.value, payload)
      ElMessage.success('章节已创建')
    }
    dialogVisible.value = false
    loadChapters()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '章节保存失败'))
  } finally {
    submitting.value = false
  }
}

async function confirmDelete(chapter) {
  await ElMessageBox.confirm(`确认删除章节“${chapter.title}”吗？`, '删除章节', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })

  deletingId.value = chapter.id
  try {
    await deleteChapter(chapter.id)
    ElMessage.success('章节已删除')
    loadChapters()
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '章节删除失败'))
  } finally {
    deletingId.value = null
  }
}

onMounted(() => {
  loadPage()
})
</script>

<style scoped>
.chapters-shell {
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
  max-width: 720px;
  color: rgba(246, 241, 230, 0.72);
}

.chapter-panel {
  margin-top: 18px;
  padding: 18px;
}

.panel-title {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.panel-title h2 {
  margin: 0;
  font-size: clamp(38px, 5vw, 72px);
  font-weight: 900;
  line-height: 0.85;
  letter-spacing: -0.07em;
}

.chapter-cell,
.asset-cell {
  display: grid;
  gap: 8px;
}

.chapter-cell strong {
  font-size: 22px;
  font-weight: 900;
}

.chapter-cell span,
.asset-cell span {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}
</style>
