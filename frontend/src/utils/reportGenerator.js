import { pricesAPI } from '../api/prices'
import { formatDate, formatArea } from './formatters'

/**
 * 生成报告数据
 * @param {Object} zone - 监测区数据
 * @param {Object} chartData - 图表数据
 * @returns {Promise<Object>} 报告数据对象
 */
export async function generateReportData(zone, chartData) {
  // 获取当前碳价
  let currentPrice = 0
  try {
    const priceData = await pricesAPI.getCurrentPrice()
    currentPrice = priceData.price || 0
  } catch (error) {
    console.warn('获取碳价失败，使用默认值0:', error)
  }

  // 计算统计数据
  const stats = calculateStatistics(chartData)
  
  // 生成报告ID
  const reportId = `RPT-${zone.id}-${Date.now()}`
  
  // 计算监测期
  const startDate = stats.startDate || new Date(zone.created_at).toLocaleDateString('zh-CN')
  const endDate = stats.endDate || new Date().toLocaleDateString('zh-CN')
  
  // 计算碳汇总量（累计）
  const totalCarbonSink = zone.total_carbon_absorption || stats.totalCarbon || 0
  
  // 计算单位面积碳汇量
  const areaInMu = zone.area ? zone.area / 666.67 : 0 // 平方米转亩
  const carbonPerMu = areaInMu > 0 ? (totalCarbonSink / areaInMu).toFixed(3) : '0'
  
  // 计算等效车辆数（假设每辆车年排放2.4吨CO2）
  const equivalentCars = Math.round(totalCarbonSink / 2.4)
  
  // 计算经济价值
  const estimatedEconomicValue = (totalCarbonSink * currentPrice).toFixed(2)
  
  // 判断植被状况
  const avgNDVI = stats.avgNDVI || 0
  let vegetationStatus = '一般'
  if (avgNDVI >= 0.7) vegetationStatus = '优秀'
  else if (avgNDVI >= 0.5) vegetationStatus = '良好'
  else if (avgNDVI >= 0.3) vegetationStatus = '一般'
  else vegetationStatus = '较差'
  
  // 判断NDVI趋势
  let ndviTrend = '稳定'
  if (stats.ndviTrend > 0.05) ndviTrend = '上升'
  else if (stats.ndviTrend < -0.05) ndviTrend = '下降'
  
  // 获取峰值月份
  const peakMonth = stats.peakMonth || new Date().getMonth() + 1
  
  // 生成时间
  const generationTime = new Date().toLocaleString('zh-CN')
  
  // 数据更新时间
  const dataUpdateTime = stats.lastUpdateTime || generationTime

  return {
    // 报告元数据
    report_id: reportId,
    start_date: startDate,
    end_date: endDate,
    generation_time: generationTime,
    
    // 项目信息
    project_id: `PRJ-${zone.id}`,
    project_name: zone.name || '未命名监测区',
    geo_location: zone.coordinates ? '见监测区边界图' : '未设置',
    project_area: areaInMu.toFixed(2),
    dominant_species: '待补充', // 需要从zone数据中获取或设为默认值
    forest_type: '待补充', // 需要从zone数据中获取或设为默认值
    
    // 执行摘要
    total_carbon_sink: totalCarbonSink.toFixed(3),
    equivalent_cars: equivalentCars,
    avg_ndvi: avgNDVI.toFixed(4),
    vegetation_status: vegetationStatus,
    current_carbon_price: currentPrice.toFixed(2),
    estimated_economic_value: estimatedEconomicValue,
    
    // 核心计量结果
    carbon_total_value: totalCarbonSink.toFixed(3),
    carbon_per_mu: carbonPerMu,
    data_update_time: dataUpdateTime,
    
    // 植被状况
    ndvi_start: stats.ndviStart?.toFixed(4) || 'N/A',
    ndvi_end: stats.ndviEnd?.toFixed(4) || 'N/A',
    ndvi_trend: ndviTrend,
    peak_month: peakMonth,
    ndvi_peak_value: stats.ndviPeak?.toFixed(4) || 'N/A',
    
    // 数据质量说明
    remote_sensing_source: '卫星遥感数据',
    calculation_model: '空天地一体化碳汇计量模型',
    uncertainty_percentage: '5-10',
    referenced_price: currentPrice.toFixed(2),
    price_source: '碳市场实时价格',
    price_update_date: new Date().toLocaleDateString('zh-CN'),
    
    // 结论与建议
    performance_summary: avgNDVI >= 0.5 ? '积极的' : '稳定的',
    management_measures: '补植、施肥、病虫害防治等',
    
    // 图片URL（需要后续生成）
    boundary_image_url: '', // 监测区域边界图
    ndvi_chart_url: '', // NDVI历史趋势图
    carbon_chart_url: '' // 碳吸收量历史趋势图
  }
}

/**
 * 计算统计数据
 * @param {Object} chartData - 图表数据
 * @returns {Object} 统计数据
 */
function calculateStatistics(chartData) {
  if (!chartData || !chartData.timestamps || chartData.timestamps.length === 0) {
    return {
      avgNDVI: 0,
      ndviStart: 0,
      ndviEnd: 0,
      ndviTrend: 0,
      ndviPeak: 0,
      peakMonth: new Date().getMonth() + 1,
      totalCarbon: 0,
      startDate: null,
      endDate: null,
      lastUpdateTime: null
    }
  }

  const { timestamps, ndvi_values, carbon_values } = chartData
  
  // NDVI统计
  const ndviSum = ndvi_values.reduce((sum, val) => sum + (val || 0), 0)
  const avgNDVI = ndviSum / ndvi_values.length
  const ndviStart = ndvi_values[0] || 0
  const ndviEnd = ndvi_values[ndvi_values.length - 1] || 0
  const ndviTrend = ndviEnd - ndviStart
  
  // 找到NDVI峰值
  let ndviPeak = 0
  let peakIndex = 0
  ndvi_values.forEach((val, index) => {
    if (val > ndviPeak) {
      ndviPeak = val
      peakIndex = index
    }
  })
  const peakDate = new Date(timestamps[peakIndex])
  const peakMonth = peakDate.getMonth() + 1
  
  // 碳吸收量统计（累计）
  const totalCarbon = carbon_values.reduce((sum, val) => sum + (val || 0), 0)
  
  // 日期范围
  const startDate = new Date(timestamps[0]).toLocaleDateString('zh-CN')
  const endDate = new Date(timestamps[timestamps.length - 1]).toLocaleDateString('zh-CN')
  const lastUpdateTime = new Date(timestamps[timestamps.length - 1]).toLocaleString('zh-CN')

  return {
    avgNDVI,
    ndviStart,
    ndviEnd,
    ndviTrend,
    ndviPeak,
    peakMonth,
    totalCarbon,
    startDate,
    endDate,
    lastUpdateTime
  }
}

/**
 * 替换模板中的变量
 * @param {string} template - 模板字符串
 * @param {Object} data - 数据对象
 * @returns {string} 替换后的字符串
 */
export function replaceTemplateVariables(template, data) {
  let result = template
  Object.keys(data).forEach(key => {
    const regex = new RegExp(`\\{\\{${key}\\}\\}`, 'g')
    result = result.replace(regex, data[key] || '')
  })
  return result
}
