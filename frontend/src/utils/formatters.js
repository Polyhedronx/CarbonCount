/**
 * 格式化工具函数
 */

/**
 * 格式化面积
 * @param {number} area - 面积（平方米）
 * @returns {string} 格式化后的面积字符串
 */
export const formatArea = (area) => {
  if (!area && area !== 0) return 'N/A'
  if (area >= 10000) {
    return `${(area / 10000).toFixed(2)} 公顷`
  }
  return `${area.toFixed(2)} 平方米`
}

/**
 * 格式化日期时间
 * @param {string|Date} dateString - 日期字符串或Date对象
 * @returns {string} 格式化后的日期时间字符串
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 格式化图表日期时间
 * @param {Date|string} value - 日期值
 * @returns {string} 格式化后的日期时间字符串 (MM/DD HH:mm)
 */
export const formatChartDate = (value) => {
  const date = new Date(value)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
}

/**
 * 格式化图表工具提示
 * @param {Date|string} dateValue - 日期值
 * @param {string} seriesName - 系列名称
 * @param {number} value - 数值
 * @param {string} unit - 单位（可选）
 * @returns {string} 格式化后的工具提示字符串
 */
export const formatChartTooltip = (dateValue, seriesName, value, unit = '') => {
  const date = new Date(dateValue)
  const dateStr = date.toLocaleDateString('zh-CN')
  const timeStr = date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  const valueStr = unit ? `${value.toFixed(6)} ${unit}` : value.toFixed(4)
  return `${dateStr} ${timeStr}<br/>${seriesName}: ${valueStr}`
}
