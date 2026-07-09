<template>
  <section class="community-page">
    <section class="surface post-form-panel">
      <h2>{{ t('community.resource.title') }}</h2>
      <el-form label-position="top" @submit.prevent>
        <el-form-item :label="t('community.resource.fieldTitle')">
          <el-input v-model.trim="resourceForm.title" maxlength="128" show-word-limit :placeholder="t('community.resource.titlePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('community.resource.fieldCategory')">
          <el-select v-model="resourceForm.category" :placeholder="t('community.resource.categoryPlaceholder')" clearable style="width: 240px">
            <el-option v-for="item in categories" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('community.resource.fieldDesc')">
          <el-input v-model.trim="resourceForm.description" type="textarea" :rows="3" maxlength="2000" show-word-limit :placeholder="t('community.resource.descPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('community.resource.fieldUrl')">
          <el-input v-model.trim="resourceForm.url" :placeholder="t('community.resource.urlPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('community.resource.fieldFile')">
          <el-upload
            v-model:file-list="fileList"
            :limit="1"
            :auto-upload="false"
            :on-change="handleFileChange"
          >
            <el-button :icon="Paperclip">{{ t('community.resource.selectFile') }}</el-button>
          </el-upload>
        </el-form-item>
        <div class="table-actions">
          <el-button type="primary" :icon="Upload" :loading="submitting" @click="submitResource">{{ t('community.resource.submit') }}</el-button>
        </div>
      </el-form>
    </section>

    <section class="surface filter-panel">
      <div class="filter-row-simple">
        <el-input v-model.trim="keyword" clearable :placeholder="t('community.resource.searchPlaceholder')" @keyup.enter="loadResources(1)" />
        <el-button type="primary" :icon="Search" :loading="loading" @click="loadResources(1)">{{ t('community.resource.search') }}</el-button>
      </div>
    </section>

    <div class="community-layout">
      <aside class="community-sidebar surface">
        <h4>{{ t('community.category.label') }}</h4>
        <CategoryNav v-model="activeCategory" :categories="categories" @change="handleCategoryChange" />
      </aside>

      <div class="community-main">
        <div v-loading="loading" class="post-grid">
          <ResourceCard
            v-for="resource in resources"
            :key="resource.id"
            :resource="resource"
            @deleted="handleDeleted"
            @updated="handleUpdated"
          />
        </div>

        <div v-if="!loading && resources.length === 0" class="empty-state">{{ t('community.resource.emptyState') }}</div>

        <PaginationBar :total="total" :page="page" :page-size="pageSize" @change="loadResources" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { Paperclip, Search, Upload } from '@element-plus/icons-vue'
import ResourceCard from '../../components/community/ResourceCard.vue'
import CategoryNav from '../../components/community/CategoryNav.vue'
import PaginationBar from '../../components/PaginationBar.vue'
import { createResource, fetchCategories, fetchResources } from '../../api/community'
import { getCommunityErrorMessage } from '../../utils/errorMessage'
import { normalizeUrl } from '../../utils/url'

const { t } = useI18n()

const loading = ref(false)
const submitting = ref(false)
const resources = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const fileList = ref([])
const selectedFile = ref(null)
const categories = ref([])
const activeCategory = ref('')

const resourceForm = reactive({
  title: '',
  description: '',
  url: '',
  category: ''
})

function handleFileChange(uploadFile) {
  selectedFile.value = uploadFile.raw || null
}

async function loadCategories() {
  try {
    const data = await fetchCategories('resource')
    categories.value = data || []
  } catch (error) {
    categories.value = []
  }
}

async function loadResources(nextPage = page.value) {
  loading.value = true
  try {
    const data = await fetchResources({
      page: nextPage,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      category: activeCategory.value || undefined
    })
    resources.value = data?.results || []
    total.value = data?.count || resources.value.length
    page.value = data?.page || nextPage
    pageSize.value = data?.page_size || pageSize.value
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.resource.loadFailed')))
  } finally {
    loading.value = false
  }
}

function handleCategoryChange() {
  loadResources(1)
}

function resetForm() {
  resourceForm.title = ''
  resourceForm.description = ''
  resourceForm.url = ''
  resourceForm.category = ''
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
    ElMessage.warning(t('community.resource.titleRequired'))
    return
  }
  if (!resourceForm.url && !selectedFile.value) {
    ElMessage.warning(t('community.resource.urlOrFileRequired'))
    return
  }
  submitting.value = true
  try {
    await createResource({
      title: resourceForm.title,
      description: resourceForm.description,
      url: resourceForm.url ? normalizeUrl(resourceForm.url) : '',
      category: resourceForm.category,
      file: selectedFile.value || undefined
    })
    ElMessage.success(t('community.resource.submitSuccess'))
    resetForm()
    await loadResources(1)
  } catch (error) {
    ElMessage.error(getCommunityErrorMessage(error, t('community.resource.submitFailed')))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadCategories()
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

