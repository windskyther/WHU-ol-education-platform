<template>
  <section class="community-page">
    <section class="surface post-form-panel">
      <h2>发布新帖子</h2>
      <el-form label-position="top" @submit.prevent>
        <el-form-item label="标题">
          <el-input v-model.trim="postForm.title" maxlength="128" show-word-limit placeholder="给帖子起个标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model.trim="postForm.content" type="textarea" :rows="4" maxlength="4000" show-word-limit placeholder="分享你的想法、问题或经验…" />
        </el-form-item>
        <el-form-item label="附件（可选）">
          <el-upload
            v-model:file-list="fileList"
            multiple
            :auto-upload="false"
            :limit="5"
          >
            <el-button :icon="Paperclip">选择附件</el-button>
          </el-upload>
        </el-form-item>
        <div class="table-actions">
          <el-button type="primary" :icon="EditPen" :loading="submitting" @click="submitPost">发布帖子</el-button>
        </div>
      </el-form>
    </section>

    <section class="surface filter-panel">
      <div class="filter-row-simple">
        <el-input v-model.trim="keyword" clearable placeholder="搜索帖子标题或内容" @keyup.enter="loadPosts(1)" />
        <el-button type="primary" :icon="Search" :loading="loading" @click="loadPosts(1)">搜索</el-button>
      </div>
    </section>

    <div v-loading="loading" class="post-list">
      <PostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
        @deleted="handleDeleted"
        @updated="handleUpdated"
      />
    </div>

    <div v-if="!loading && posts.length === 0" class="empty-state">还没有帖子，来发布第一条吧。</div>

    <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadPosts" />
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { EditPen, Paperclip, Search } from '@element-plus/icons-vue'
import PostCard from '../../components/community/PostCard.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { createPost, fetchPosts, uploadPostAttachments } from '../../api/community'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const loading = ref(false)
const submitting = ref(false)
const posts = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const fileList = ref([])

const postForm = reactive({
  title: '',
  content: ''
})

async function loadPosts(nextPage = page.value) {
  loading.value = true
  try {
    const data = await fetchPosts({ page: nextPage, page_size: pageSize.value, keyword: keyword.value || undefined })
    posts.value = data?.results || []
    total.value = data?.count || posts.value.length
    page.value = data?.page || nextPage
    pageSize.value = data?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '帖子加载失败'))
  } finally {
    loading.value = false
  }
}

function resetForm() {
  postForm.title = ''
  postForm.content = ''
  fileList.value = []
}

function handleDeleted(postId) {
  posts.value = posts.value.filter((item) => item.id !== postId)
  total.value = Math.max(total.value - 1, 0)
}

function handleUpdated(updated) {
  const index = posts.value.findIndex((item) => item.id === updated.id)
  if (index !== -1) {
    posts.value[index] = { ...posts.value[index], ...updated }
  }
}

async function submitPost() {
  if (!postForm.title || !postForm.content) {
    ElMessage.warning('请填写帖子标题和内容')
    return
  }
  submitting.value = true
  try {
    const post = await createPost({ title: postForm.title, content: postForm.content })
    const files = fileList.value.map((item) => item.raw).filter(Boolean)
    if (files.length) {
      await uploadPostAttachments(post.id, files)
    }
    ElMessage.success('帖子发布成功')
    resetForm()
    await loadPosts(1)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '帖子发布失败'))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadPosts(1)
})
</script>

<style scoped>
.community-page {
  display: grid;
  gap: 22px;
}

.post-form-panel {
  display: grid;
  gap: 12px;
  padding: 24px;
}

.post-form-panel h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
}

.filter-panel {
  padding: 16px;
}

.filter-row-simple {
  display: flex;
  gap: 12px;
}

.filter-row-simple .el-input {
  flex: 1;
}

.post-list {
  display: grid;
  gap: 16px;
  min-height: 80px;
}

@media (max-width: 680px) {
  .filter-row-simple {
    flex-direction: column;
  }
}
</style>
