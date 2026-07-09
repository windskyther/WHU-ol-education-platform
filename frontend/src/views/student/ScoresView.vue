<template>
  <main class="page-shell scores-page">
    <AppNav />

    <section class="scores-workspace">
      <header class="manager-heading kinetic-panel">
        <div>
          <p class="eyebrow">Score ledger</p>
          <h1>成绩记录</h1>
          <p>查看已经提交的考试成绩，分数以后端判分结果为准。</p>
        </div>
      </header>

      <section class="surface filter-panel">
        <div class="filter-row score-filter-row">
          <el-input v-model.trim="courseId" clearable placeholder="课程 ID" @keyup.enter="loadScores(1)" />
          <el-button type="primary" :loading="loading" @click="loadScores(1)">筛选</el-button>
        </div>
      </section>

      <section class="surface table-panel">
        <el-table v-loading="loading" :data="scores" row-key="id">
          <el-table-column label="考试" min-width="220">
            <template #default="{ row }">
              <div class="score-cell">
                <strong>{{ row.exam_title || row.exam?.title || '未命名考试' }}</strong>
                <span>{{ row.course_title || row.course?.title || '课程未命名' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="分数" width="120">
            <template #default="{ row }">{{ row.total_score ?? row.score ?? '-' }}</template>
          </el-table-column>
          <el-table-column label="结果" width="120">
            <template #default="{ row }">
              <el-tag :type="isPassed(row) ? 'success' : 'warning'" effect="light">
                {{ isPassed(row) ? '已通过' : '未通过' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="提交时间" min-width="180">
            <template #default="{ row }">{{ formatTime(row.submitted_at || row.created_at) }}</template>
          </el-table-column>
        </el-table>

        <div v-if="!loading && scores.length === 0" class="empty-state">暂无成绩记录。</div>
        <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadScores" />
      </section>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppNav from '../../components/AppNav.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { fetchMyScores } from '../../api/exam'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const route = useRoute()
const loading = ref(false)
const scores = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const courseId = ref(route.query.course_id || '')

function normalizeList(data) {
  if (Array.isArray(data)) return data
  return data?.results || []
}

function isPassed(row) {
  if (row.passed !== undefined) return Boolean(row.passed)
  if (row.pass_score !== undefined && row.total_score !== undefined) return Number(row.total_score) >= Number(row.pass_score)
  return row.status === 'graded' || row.status === 'submitted'
}

function formatTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

async function loadScores(nextPage = page.value) {
  loading.value = true
  try {
    const data = await fetchMyScores({
      page: nextPage,
      page_size: pageSize.value,
      course_id: courseId.value || undefined
    })
    scores.value = normalizeList(data)
    total.value = data?.count || scores.value.length
    page.value = data?.page || nextPage
    pageSize.value = data?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '成绩加载失败'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadScores(1)
})
</script>

<style scoped>
.scores-workspace {
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
  max-width: 680px;
  color: rgba(246, 241, 230, 0.72);
}

.filter-panel,
.table-panel {
  margin-top: 18px;
  padding: 18px;
}

.score-filter-row {
  grid-template-columns: minmax(180px, 280px) auto;
  justify-content: start;
}

.score-cell {
  display: grid;
  gap: 6px;
}

.score-cell strong {
  font-weight: 900;
}

.score-cell span {
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

@media (max-width: 720px) {
  .score-filter-row {
    grid-template-columns: 1fr;
  }
}
</style>
