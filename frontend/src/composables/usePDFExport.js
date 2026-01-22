import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import html2pdf from 'html2pdf.js'

/**
 * PDF导出 Composable
 */
export function usePDFExport() {
  const exporting = ref(false)

  /**
   * 导出为PDF
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
        margin: 1,
        filename: filename || 'export.pdf',
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
    exportToPDF
  }
}
