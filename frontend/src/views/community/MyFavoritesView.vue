<template>
  <section class="community-page">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="收藏的帖子" name="post" />
      <el-tab-pane label="收藏的资料" name="resource" />
    </el-tabs>

    <div v-loading="loading" class="post-list">
      <template v-if="activeTab === 'post'">
        <PostCard
          v-for="post in posts"
          :key="post.id"
          :post="post"
          @deleted="handlePostDeleted"
          @updated="handlePostUpdated"
        />
      </template>
      <template v-else>
        <ResourceCard
          v-for="resource in resources"
          :key="resource.id"
          :resource="resource"
          @deleted="handleResourceDeleted"
          @updated="handleResourceUpdated"
        />
      </template>
    </div>

    <div v-if="!loading && activeTab === 'post' && posts.length === 0" class="empty-state">
      还没有收藏的帖子，去论坛看看感兴趣的内容吧。
    </div>
    <div v-if="!loading && activeTab === 'resource' && resources.length === 0" class="empty-state">
      还没有收藏的资料，去资料推送看看吧。
    </div>

    <PaginationBar
      v-if="activeTab === 'post'"
      :total="postTotal"
      :page="postPage"
      :page-size="pageSize"
      @change="loadPosts"
    />
    <PaginationBar
      v-if="activeTab === 'resource'"
      :total="resourceTotal"
      :page="resourcePage"
      :page-size="pageSize"
      @change="loadResources"
    />
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PostCard from '../../components/community/PostCard.vue'
import ResourceCard from '../../components/community/ResourceCard.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { fetchMyFavorites } from '../../api/community'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const activeTab = ref('post')
const loading = ref(false)
const pageSize = ref(10)

const posts = ref([])
const postTotal = ref(0)
const postPage = ref(1)
const postsLoaded = ref(false)

const resources = ref([])
const resourceTotal = ref(0)
const resourcePage = ref(1)
const resourcesLoaded = ref(false)

async function loadPosts(nextPage = postPage.value) {
  loading.value = true
  try {
    const data = await fetchMyFavorites('post', { page: nextPage, page_size: pageSize.value })
    posts.value = data?.results || []
    postTotal.value = data?.count || posts.value.length
    postPage.value = data?.page || nextPage
    postsLoaded.value = true
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '收藏加载失败'))
  } finally {
    loading.value = false
  }
}

async function loadResources(nextPage = resourcePage.value) {
  loading.value = true
  try {
    const data = await fetchMyFavorites('resource', { page: nextPage, page_size: pageSize.value })
    resources.value = data?.results || []
    resourceTotal.value = data?.count || resources.value.length
    resourcePage.value = data?.page || nextPage
    resourcesLoaded.value = true
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '收藏加载失败'))
  } finally {
    loading.value = false
  }
}

function handleTabChange(name) {
  if (name === 'post' && !postsLoaded.value) {
    loadPosts(1)
  } else if (name === 'resource' && !resourcesLoaded.value) {
    loadResources(1)
  }
}

function handlePostDeleted(postId) {
  posts.value = posts.value.filter((item) => item.id !== postId)
  postTotal.value = Math.max(postTotal.value - 1, 0)
}

function handlePostUpdated(updated) {
  const index = posts.value.findIndex((item) => item.id === updated.id)
  if (index !== -1) posts.value[index] = { ...posts.value[index], ...updated }
}

function handleResourceDeleted(resourceId) {
  resources.value = resources.value.filter((item) => item.id !== resourceId)
  resourceTotal.value = Math.max(resourceTotal.value - 1, 0)
}

function handleResourceUpdated(updated) {
  const index = resources.value.findIndex((item) => item.id === updated.id)
  if (index !== -1) resources.value[index] = { ...resources.value[index], ...updated }
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

.post-list {
  display: grid;
  gap: 16px;
  min-height: 80px;
}
</style>
