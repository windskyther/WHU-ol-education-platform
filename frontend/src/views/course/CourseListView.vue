<template>
  <main class="page-shell">
    <nav class="app-nav">
      <RouterLink class="brand-link" to="/">
        <span class="brand-mark">WHU</span>
        <span>在线教育平台</span>
      </RouterLink>
      <div class="nav-actions">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink v-if="userStore.role === 'student'" to="/student/courses">我的课程</RouterLink>
        <RouterLink v-if="!userStore.isLoggedIn" to="/login">登录</RouterLink>
        <el-button v-if="userStore.role === 'teacher' || userStore.role === 'admin'" type="primary" @click="$router.push('/teacher/courses')">
          管理课程
        </el-button>
      </div>
    </nav>

    <section class="course-list-shell">
      <div class="list-heading">
        <div>
          <p class="eyebrow">Course catalog</p>
          <h1>找到下一门想完成的课</h1>
        </div>
        <p>筛选已发布课程，查看难度、分类和章节数量。学生加入后即可进入学习页并记录进度。</p>
      </div>

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
import { RouterLink } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
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
  max-width: 1180px;
  margin: 54px auto 0;
}

.list-heading {
  display: grid;
  grid-template-columns: minmax(0, 0.72fr) minmax(280px, 0.48fr);
  gap: 28px;
  align-items: end;
  margin-bottom: 22px;
}

.list-heading h1 {
  margin: 0;
  font-size: clamp(38px, 5vw, 54px);
  line-height: 1.06;
}

.list-heading p:last-child {
  margin: 0;
  color: var(--slate-600);
  line-height: 1.75;
}

.filter-panel {
  padding: 16px;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  min-height: 180px;
  margin-top: 18px;
}

@media (max-width: 900px) {
  .list-heading,
  .course-grid {
    grid-template-columns: 1fr;
  }
}
</style>
