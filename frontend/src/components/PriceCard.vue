<template>
  <div class="price-card">
    <div class="price-header">
      <h3>实时碳汇价格</h3>
      <el-icon class="refresh-icon" @click="$emit('refresh')">
        <Refresh />
      </el-icon>
    </div>
    <div class="price-value">
      <span class="price">{{ price }} 元/吨</span>
      <span class="price-time">{{ timestamp }}</span>
    </div>
  </div>
</template>

<script>
import { Refresh } from '@element-plus/icons-vue'

export default {
  name: 'PriceCard',
  components: {
    Refresh
  },
  props: {
    price: {
      type: String,
      default: '--'
    },
    timestamp: {
      type: String,
      default: ''
    }
  },
  emits: ['refresh']
}
</script>

<style scoped>
.price-card {
  padding: 20px;
  border-bottom: 1px solid #e6e6e6;
}

.price-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.price-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.refresh-icon {
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.refresh-icon:hover {
  color: #409eff;
}

.price-value {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price {
  font-size: 24px;
  font-weight: bold;
  color: #67c23a;
}

.price-time {
  font-size: 12px;
  color: #999;
}
</style>
