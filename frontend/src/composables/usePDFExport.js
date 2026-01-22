import { ref, createApp, h, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import html2pdf from 'html2pdf.js'
import ReportTemplate from '../components/ReportTemplate.vue'
import { generateReportData } from '../utils/reportGenerator'
import { generateChartImage } from '../utils/chartImageGenerator'

/**
 * PDF导出 Composable
 */
export function usePDFExport() {
  const exporting = ref(false)

  /**
   * 导出报告为PDF
   * @param {Object} zone - 监测区数据
   * @param {Object} chartData - 图表数据
   * @param {Object} ndviOption - NDVI图表配置
   * @param {Object} carbonOption - 碳吸收量图表配置
   * @param {string} filename - 文件名
   */
  const exportReportToPDF = async (zone, chartData, ndviOption, carbonOption, filename) => {
    let container = null
    let app = null
    
    try {
      exporting.value = true
      ElMessage.info('正在生成报告，请稍候...')

      // 参数验证
      if (!zone) {
        throw new Error('监测区数据不能为空')
      }

      // 1. 生成报告数据
      const reportData = await generateReportData(zone, chartData)

      // 2. 生成图表图片
      const chartImages = {}
      
      // 生成NDVI图表图片
      if (ndviOption && chartData && chartData.timestamps && chartData.timestamps.length > 0) {
        try {
          chartImages.ndvi = await generateChartImage(ndviOption, {
            width: 800,
            height: 400,
            type: 'png',
            pixelRatio: 2
          })
        } catch (error) {
          console.warn('生成NDVI图表图片失败:', error)
          chartImages.ndvi = ''
        }
      } else {
        chartImages.ndvi = ''
      }

      // 生成碳吸收量图表图片
      if (carbonOption && chartData && chartData.timestamps && chartData.timestamps.length > 0) {
        try {
          chartImages.carbon = await generateChartImage(carbonOption, {
            width: 800,
            height: 400,
            type: 'png',
            pixelRatio: 2
          })
        } catch (error) {
          console.warn('生成碳吸收量图表图片失败:', error)
          chartImages.carbon = ''
        }
      } else {
        chartImages.carbon = ''
      }

      // 3. 将图片URL添加到报告数据
      reportData.ndvi_chart_url = chartImages.ndvi
      reportData.carbon_chart_url = chartImages.carbon

      // 4. 创建临时容器并渲染ReportTemplate
      container = document.createElement('div')
      container.id = 'pdf-export-container'
      // 容器必须完全可见才能被html2canvas捕获，但可以放在屏幕外
      container.style.position = 'fixed'
      container.style.left = '0'
      container.style.top = '0'
      container.style.width = '210mm'
      container.style.height = 'auto'
      container.style.background = 'white'
      container.style.zIndex = '999999'
      container.style.visibility = 'visible'
      container.style.opacity = '1'
      container.style.pointerEvents = 'none'
      // 将容器移到屏幕外但保持可见
      container.style.transform = 'translateX(-9999px)'
      document.body.appendChild(container)

      // 创建Vue应用实例并挂载ReportTemplate
      app = createApp({
        render: () => h(ReportTemplate, { reportData })
      })
      app.mount(container)

      // 等待DOM渲染完成
      await nextTick()
      
      // 等待图片加载完成
      const images = container.querySelectorAll('img')
      if (images.length > 0) {
        await Promise.all(
          Array.from(images).map(img => {
            if (img.complete) return Promise.resolve()
            return new Promise((resolve) => {
              img.onload = resolve
              img.onerror = resolve // 即使失败也继续
              setTimeout(resolve, 3000) // 超时保护
            })
          })
        )
      }
      
      // 额外等待确保所有内容渲染完成
      await new Promise(resolve => setTimeout(resolve, 500))

      // 5. 确保容器完全可见并在视口内
      // 使用绝对定位而不是fixed，并确保在视口内
      const originalTransform = container.style.transform
      const originalPosition = container.style.position
      const originalLeft = container.style.left
      const originalTop = container.style.top
      const originalZIndex = container.style.zIndex
      
      // 将容器移到视口内但不可见（使用clip-path或overflow）
      container.style.position = 'absolute'
      container.style.left = '0'
      container.style.top = '0'
      container.style.transform = 'translateX(0)'
      container.style.zIndex = '999999'
      container.style.overflow = 'hidden'
      container.style.clipPath = 'inset(0)'
      
      // 强制重排
      container.offsetHeight
      
      // 等待样式应用和重排
      await new Promise(resolve => setTimeout(resolve, 300))

      // 6. 导出为PDF
      const opt = {
        margin: [15, 15, 15, 15], // 上下左右边距（mm）
        filename: filename || `空天地一体化碳汇监测报告-${zone.name || '报告'}-${new Date().toISOString().split('T')[0]}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: {
          scale: 2, // 高分辨率
          useCORS: true,
          logging: false,
          backgroundColor: '#ffffff',
          allowTaint: true,
          letterRendering: true, // 改善文字渲染
          windowWidth: container.scrollWidth,
          windowHeight: container.scrollHeight,
          onclone: (clonedDoc) => {
            // 确保克隆的文档中字体正确且完全可见
            const clonedReportContainer = clonedDoc.getElementById('report-container')
            const clonedOuterContainer = clonedDoc.getElementById('pdf-export-container')
            
            if (clonedReportContainer) {
              clonedReportContainer.style.fontFamily = "'Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS', 'PingFang SC', 'Hiragino Sans GB', sans-serif"
              clonedReportContainer.style.visibility = 'visible'
              clonedReportContainer.style.opacity = '1'
              clonedReportContainer.style.position = 'static'
              clonedReportContainer.style.transform = 'none'
            }
            
            if (clonedOuterContainer) {
              clonedOuterContainer.style.visibility = 'visible'
              clonedOuterContainer.style.opacity = '1'
              clonedOuterContainer.style.position = 'static'
              clonedOuterContainer.style.transform = 'none'
              clonedOuterContainer.style.left = 'auto'
              clonedOuterContainer.style.top = 'auto'
              clonedOuterContainer.style.overflow = 'visible'
              clonedOuterContainer.style.clipPath = 'none'
            }
          }
        },
        jsPDF: {
          unit: 'mm',
          format: 'a4',
          orientation: 'portrait',
          compress: true
        },
        pagebreak: { 
          mode: ['avoid-all', 'css', 'legacy'],
          before: '.page-break-before',
          after: '.page-break-after',
          avoid: ['.report-section', '.subsection', '.chart-container', 'table']
        }
      }

      // 尝试直接使用report-container元素，而不是外层容器
      const reportContainer = container.querySelector('#report-container')
      const targetElement = reportContainer || container

      await html2pdf().set(opt).from(targetElement).save()

      // 恢复容器样式（移回屏幕外）
      container.style.transform = originalTransform || 'translateX(-9999px)'
      container.style.position = originalPosition || 'fixed'
      container.style.left = originalLeft || '0'
      container.style.top = originalTop || '0'
      container.style.zIndex = originalZIndex || '999999'
      container.style.overflow = ''
      container.style.clipPath = ''

      ElMessage.success('PDF导出成功')
    } catch (error) {
      console.error('PDF导出失败:', error)
      ElMessage.error(`PDF导出失败: ${error.message || '未知错误'}`)
      throw error
    } finally {
      // 清理临时DOM
      if (app && container) {
        try {
          app.unmount()
        } catch (e) {
          console.warn('卸载Vue应用失败:', e)
        }
        try {
          if (container.parentNode) {
            document.body.removeChild(container)
          }
        } catch (e) {
          console.warn('移除容器失败:', e)
        }
      }
      exporting.value = false
    }
  }

  /**
   * 导出为PDF（兼容旧版本，直接导出DOM元素）
   * @param {HTMLElement|string} element - 要导出的DOM元素或选择器
   * @param {string} filename - 文件名
   */
  const exportToPDF = async (element, filename) => {
    try {
      exporting.value = true

      const targetElement = typeof element === 'string' 
        ? document.querySelector(element) 
        : element

      if (!targetElement) {
        throw new Error('找不到要导出的内容')
      }

      const opt = {
        margin: [15, 15, 15, 15],
        filename: filename || 'export.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: {
          scale: 2,
          useCORS: true,
          logging: false,
          backgroundColor: '#ffffff'
        },
        jsPDF: {
          unit: 'mm',
          format: 'a4',
          orientation: 'portrait'
        }
      }

      await html2pdf().set(opt).from(targetElement).save()
      ElMessage.success('PDF导出成功')
    } catch (error) {
      console.error('PDF导出失败:', error)
      ElMessage.error('PDF导出失败')
      throw error
    } finally {
      exporting.value = false
    }
  }

  return {
    exporting,
    exportToPDF,
    exportReportToPDF
  }
}
