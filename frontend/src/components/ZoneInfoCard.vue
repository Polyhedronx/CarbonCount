<template>
  <div class="info-card">
    <h3>基本信息</h3>
    <div class="info-grid">
      <div class="info-item">
        <span class="label">状态:</span>
        <span class="value">
          <el-tag :type="zone.status === 'active' ? 'success' : 'info'">
            {{ zone.status === 'active' ? '监测中' : '已停止' }}
          </el-tag>
        </span>
      </div>
      <div class="info-item">
        <span class="label">面积:</span>
        <span class="value">{{ formatArea(zone.area) }}</span>
      </div>
      <div class="info-item">
        <span class="label">总碳汇量:</span>
        <span class="value">{{ formatCarbon(zone.total_carbon_absorption) }} 吨</span>
      </div>
      <div class="info-item">
        <span class="label">当前NDVI:</span>
        <span class="value">{{ formatNDVI(zone.current_ndvi) }}</span>
      </div>
      <div class="info-item">
        <span class="label">创建时间:</span>
        <span class="value">{{ formatDate(zone.created_at) }}</span>
      </div>
      <div class="info-item">
        <span class="label">监测数据点数:</span>
        <span class="value">{{ zone.measurements_count || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatArea, formatDate } from '../utils/formatters'

const props = defineProps({
  zone: {
    type: Object,
    required: true
  }
})

const formatCarbon = (value) => {
  return value ? value.toFixed(3) : '0'
}

const formatNDVI = (value) => {
  return value ? value.toFixed(4) : 'N/A'
}
</script>

<style scoped>
.info-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-card h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
  font-weight: 500;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  color: #666;
  font-size: 14px;
}

.value {
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
