import { computed } from 'vue'
import { formatChartDate, formatChartTooltip } from '../utils/formatters'

/**
 * 图表配置 Composable
 */
export function useChartConfig(chartData) {
  /**
   * NDVI图表配置
   */
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
          return formatChartTooltip(param.axisValue, param.seriesName, param.value)
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
          formatter: formatChartDate
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

  /**
   * 碳吸收量图表配置
   */
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
          return formatChartTooltip(param.axisValue, param.seriesName, param.value, '吨/天')
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
          formatter: formatChartDate
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

  return {
    ndviOption,
    carbonOption
  }
}
