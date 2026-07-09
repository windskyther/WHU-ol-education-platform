<template>
  <el-dialog v-model="visible" :title="course?.id ? t('course.form.editTitle') : t('course.form.createTitle')" width="640px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item :label="t('course.form.titleLabel')" prop="title">
        <el-input v-model.trim="form.title" :placeholder="t('course.form.titlePlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('course.form.descriptionLabel')" prop="description">
        <el-input v-model.trim="form.description" type="textarea" :rows="4" :placeholder="t('course.form.descriptionPlaceholder')" />
      </el-form-item>
      <div class="form-grid">
        <el-form-item :label="t('course.form.categoryLabel')" prop="category">
          <el-input v-model.trim="form.category" placeholder="programming" />
        </el-form-item>
        <el-form-item :label="t('course.form.levelLabel')" prop="level">
          <el-select v-model="form.level" :placeholder="t('course.form.levelPlaceholder')">
            <el-option v-for="opt in levelOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
      </div>
      <el-form-item :label="t('course.form.coverLabel')">
        <input ref="coverInputRef" class="cover-input" type="file" accept=".jpg,.jpeg,.png,.webp" @change="handleCoverChange" />
        <div class="cover-row">
          <el-button :icon="Picture" @click="coverInputRef?.click()">{{ t('course.form.selectCover') }}</el-button>
          <span class="muted">{{ coverName || t('course.form.coverHint') }}</span>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">{{ t('common.save') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  course: {
    type: Object,
    default: null
  },
  submitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formRef = ref()
const coverInputRef = ref()
const coverFile = ref(null)
const coverName = ref('')

const form = reactive({
  title: '',
  description: '',
  category: '',
  level: 'beginner'
})

const rules = computed(() => ({
  title: [{ required: true, message: t('course.form.titleRequired'), trigger: 'blur' }],
  level: [{ required: true, message: t('course.form.levelRequired'), trigger: 'change' }]
}))

const levelOptions = computed(() => [
  { label: t('course.level.beginner'), value: 'beginner' },
  { label: t('course.level.intermediate'), value: 'intermediate' },
  { label: t('course.level.advanced'), value: 'advanced' }
])

watch(
  () => [props.modelValue, props.course],
  () => {
    if (!props.modelValue) return
    form.title = props.course?.title || ''
    form.description = props.course?.description || ''
    form.category = props.course?.category || ''
    form.level = props.course?.level || 'beginner'
    coverFile.value = null
    coverName.value = ''
  },
  { immediate: true }
)

function handleCoverChange(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase()
  if (!['.jpg', '.jpeg', '.png', '.webp'].includes(extension)) {
    ElMessage.error(t('course.form.coverTypeError'))
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error(t('course.form.coverSizeError'))
    return
  }
  coverFile.value = file
  coverName.value = file.name
}

async function handleSubmit() {
  await formRef.value.validate()
  const payload = { ...form }

  if (coverFile.value) {
    const formData = new FormData()
    Object.entries(payload).forEach(([key, value]) => {
      if (value !== undefined && value !== null) formData.append(key, value)
    })
    formData.append('cover', coverFile.value)
    emit('submit', formData)
    return
  }

  emit('submit', payload)
}
</script>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: 1fr 180px;
  gap: 12px;
}

.cover-input {
  display: none;
}

.cover-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
