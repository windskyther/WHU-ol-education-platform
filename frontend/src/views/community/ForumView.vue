<template>
  <section class="community-page">
    <section class="surface post-form-panel">
      <h2>{{ t('community.forum.newPostTitle') }}</h2>
      <el-form label-position="top" @submit.prevent>
        <el-form-item :label="t('community.forum.fieldTitle')">
          <el-input v-model.trim="postForm.title" maxlength="128" show-word-limit :placeholder="t('community.forum.titlePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('community.forum.fieldCategory')">
          <el-select v-model="postForm.category" :placeholder="t('community.forum.categoryPlaceholder')" clearable style="width: 240px">
            <el-option v-for="item in categories" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('community.forum.fieldContent')">
          <el-input v-model.trim="postForm.content" type="textarea" :rows="4" maxlength="4000" show-word-limit :placeholder="t('community.forum.contentPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('community.forum.fieldAttachment')">
          <el-upload
            v-model:file-list="fileList"
            multiple
            :auto-upload="false"
            :limit="5"
          >
            <el-button :icon="Paperclip">{{ t('community.forum.selectAttachment') }}</el-button>
          </el-upload>
        </el-form-item>
        <div class="table-actions">
          <el-button type="primary" :icon="EditPen" :loading="submitting" @click="submitPost">{{ t('community.forum.submitPost') }}</el-button>
        </div>
      </el-form>
    </section>

    <section class="surface filter-panel">
      <div class="filter-row-simple">
        <el-input v-model.trim="keyword" clearable :placeholder="t('community.forum.searchPlaceholder')" @keyup.enter="loadPosts(1)" />
        <el-button type="primary" :icon="Search" :loading="loading" @click="loadPosts(1)">{{ t('community.forum.search') }}</el-button>
      </div>
    </section>

    <div class="community-layout">
      <aside class="community-sidebar surface">
        <h4>{{ t('community.category.label') }}</h4>
        <CategoryNav v-model="activeCategory" :categories="categories" @change="handleCategoryChange" />
      </aside>

      <div class="community-main">
        <div v-loading="loading" class="post-grid">
          <PostCard
            v-for="post in posts"
            :key="post.id"
            :post="post"
            @deleted="handleDeleted"
            @updated="handleUpdated"
          />
        </div>

        <div v-if="!loading && posts.length === 0" class="empty-state">{{ t('community.forum.emptyState') }}</div>

        <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadPosts" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { EditPen, Paperclip, Search } from '@element-plus/icons-vue'
import PostCard from '../../components/community/PostCard.vue'
import CategoryNav from '../../components/community/CategoryNav.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { createPost, fetchCategories, fetchPosts, uploadPostAttachments } from '../../api/community'
import { getCommunityErrorMessage } from '../../utils/errorMessage'

const { t } = useI18n()

const loading = ref(false)
const submitting = ref(false)
const posts = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const fileList = ref([])
const categories = ref([])
const activeCategory = ref('')

const postForm = reactive({
  title: '',
  content: '',
  category: ''
})

async function loadCategories() {
  try {
    const data = await fetchCategories('post')
    categories.value = data || []
  } catch (error) {
    categories.value = []
  }
}

async function loadPosts(nextPage = page.value) {
  loading.value = true
  try {
    const data = await fetchPosts({
      page: nextPage,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      category: activeCategory.value || undefined
    })
    posts.value = data?.results || []
    total.value = data?.count || posts.value.length
    page.value = data?.page || nextPage
    pageSize.value = data?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.forum.loadFailed')))
  } finally {
    loading.value = false
  }
}

function handleCategoryChange() {
  loadPosts(1)
}

function resetForm() {
  postForm.title = ''
  postForm.content = ''
  postForm.category = ''
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
    ElMessage.warning(t('community.forum.requiredFields'))
    return
  }
  submitting.value = true
  try {
    const post = await createPost({ title: postForm.title, content: postForm.content, category: postForm.category })
    const files = fileList.value.map((item) => item.raw).filter(Boolean)
    if (files.length) {
      await uploadPostAttachments(post.id, files)
    }
    ElMessage.success(t('community.forum.submitSuccess'))
    resetForm()
    await loadPosts(1)
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.forum.submitFailed')))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadCategories()
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

.community-layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 20px;
  align-items: start;
}

.community-sidebar {
  padding: 16px;
  position: sticky;
  top: 16px;
}

.community-sidebar h4 {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--ink-500, #6b7a70);
}

.community-main {
  display: grid;
  gap: 16px;
  min-width: 0;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  min-height: 80px;
}

@media (max-width: 860px) {
  .community-layout {
    grid-template-columns: 1fr;
  }

  .community-sidebar {
    position: static;
  }

  .post-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .filter-row-simple {
    flex-direction: column;
  }
}
</style>

