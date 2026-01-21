<template>
  <div class="control-panel">
    <el-button
      type="primary"
      :disabled="isCreating"
      @click="$emit('start-create')"
      class="action-btn"
    >
      <el-icon><Plus /></el-icon>
      {{ isCreating ? '正在创建' : '创建监测区' }}
    </el-button>

    <el-button
      v-if="isCreating"
      type="success"
      @click="$emit('finish-create')"
      class="action-btn"
    >
      <el-icon><Check /></el-icon>
      完成创建
    </el-button>

    <el-button
      v-if="isCreating"
      type="warning"
      @click="$emit('cancel-create')"
      class="action-btn"
    >
      <el-icon><Close /></el-icon>
      取消创建
    </el-button>
  </div>
</template>

<script>
import { Plus, Check, Close } from '@element-plus/icons-vue'

export default {
  name: 'ControlPanel',
  components: {
    Plus,
    Check,
    Close
  },
  props: {
    isCreating: {
      type: Boolean,
      default: false
    }
  },
  emits: ['start-create', 'finish-create', 'cancel-create']
}
</script>

<style scoped>
.control-panel {
  padding: 20px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-btn {
  width: 100%;
  margin-left: 0px;
}
</style>
