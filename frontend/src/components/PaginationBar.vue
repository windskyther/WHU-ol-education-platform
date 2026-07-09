<template>
  <div v-if="total > 0" class="pagination-bar">
    <span>共 {{ total }} 条</span>
    <el-pagination
      background
      layout="prev, pager, next"
      :current-page="page"
      :page-size="pageSize"
      :total="total"
      @current-change="$emit('change', $event)"
    />
  </div>
</template>

<script setup>
defineProps({
  total: {
    type: Number,
    default: 0
  },
  page: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  }
})

defineEmits(['change'])
</script>

<style scoped>
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 22px;
  color: var(--slate-500);
  font-weight: 700;
}

@media (max-width: 680px) {
  .pagination-bar {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
