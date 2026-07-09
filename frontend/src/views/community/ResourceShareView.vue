<template>
  <section class="community-page">
    <section class="surface post-form-panel">
      <h2>分享学习资料</h2>
      <el-form label-position="top" @submit.prevent>
        <el-form-item label="标题">
          <el-input v-model.trim="resourceForm.title" maxlength="128" show-word-limit placeholder="资料标题" />
        </el-form-item>
        <el-form-item label="说明（可选）">
          <el-input v-model.trim="resourceForm.description" type="textarea" :rows="3" maxlength="2000" show-word-limit placeholder="简单说明这份资料的内容" />
        </el-form-item>
        <el-form-item label="资料网址（可选，填写后卡片会显示 GO 按钮）">
          <el-input v-model.trim="resourceForm.url" placeholder="https://…" />
        </el-form-item>
        <el-form-item label="或上传文件（可选，与网址二选一）">
          <el-upload
            v-model:file-list="fileList"
            :limit="1"
            :auto-upload="false"
            :on-change="handleFileChange"
          >
            <el-button :icon="Paperclip">选择文件</el-button>
          </el-upload>
        </el-form-item>
        <div class="table-actions">
          <el-button type="primary" :icon="Upload" :loading="submitting" @click="submitResource">分享资料</el-button>
        </div>
      </el-form>
    </section>

    <section class="surface filter-panel">
      <div class="filter-row-simple">
        <el-input v-model.trim="keyword" clearable placeholder="搜索资料标题或说明" @keyup.enter="loadResources(1)" />
        <el-button type="primary" :icon="Search" :loading="loading" @click="loadResources(1)">搜索</el-button>
      </div>
    </section>

    <div v-loading="loading" class="post-list">
      <ResourceCard
        v-for="resource in resources"
        :key="resource.id"
        :resource="resource"
        @deleted="handleDeleted"
        @updated="handleUpdated"
      />
    </div>

    <div v-if="!loading && resources.length === 0" class="empty-state">还没有分享的资料，快来上传第一份吧。</div>

    <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadResources" />
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Paperclip, Search, Upload } from '@element-plus/icons-vue'
import ResourceCard from '../../components/community/ResourceCard.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { createResource, fetchResources } from '../../api/community'
import { getCommonErrorMessage } from '../../utils/errorMessage'

const loading = ref(false)
const submitting = ref(false)
const resources = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const fileList = ref([])
const selectedFile = ref(null)

const resourceForm = reactive({
  title: '',
  description: '',
  url: ''
})

function handleFileChange(uploadFile) {
  selectedFile.value = uploadFile.raw || null
}

async function loadResources(nextPage = page.value) {
  loading.value = true
  try {
    const data = await fetchResources({ page: nextPage, page_size: pageSize.value, keyword: keyword.value || undefined })
    resources.value = data?.results || []
    total.value = data?.count || resources.value.length
    page.value = data?.page || nextPage
    pageSize.value = data?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '资料加载失败'))
  } finally {
    loading.value = false
  }
}

function resetForm() {
  resourceForm.title = ''
  resourceForm.description = ''
  resourceForm.url = ''
  fileList.value = []
  selectedFile.value = null
}

function handleDeleted(resourceId) {
  resources.value = resources.value.filter((item) => item.id !== resourceId)
  total.value = Math.max(total.value - 1, 0)
}

function handleUpdated(updated) {
  const index = resources.value.findIndex((item) => item.id === updated.id)
  if (index !== -1) {
    resources.value[index] = { ...resources.value[index], ...updated }
  }
}

async function submitResource() {
  if (!resourceForm.title) {
    ElMessage.warning('请填写资料标题')
    return
  }
  if (!resourceForm.url && !selectedFile.value) {
    ElMessage.warning('请填写资料网址，或上传一个文件')
    return
  }
  submitting.value = true
  try {
    await createResource({
      title: resourceForm.title,
      description: resourceForm.description,
      url: resourceForm.url,
      file: selectedFile.value || undefined
    })
    ElMessage.success('资料分享成功')
    resetForm()
    await loadResources(1)
  } catch (error) {
    ElMessage.error(getCommonErrorMessage(error, '资料分享失败'))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadResources(1)
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
