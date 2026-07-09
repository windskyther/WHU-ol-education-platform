<template>
  <nav class="category-nav">
    <button
      class="category-item"
      :class="{ active: modelValue === '' }"
      @click="select('')"
    >
      {{ t('community.category.all') }}
    </button>
    <button
      v-for="item in categories"
      :key="item.value"
      class="category-item"
      :class="{ active: modelValue === item.value }"
      @click="select(item.value)"
    >
      {{ item.label }}
    </button>
  </nav>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  categories: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

function select(value) {
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style scoped>
.category-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.category-item {
  border: none;
  background: transparent;
  text-align: left;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--ink-700, #3a4a40);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.category-item:hover {
  background: var(--green-100, #e8f6ee);
}

.category-item.active {
  background: var(--green-500, #5ca982);
  color: #fff;
  font-weight: 700;
}

@media (max-width: 860px) {
  .category-nav {
    flex-direction: row;
    flex-wrap: nowrap;
    overflow-x: auto;
    gap: 8px;
    padding-bottom: 4px;
  }

  .category-item {
    flex-shrink: 0;
  }
}
</style>
