<template>
  <main class="page-shell">
    <AppNav>
      <template v-if="userStore.role === 'teacher' || userStore.role === 'admin'" #actions>
        <el-button type="primary" @click="$router.push('/teacher/courses')">课程管理</el-button>
      </template>
    </AppNav>

    <section class="course-list-shell">
      <header class="list-heading">
        <div>
          <p class="eyebrow">Course catalog</p>
          <h1>Pick your next project.</h1>
        </div>
        <p>已发布课程以项目卡片的方式排列。筛选分类、难度和关键词，然后进入详情页开始学习。</p>
      </header>

      <section class="surface filter-panel">
        <div class="filter-row">
          <el-input v-model.trim="filters.keyword" clearable placeholder="搜索课程标题" @keyup.enter="loadCourses(1)" />
          <el-input v-model.trim="filters.category" clearable placeholder="分类，例如 programming" @keyup.enter="loadCourses(1)" />
          <el-select v-model="filters.level" clearable placeholder="难度">
            <el-option label="初级" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
          </el-select>
          <el-button type="primary" :icon="Search" :loading="loading" @click="loadCourses(1)">筛选</el-button>
        </div>
      </section>

      <div v-loading="loading" class="course-grid">
        <CourseCard v-for="course in courses" :key="course.id" :course="course" />
      </div>

      <div v-if="!loading && courses.length === 0" class="empty-state">暂无匹配课程，换个关键词试试。</div>

      <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadCourses" />
    </section>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import AppNav from '../../components/AppNav.vue'
import CourseCard from '../../components/CourseCard.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { fetchCourses } from '../../api/course'
import { useUserStore } from '../../stores/user'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const userStore = useUserStore()
const loading = ref(false)
const courses = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  category: '',
  level: ''
})

function buildParams(nextPage) {
  return {
    page: nextPage,
    page_size: pageSize.value,
    keyword: filters.keyword || undefined,
    category: filters.category || undefined,
    level: filters.level || undefined
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
    ElMessage.error(getCommonErrorMessage(error, '课程列表加载失败'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCourses(1)
})
</script>

<style scoped>
.course-list-shell {
  margin: 64px auto 0;
}

.list-heading {
  display: grid;
  grid-template-columns: minmax(0, 0.66fr) minmax(280px, 0.34fr);
  gap: 36px;
  align-items: end;
  margin-bottom: 26px;
}

.filter-panel {
  padding: 16px;
}

.course-grid {
  display: grid;
  gap: 18px;
  min-height: 220px;
  margin-top: 22px;
}

@media (max-width: 960px) {
  .list-heading {
    grid-template-columns: 1fr;
  }
}
</style>
