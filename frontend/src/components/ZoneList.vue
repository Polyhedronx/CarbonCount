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
        :class="{ active: selectedZoneId === zone.id }"
        @click="$emit('select', zone)"
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
        
        <!-- 图表区域 -->
        <div v-if="selectedZoneId === zone.id && chartData" class="zone-charts">
          <div class="chart-container">
            <h5>NDVI历史趋势</h5>
            <v-chart :option="ndviOption" style="height: 150px;" />
          </div>
          <div class="chart-container">
            <h5>碳吸收量历史趋势</h5>
            <v-chart :option="carbonOption" style="height: 150px;" />
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="zone-actions">
          <el-button
            size="small"
            :type="zone.status === 'active' ? 'warning' : 'success'"
            @click.stop="$emit('toggle-status', zone)"
          >
            {{ zone.status === 'active' ? '停止监测' : '启动监测' }}
          </el-button>
          <el-button
            size="small"
            type="primary"
            @click.stop="$emit('edit', zone)"
          >
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click.stop="$emit('delete', zone)"
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
import { Loading } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'

export default {
  name: 'ZoneList',
  components: {
    Loading,
    VChart
  },
  props: {
    zones: {
      type: Array,
      default: () => []
    },
    selectedZoneId: {
      type: Number,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    },
    chartData: {
      type: Object,
      default: null
    }
  },
  emits: ['select', 'toggle-status', 'edit', 'delete'],
  setup(props) {
    const formatArea = (area) => {
      if (area >= 10000) {
        return `${(area / 10000).toFixed(2)} 公顷`
      }
      return `${area.toFixed(2)} 平方米`
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('zh-CN')
    }

    // NDVI图表配置
    const ndviOption = computed(() => {
      const data = props.chartData
      if (!data || !data.timestamps || data.timestamps.length === 0) {
        return {
          title: { 
            text: '暂无数据', 
            left: 'center', 
            top: 'middle', 
            textStyle: { fontSize: 14, color: '#999' } 
          }
        }
      }

      return {
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const param = params[0]
            return `${param.name}<br/>${param.seriesName}: ${param.value.toFixed(4)}`
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '10%'
        },
        xAxis: {
          type: 'category',
          data: data.timestamps.map(t => new Date(t).toLocaleDateString('zh-CN')),
          axisLabel: { rotate: 45, fontSize: 10 }
        },
        yAxis: {
          type: 'value',
          name: 'NDVI',
          min: 0,
          max: 1
        },
        series: [{
          name: 'NDVI',
          type: 'line',
          data: data.ndvi_values,
          smooth: true,
          itemStyle: { color: '#67c23a' },
          areaStyle: { color: 'rgba(103, 194, 58, 0.2)' }
        }]
      }
    })

    // 碳吸收量图表配置
    const carbonOption = computed(() => {
      const data = props.chartData
      if (!data || !data.timestamps || data.timestamps.length === 0) {
        return {
          title: { 
            text: '暂无数据', 
            left: 'center', 
            top: 'middle', 
            textStyle: { fontSize: 14, color: '#999' } 
          }
        }
      }

      return {
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const param = params[0]
            return `${param.name}<br/>${param.seriesName}: ${param.value.toFixed(6)} 吨/天`
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '10%'
        },
        xAxis: {
          type: 'category',
          data: data.timestamps.map(t => new Date(t).toLocaleDateString('zh-CN')),
          axisLabel: { rotate: 45, fontSize: 10 }
        },
        yAxis: {
          type: 'value',
          name: '碳吸收量 (吨/天)'
        },
        series: [{
          name: '碳吸收量',
          type: 'line',
          data: data.carbon_values,
          smooth: true,
          itemStyle: { color: '#409eff' },
          areaStyle: { color: 'rgba(64, 158, 255, 0.2)' }
        }]
      }
    })

    return {
      formatArea,
      formatDate,
      ndviOption,
      carbonOption
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
  cursor: pointer;
  transition: all 0.2s;
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

.zone-charts {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e6e6e6;
}

.chart-container {
  margin-bottom: 15px;
}

.chart-container h5 {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.zone-actions {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e6e6e6;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.zone-actions .el-button {
  flex: 1;
  min-width: 60px;
}
</style>
