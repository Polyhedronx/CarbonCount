<template>
  <div class="zone-detail">
    <!-- 头部操作栏 -->
    <div class="detail-header">
      <h1 class="zone-title">{{ zone?.name || '加载中...' }}</h1>

      <el-button
        class="export-button"
        type="default"
        plain
        :loading="exporting"
        @click="exportToPDF"
      >
        <el-icon><Download /></el-icon>
        导出PDF
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40">
        <Loading />
      </el-icon>
      <p>加载中...</p>
    </div>

    <!-- 内容区域 -->
    <div v-else-if="zone" class="detail-content">
      <!-- 基本信息卡片 -->
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
          <div class="info-item">
            <span class="label">监测数据点数:</span>
            <span class="value">{{ zone.measurements_count || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <div class="chart-card">
          <h3>NDVI历史趋势</h3>
          <div class="chart-container">
            <v-chart
              v-if="chartData && chartData.timestamps?.length > 0"
              :option="ndviOption"
              style="height: 300px;"
              :autoresize="true"
            />
            <div v-else class="no-data">
              <el-empty description="暂无监测数据" :image-size="80" />
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3>碳吸收量历史趋势</h3>
          <div class="chart-container">
            <v-chart
              v-if="chartData && chartData.timestamps?.length > 0"
              :option="carbonOption"
              style="height: 300px;"
              :autoresize="true"
            />
            <div v-else class="no-data">
              <el-empty description="暂无监测数据" :image-size="80" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <el-result
        icon="error"
        title="加载失败"
        :sub-title="errorMessage || '监测区不存在或加载失败'"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Download,
  Loading
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { zonesAPI } from '../api/zones'
import { measurementsAPI } from '../api/measurements'
import html2pdf from 'html2pdf.js'

export default {
  name: 'ZoneDetail',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  components: {
    Download,
    Loading,
    VChart
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()

    const zone = ref(null)
    const chartData = ref(null)
    const loading = ref(true)
    const exporting = ref(false)
    const errorMessage = ref('')

    // 获取监测区ID - 优先使用props，其次使用路由参数
    const zoneId = computed(() => {
      console.log('ZoneDetail: props.id =', props.id, 'route.params.id =', route.params.id)
      return props.id || route.params.id
    })

    // 加载数据
    const loadData = async () => {
      try {
        console.log('ZoneDetail: loadData called, zoneId =', zoneId.value)
        loading.value = true
        errorMessage.value = ''

        // 加载监测区详情
        console.log('ZoneDetail: fetching zone data...')
        zone.value = await zonesAPI.getZone(zoneId.value)
        console.log('ZoneDetail: zone data received:', zone.value)

        // 加载图表数据
        console.log('ZoneDetail: fetching chart data...')
        chartData.value = await measurementsAPI.getZoneChartData(zoneId.value)
        console.log('ZoneDetail: chart data received:', chartData.value)

      } catch (error) {
        console.error('加载监测区详情失败:', error)
        errorMessage.value = error.response?.data?.detail || '加载失败'
        ElMessage.error('加载监测区详情失败')
      } finally {
        console.log('ZoneDetail: loadData completed, loading = false, zone =', zone.value, 'chartData =', chartData.value)
        loading.value = false
      }
    }

    // 格式化面积
    const formatArea = (area) => {
      if (area >= 10000) {
        return `${(area / 10000).toFixed(2)} 公顷`
      }
      return `${area.toFixed(2)} 平方米`
    }

    // 格式化日期
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }


    // 导出PDF
    const exportToPDF = async () => {
      try {
        exporting.value = true

        const element = document.querySelector('.detail-content')
        if (!element) {
          throw new Error('找不到要导出的内容')
        }

        const opt = {
          margin: 1,
          filename: `碳汇监测区-${zone.value?.name || zoneId.value}.pdf`,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: {
            scale: 2,
            useCORS: true,
            logging: false
          },
          jsPDF: {
            unit: 'mm',
            format: 'a4',
            orientation: 'portrait'
          }
        }

        await html2pdf().set(opt).from(element).save()

        ElMessage.success('PDF导出成功')
      } catch (error) {
        console.error('PDF导出失败:', error)
        ElMessage.error('PDF导出失败')
      } finally {
        exporting.value = false
      }
    }

    // NDVI图表配置
    const ndviOption = computed(() => {
      const data = chartData.value
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
            const date = new Date(param.axisValue)
            const dateStr = date.toLocaleDateString('zh-CN')
            const timeStr = date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
            return `${dateStr} ${timeStr}<br/>${param.seriesName}: ${param.value.toFixed(4)}`
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
          data: data.timestamps.map(t => new Date(t)),
          axisLabel: {
            rotate: 45,
            fontSize: 10,
            formatter: (value) => {
              const date = new Date(value)
              return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
            }
          }
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
      const data = chartData.value
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
            const date = new Date(param.axisValue)
            const dateStr = date.toLocaleDateString('zh-CN')
            const timeStr = date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
            return `${dateStr} ${timeStr}<br/>${param.seriesName}: ${param.value.toFixed(6)} 吨/天`
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
          data: data.timestamps.map(t => new Date(t)),
          axisLabel: {
            rotate: 45,
            fontSize: 10,
            formatter: (value) => {
              const date = new Date(value)
              return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
            }
          }
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

    // 组件挂载时加载数据
    onMounted(() => {
      loadData()
    })

    // 监听路由参数变化
    const unwatch = route.watch((to) => {
      if (to.name === 'ZoneDetail') {
        loadData()
      }
    })

    return {
      zone,
      chartData,
      loading,
      exporting,
      errorMessage,
      formatArea,
      formatDate,
      exportToPDF,
      ndviOption,
      carbonOption
    }
  }
}
</script>

<style scoped>
.zone-detail {
  height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e6e6e6;
}


.export-button {
  background-color: #f8f9fa;
  border-color: #dee2e6;
  color: #495057;
}

.zone-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.loading-container p {
  margin-top: 12px;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
}

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

.charts-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
  font-weight: 500;
}

.chart-container {
  position: relative;
  min-height: 300px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.error-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (min-width: 1024px) {
  .charts-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .charts-section {
    grid-template-columns: 1fr;
  }
}
</style>