import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TooltipComponent,
  GridComponent,
  TitleComponent
} from 'echarts/components'

// 注册必要的组件
echarts.use([
  CanvasRenderer,
  LineChart,
  TooltipComponent,
  GridComponent,
  TitleComponent
])

/**
 * 从图表配置生成图片
 * @param {Object} chartOption - ECharts图表配置选项
 * @param {Object} options - 额外选项
 * @param {number} options.width - 图片宽度（默认800）
 * @param {number} options.height - 图片高度（默认400）
 * @param {string} options.type - 图片类型（默认'png'）
 * @param {number} options.pixelRatio - 像素比（默认2，用于高分辨率）
 * @returns {Promise<string>} base64格式的图片URL
 */
export async function generateChartImage(chartOption, options = {}) {
  const {
    width = 800,
    height = 400,
    type = 'png',
    pixelRatio = 2
  } = options

  try {
    // 创建临时的DOM容器
    const container = document.createElement('div')
    container.style.width = `${width}px`
    container.style.height = `${height}px`
    container.style.position = 'absolute'
    container.style.left = '-9999px'
    container.style.top = '-9999px'
    document.body.appendChild(container)

    // 创建ECharts实例
    const chart = echarts.init(container, null, {
      width,
      height,
      renderer: 'canvas'
    })

    // 设置图表配置
    chart.setOption(chartOption, { notMerge: true })

    // 等待图表渲染完成
    await new Promise((resolve) => {
      let resolved = false
      const finish = () => {
        if (!resolved) {
          resolved = true
          resolve()
        }
      }
      
      // 监听渲染完成事件
      chart.on('finished', finish)
      
      // 超时保护
      setTimeout(() => {
        finish()
      }, 1000)
      
      // 立即检查是否已经渲染完成
      setTimeout(() => {
        try {
          // 尝试获取图表实例，如果成功说明已渲染
          if (chart && chart.getWidth && chart.getHeight) {
            finish()
          }
        } catch (e) {
          // 忽略错误，继续等待
        }
      }, 200)
    })

    // 生成图片
    const imageUrl = chart.getDataURL({
      type,
      pixelRatio,
      backgroundColor: '#fff'
    })

    // 清理
    chart.dispose()
    document.body.removeChild(container)

    return imageUrl
  } catch (error) {
    console.error('生成图表图片失败:', error)
    throw error
  }
}

/**
 * 批量生成图表图片
 * @param {Array<{name: string, option: Object, options?: Object}>} charts - 图表配置数组
 * @returns {Promise<Object>} 包含所有图表图片URL的对象
 */
export async function generateChartImages(charts) {
  const results = {}
  
  for (const chart of charts) {
    try {
      const imageUrl = await generateChartImage(chart.option, chart.options)
      results[chart.name] = imageUrl
    } catch (error) {
      console.error(`生成图表 ${chart.name} 图片失败:`, error)
      // 如果生成失败，设置为空字符串，报告模板会处理
      results[chart.name] = ''
    }
  }
  
  return results
}
