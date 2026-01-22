<template>
  <div class="zone-detail">
    <!-- 头部操作栏 -->
    <div class="detail-header">
      <el-button
        class="back-button"
        type="default"
        plain
        circle
        @click="handleGoBack"
      >
        <el-icon><ArrowLeft /></el-icon>
      </el-button>

      <h1 class="zone-title">{{ zone?.name || '加载中' }}</h1>

      <el-button
        class="export-button"
        type="default"
        plain
        :loading="exporting"
        @click="handleExportPDF"
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
    <div v-else-if="hasData" class="detail-content">
      <!-- 基本信息卡片 -->
      <ZoneInfoCard :zone="zone" />

      <!-- 图表区域 -->
      <div class="charts-section">
        <ZoneChartCard
          title="NDVI历史趋势"
          :chart-option="ndviOption"
          :has-data="hasChartData"
        />
        <ZoneChartCard
          title="碳吸收量历史趋势"
          :chart-option="carbonOption"
          :has-data="hasChartData"
        />
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

<script setup>
import { computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Download, Loading, ArrowLeft } from '@element-plus/icons-vue'
import ZoneInfoCard from '../components/ZoneInfoCard.vue'
import ZoneChartCard from '../components/ZoneChartCard.vue'
import { useZoneDetail } from '../composables/useZoneDetail'
import { useChartConfig } from '../composables/useChartConfig'
import { usePDFExport } from '../composables/usePDFExport'

const props = defineProps({
  id: {
    type: [String, Number],
    default: null
  }
})

const route = useRoute()
const router = useRouter()

// 获取监测区ID - 优先使用props，其次使用路由参数
const zoneId = computed(() => {
  return props.id || route.params.id
})

// 使用 composables
const {
  zone,
  chartData,
  loading,
  errorMessage,
  loadData,
  hasData,
  hasChartData
} = useZoneDetail(zoneId)

const { ndviOption, carbonOption } = useChartConfig(chartData)
const { exporting, exportToPDF } = usePDFExport()

// 处理返回
const handleGoBack = () => {
  // 使用 router.push 跳转到首页
  router.push('/').catch(err => {
    // 忽略重复导航错误
    if (err.name !== 'NavigationDuplicated') {
      console.error('Navigation error:', err)
    }
  })
}

// 处理PDF导出
const handleExportPDF = async () => {
  const filename = `碳汇监测区-${zone.value?.name || zoneId.value}.pdf`
  await exportToPDF('.detail-content', filename)
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})

// 监听路由参数变化
watch(
  () => route.params.id,
  () => {
    if (route.name === 'ZoneDetail') {
      loadData()
    }
  }
)
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
  display: grid;
  grid-template-columns: minmax(auto, max-content) 1fr minmax(auto, max-content);
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 0 20px 16px;
  border-bottom: 1px solid #e6e6e6;
  min-width: 0;
  position: relative;
}

.back-button {
  justify-self: start;
  background-color: #f8f9fa;
  border-color: #dee2e6;
  color: #495057;
  width: 40px;
  height: 40px;
  padding: 0;
  flex-shrink: 0;
}

.export-button {
  justify-self: end;
  background-color: #f8f9fa;
  border-color: #dee2e6;
  color: #495057;
  white-space: nowrap;
  min-width: fit-content;
  flex-shrink: 0;
}

.zone-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 600;
  color: #333;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: calc(100% - 200px);
  pointer-events: none;
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

.charts-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
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
    gap: 12px;
    padding: 0 12px 16px;
  }

  .back-button {
    width: 36px;
    height: 36px;
  }

  .zone-title {
    font-size: 20px;
    max-width: calc(100% - 160px);
  }

  .export-button {
    font-size: 14px;
    padding: 8px 12px;
  }

  .export-button .el-icon {
    margin-right: 4px;
  }

  .charts-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .detail-header {
    gap: 8px;
    padding: 0 8px 16px;
  }

  .back-button {
    width: 32px;
    height: 32px;
  }

  .zone-title {
    font-size: 18px;
    max-width: calc(100% - 120px);
  }

  .export-button {
    padding: 6px 8px;
    font-size: 12px;
  }

  .export-button span:not(.el-icon) {
    display: none;
  }

  .export-button .el-icon {
    margin-right: 0;
  }
}
</style>