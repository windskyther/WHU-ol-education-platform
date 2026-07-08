<template>
  <el-dialog v-model="visible" :title="course?.id ? '编辑课程' : '创建课程'" width="640px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="课程标题" prop="title">
        <el-input v-model.trim="form.title" placeholder="例如：Python 入门实践" />
      </el-form-item>
      <el-form-item label="课程简介" prop="description">
        <el-input v-model.trim="form.description" type="textarea" :rows="4" placeholder="说明课程目标、适合对象和学习内容" />
      </el-form-item>
      <div class="form-grid">
        <el-form-item label="分类" prop="category">
          <el-input v-model.trim="form.category" placeholder="programming" />
        </el-form-item>
        <el-form-item label="难度" prop="level">
          <el-select v-model="form.level" placeholder="请选择难度">
            <el-option label="初级" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
          </el-select>
        </el-form-item>
      </div>
      <el-form-item label="课程封面">
        <input ref="coverInputRef" class="cover-input" type="file" accept=".jpg,.jpeg,.png,.webp" @change="handleCoverChange" />
        <div class="cover-row">
          <el-button :icon="Picture" @click="coverInputRef?.click()">选择封面</el-button>
          <span class="muted">{{ coverName || '支持 jpg、jpeg、png、webp，最大 5 MB' }}</span>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'

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

const rules = {
  title: [{ required: true, message: '请输入课程标题', trigger: 'blur' }],
  level: [{ required: true, message: '请选择难度', trigger: 'change' }]
}

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
    ElMessage.error('封面仅支持 jpg、jpeg、png、webp')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('封面不能超过 5 MB')
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
