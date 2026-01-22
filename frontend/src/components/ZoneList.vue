<template>
  <div class="zones-list">
    <h3>监测区列表</h3>
    <div v-if="loading" class="loading">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      加载中...
    </div>
    <div v-else-if="zones.length === 0" class="empty-state">
      暂无监测区
    </div>
    <div v-else class="zones-container">
      <div
        v-for="zone in zones"
        :key="zone.id"
        class="zone-item"
        @click="handleItemClick(zone, $event)"
      >
        <div class="zone-header">
          <h4>{{ zone.name }}</h4>
          <div class="zone-status" :class="zone.status">
            {{ zone.status === 'active' ? '监测中' : '已停止' }}
          </div>
        </div>
        <div class="zone-info">
          <div class="info-item">
            <span class="label">面积:</span>
            <span class="value">{{ formatArea(zone.area) }}</span>
          </div>
          <div class="info-item">
            <span class="label">总碳汇:</span>
            <span class="value">{{ zone.total_carbon_absorption?.toFixed(3) || 0 }} 吨</span>
          </div>
          <div class="info-item">
            <span class="label">当前NDVI:</span>
            <span class="value">{{ zone.current_ndvi?.toFixed(4) || 'N/A' }}</span>
          </div>
          <div class="info-item">
            <span class="label">创建时间:</span>
            <span class="value">{{ formatDate(zone.created_at) }}</span>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="zone-actions">
          <el-button
            size="small"
            @click.stop="$emit('toggle-status', zone)"
            class="secondary-btn"
          >
            {{ zone.status === 'active' ? '停止监测' : '启动监测' }}
          </el-button>
          <el-button
            size="small"
            @click.stop="$emit('edit', zone)"
            class="secondary-btn"
          >
            编辑
          </el-button>
          <el-button
            size="small"
            @click.stop="$emit('delete', zone)"
            class="danger-btn"
          >
            删除
          </el-button>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'

export default {
  name: 'ZoneList',
  components: {
    Loading
  },
  props: {
    zones: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle-status', 'edit', 'delete'],
  setup(props, { emit }) {
    const router = useRouter()
    const formatArea = (area) => {
      if (area >= 10000) {
        return `${(area / 10000).toFixed(2)} 公顷`
      }
      return `${area.toFixed(2)} 平方米`
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('zh-CN')
    }

    // 处理区域项点击事件
    const handleItemClick = (zone, event) => {
      // 检查点击目标是否是按钮或按钮内部元素
      const target = event.target
      const isButtonClick = target.closest('.zone-actions') ||
                          target.closest('.el-button') ||
                          target.closest('button')

      // 如果是按钮点击，不触发路由跳转
      if (isButtonClick) {
        return
      }

      // 跳转到监测区详情页
      router.push(`/zones/${zone.id}`)
    }


    return {
      formatArea,
      formatDate,
      handleItemClick
    }
  }
}
</script>

<style scoped>
.zones-list {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.zones-list h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.loading, .empty-state {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.zones-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.zone-item {
  padding: 15px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  transition: all 0.2s;
  position: relative;
}

.zone-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.zone-item.active {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.zone-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  cursor: pointer;
}

.zone-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.zone-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.zone-status.active {
  background-color: #f0f9ff;
  color: #409eff;
}

.zone-status.inactive {
  background-color: #fef0f0;
  color: #f56c6c;
}

.zone-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  cursor: pointer;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.label {
  color: #666;
}

.value {
  color: #333;
  font-weight: 500;
}




.zone-actions {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e6e6e6;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  pointer-events: auto;
  position: relative;
  z-index: 10;
}

.zone-actions .el-button {
  flex: 1;
  min-width: 60px;
  pointer-events: auto;
}

/* 次要操作按钮 - 中性灰色 */
.zone-actions .secondary-btn {
  background-color: #FFFFFF;
  border-color: #DCDFE6;
  color: #606266;
}

.zone-actions .secondary-btn:hover {
  background-color: #F5F7FA;
  border-color: #C0C4CC;
  color: #606266;
}

/* 危险操作按钮 - 自定义红色 */
.zone-actions .danger-btn {
  background-color: #F56C6C;
  border-color: #F56C6C;
  color: #FFFFFF;
}

.zone-actions .danger-btn:hover {
  background-color: #F78989;
  border-color: #F78989;
  color: #FFFFFF;
}
</style>
