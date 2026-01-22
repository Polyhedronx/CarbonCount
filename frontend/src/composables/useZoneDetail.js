import { ref, computed, unref } from 'vue'
import { ElMessage } from 'element-plus'
import { zonesAPI } from '../api/zones'
import { measurementsAPI } from '../api/measurements'

/**
 * 监测区详情数据管理 Composable
 * @param {import('vue').Ref|import('vue').ComputedRef|string|number} zoneId - 监测区ID
 */
export function useZoneDetail(zoneId) {
  const zone = ref(null)
  const chartData = ref(null)
  const loading = ref(true)
  const errorMessage = ref('')

  /**
   * 获取实际的zoneId值
   */
  const getZoneId = () => {
    return unref(zoneId)
  }

  /**
   * 加载监测区详情数据
   */
  const loadZoneData = async () => {
    try {
      loading.value = true
      errorMessage.value = ''
      const id = getZoneId()
      if (!id) {
        throw new Error('监测区ID不能为空')
      }
      zone.value = await zonesAPI.getZone(id)
    } catch (error) {
      console.error('加载监测区详情失败:', error)
      errorMessage.value = error.response?.data?.detail || error.message || '加载失败'
      ElMessage.error('加载监测区详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 加载图表数据
   */
  const loadChartData = async () => {
    try {
      const id = getZoneId()
      if (!id) {
        return
      }
      chartData.value = await measurementsAPI.getZoneChartData(id)
    } catch (error) {
      console.error('加载图表数据失败:', error)
      // 图表数据加载失败不影响页面显示，只记录错误
      chartData.value = null
    }
  }

  /**
   * 加载所有数据
   */
  const loadData = async () => {
    await Promise.all([
      loadZoneData(),
      loadChartData()
    ])
  }

  /**
   * 是否有数据
   */
  const hasData = computed(() => {
    return zone.value !== null
  })

  /**
   * 是否有图表数据
   */
  const hasChartData = computed(() => {
    return chartData.value && 
           chartData.value.timestamps && 
           chartData.value.timestamps.length > 0
  })

  return {
    zone,
    chartData,
    loading,
    errorMessage,
    loadData,
    loadZoneData,
    loadChartData,
    hasData,
    hasChartData
  }
}
