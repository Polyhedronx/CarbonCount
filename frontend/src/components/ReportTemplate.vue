<template>
  <div v-if="reportData" ref="reportContainer" class="report-container" id="report-container">
    <!-- 报告标题 -->
    <div class="report-header">
      <h1 class="report-title">空天地一体化碳汇监测报告</h1>
      <div class="report-meta">
        <p><strong>报告编号：</strong>{{ reportData.report_id }}</p>
        <p><strong>监测期：</strong>{{ reportData.start_date }} 至 {{ reportData.end_date }}</p>
        <p><strong>生成时间：</strong>{{ reportData.generation_time }}</p>
      </div>
    </div>

    <hr class="divider" />

    <!-- 目录 -->
    <div class="table-of-contents">
      <h2>目录</h2>
      <ul>
        <li><a href="#section-1">一、监测概述</a>
          <ul>
            <li><a href="#section-1-1">1.1 执行摘要</a></li>
            <li><a href="#section-1-2">1.2 项目与监测区概况</a></li>
            <li><a href="#section-1-3">1.3 监测方法与技术</a></li>
          </ul>
        </li>
        <li><a href="#section-2">二、核心计量结果</a>
          <ul>
            <li><a href="#section-2-1">2.1 碳汇量评估</a></li>
            <li><a href="#section-2-2">2.2 植被状况动态分析</a></li>
            <li><a href="#section-2-3">2.3 数据质量与说明</a></li>
          </ul>
        </li>
        <li><a href="#section-3">三、结论与建议</a></li>
      </ul>
    </div>

    <hr class="divider" />

    <!-- 一、监测概述 -->
    <section id="section-1" class="report-section">
      <h2>一、监测概述</h2>

      <!-- 1.1 执行摘要 -->
      <div id="section-1-1" class="subsection">
        <h3>1.1 执行摘要</h3>
        <p>
          本报告基于"空天地一体化"监测技术，对 <strong>{{ reportData.project_name }}</strong> 在监测期内的森林碳汇状况进行了量化评估。核心结论如下：
        </p>
        <ul>
          <li>
            <strong>碳汇总量</strong>：监测区累计固碳碳汇总量 <strong>{{ reportData.total_carbon_sink }}</strong> tCO₂e，相当于中和了约 <strong>{{ reportData.equivalent_cars }}</strong> 辆家用轿车一年的碳排放。
          </li>
          <li>
            <strong>植被健康</strong>：平均植被指数（NDVI）为 <strong>{{ reportData.avg_ndvi }}</strong>，植被覆盖与健康状况评定为 <strong>{{ reportData.vegetation_status }}</strong>。
          </li>
          <li>
            <strong>经济价值</strong>：按当前市场碳价（实时碳价 <strong>{{ reportData.current_carbon_price }}</strong> CNY/吨）估算，本期监测的碳汇量潜在经济价值约为 <strong>{{ reportData.estimated_economic_value }}</strong> 元人民币。
          </li>
        </ul>
      </div>

      <!-- 1.2 项目与监测区概况 -->
      <div id="section-1-2" class="subsection">
        <h3>1.2 项目与监测区概况</h3>
        <div class="table-wrapper">
        <table class="info-table">
          <tbody>
            <tr>
              <th>项目属性</th>
              <th>内容</th>
            </tr>
            <tr>
              <td><strong>项目编号</strong></td>
              <td>{{ reportData.project_id }}</td>
            </tr>
            <tr>
              <td><strong>监测区名称</strong></td>
              <td>{{ reportData.project_name }}</td>
            </tr>
            <tr>
              <td><strong>地理位置</strong></td>
              <td>{{ reportData.geo_location }}</td>
            </tr>
            <tr>
              <td><strong>监测面积</strong></td>
              <td>{{ reportData.project_area }} 亩</td>
            </tr>
            <tr>
              <td><strong>优势树种</strong></td>
              <td>{{ reportData.dominant_species }}</td>
            </tr>
            <tr>
              <td><strong>林分类型</strong></td>
              <td>{{ reportData.forest_type }}</td>
            </tr>
          </tbody>
        </table>
        </div>
        <p class="image-note">
          <strong>监测区边界图示：</strong><br />
          <em>（注：上图为从系统地图导出的监测区域边界截图/矢量图）</em>
        </p>
      </div>

      <!-- 1.3 监测方法与技术 -->
      <div id="section-1-3" class="subsection">
        <h3>1.3 监测方法与技术</h3>
        <p>本次评估采用"空天地一体化"技术体系，确保数据全面、精准：</p>
        <ol>
          <li><strong>"天"</strong>：利用卫星遥感数据，反演植被指数 (NDVI)；</li>
          <li><strong>"空"</strong>：集成无人机航拍影像，进行区域校验与局部精细化分析；</li>
          <li><strong>"地"</strong>：结合项目填报的树种、林分等本地调查数据，应用碳计量模型。</li>
        </ol>
      </div>
    </section>

    <hr class="divider" />

    <!-- 二、核心计量结果 -->
    <section id="section-2" class="report-section">
      <h2>二、核心计量结果</h2>

      <!-- 2.1 碳汇量评估 -->
      <div id="section-2-1" class="subsection">
        <h3>2.1 碳汇量评估</h3>
        <div class="table-wrapper">
        <table class="data-table">
          <tbody>
            <tr>
              <th>指标</th>
              <th>数值</th>
              <th>单位</th>
            </tr>
            <tr>
              <td><strong>本期预估固碳总量</strong></td>
              <td>{{ reportData.carbon_total_value }}</td>
              <td>tCO₂e</td>
            </tr>
            <tr>
              <td><strong>单位面积碳汇量</strong></td>
              <td>{{ reportData.carbon_per_mu }}</td>
              <td>tCO₂e/亩</td>
            </tr>
            <tr>
              <td><strong>数据更新时间</strong></td>
              <td>{{ reportData.data_update_time }}</td>
              <td>-</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

      <!-- 2.2 植被状况动态分析 -->
      <div id="section-2-2" class="subsection">
        <h3>2.2 植被状况动态分析</h3>
        <p><strong>趋势分析摘要：</strong></p>
        <ul>
          <li>
            NDVI均值从期初值 {{ reportData.ndvi_start }} 变化至期末值 {{ reportData.ndvi_end }}，总体趋势为 <strong>{{ reportData.ndvi_trend }}</strong>。
          </li>
          <li>
            植被生长旺季出现在 <strong>{{ reportData.peak_month }}</strong> 月，NDVI峰值达 <strong>{{ reportData.ndvi_peak_value }}</strong>。
          </li>
        </ul>
        
        <!-- NDVI趋势图 -->
        <div v-if="reportData.ndvi_chart_url" class="chart-container">
          <p class="chart-title"><strong>监测期NDVI变化趋势图</strong></p>
          <img 
            :src="reportData.ndvi_chart_url" 
            alt="NDVI历史趋势图" 
            class="chart-image"
            data-chart="ndvi"
          />
        </div>
        
        <!-- 碳吸收量趋势图 -->
        <div v-if="reportData.carbon_chart_url" class="chart-container">
          <p class="chart-title"><strong>监测期碳吸收量变化趋势图</strong></p>
          <img 
            :src="reportData.carbon_chart_url" 
            alt="碳吸收量历史趋势图" 
            class="chart-image"
            data-chart="carbon"
          />
        </div>
      </div>

      <!-- 2.3 数据质量与说明 -->
      <div id="section-2-3" class="subsection">
        <h3>2.3 数据质量与说明</h3>
        <ul>
          <li>
            <strong>数据源</strong>：本报告核心遥感数据来源于 <strong>{{ reportData.remote_sensing_source }}</strong>，采用 <strong>{{ reportData.calculation_model }}</strong> 模型计量。
          </li>
          <li>
            <strong>波动性说明</strong>：评估结果的波动性主要来源于遥感数据反演精度以及模型参数，总体不确定性估计约为 <strong>{{ reportData.uncertainty_percentage }}%</strong>。
          </li>
          <li>
            <strong>碳价引用</strong>：报告中引用的碳市场价格 <strong>{{ reportData.referenced_price }}</strong> CNY/吨 来源于 <strong>{{ reportData.price_source }}</strong>，更新时间为 <strong>{{ reportData.price_update_date }}</strong>，仅用于经济价值估算参考。
          </li>
        </ul>
      </div>
    </section>

    <hr class="divider" />

    <!-- 三、结论与建议 -->
    <section id="section-3" class="report-section">
      <h2>三、结论与建议</h2>
      <p>
        <strong>{{ reportData.project_name }}</strong> 在监测期内表现出 <strong>{{ reportData.performance_summary }}</strong> 碳汇功能，监测结果可为项目参与碳市场交易、申请生态补偿或履行社会责任提供定量依据。
      </p>
      <p><strong>建议：</strong></p>
      <ol>
        <li>
          <strong>持续监测</strong>：建议维持现有监测频率，持续跟踪碳汇动态。
        </li>
        <li>
          <strong>经营管理</strong>：针对NDVI较低的区域（如有），可考虑采取如：<strong>{{ reportData.management_measures }}</strong> 经营措施。
        </li>
        <li>
          <strong>价值实现</strong>：关注国内外碳市场政策，适时推动碳汇资产开发。
        </li>
      </ol>
    </section>

    <!-- 页脚 -->
    <div class="report-footer">
      <blockquote>
        <p><strong>报告生成系统</strong>：数碳科技—空天地一体化碳汇计量系统</p>
        <p><strong>声明</strong>：本报告由自动化系统生成，结果仅供参考，用于正式交易或认证需由具备资质的第三方机构核证。</p>
      </blockquote>
    </div>
  </div>
</template>

<script setup>
import { watch, nextTick } from 'vue'

const props = defineProps({
  reportData: {
    type: Object,
    required: true
  }
})

// 确保数据存在
if (!props.reportData) {
  console.warn('ReportTemplate: reportData is missing')
}

defineExpose({
  getContainer: () => document.getElementById('report-container')
})
</script>

<style scoped>
.report-container {
  max-width: 210mm;
  margin: 0 auto;
  padding: 20mm;
  background: white;
  color: #333 !important; /* 确保文字颜色不是白色 */
  font-family: 'Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
  line-height: 1.6;
  font-size: 12pt;
  overflow: visible; /* 确保内容不被裁剪 */
  min-height: auto; /* 允许内容自然扩展 */
  width: 100%; /* 确保宽度不为0 */
  box-sizing: border-box;
  /* 确保中文字体正确渲染 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.report-header {
  text-align: center;
  margin-bottom: 20px;
  color: #333 !important; /* 确保标题颜色正确 */
}

.report-title {
  font-size: 24pt;
  font-weight: bold;
  margin-bottom: 20px;
  color: #2c3e50 !important;
  font-family: 'Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS', sans-serif;
}

.report-meta {
  text-align: left;
  font-size: 11pt;
  line-height: 1.8;
}

.report-meta p {
  margin: 5px 0;
}

.divider {
  border: none;
  border-top: 1px solid #ddd;
  margin: 10px 0;
}

.table-of-contents {
  margin: 20px 0;
}

.table-of-contents h2 {
  font-size: 16pt;
  margin-bottom: 15px;
}

.table-of-contents ul {
  list-style: none;
  padding-left: 20px;
}

.table-of-contents li {
  margin: 8px 0;
}

.table-of-contents a {
  color: #409eff;
  text-decoration: none;
}

.table-of-contents a:hover {
  text-decoration: underline;
}

.report-section {
  margin: 20px 0;
}

.report-section h2 {
  font-size: 18pt;
  font-weight: bold;
  margin: 25px 0 15px 0;
  color: #2c3e50 !important;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
  font-family: 'Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS', sans-serif;
}

.subsection {
  margin: 15px 0;
}

.subsection h3 {
  font-size: 14pt;
  font-weight: bold;
  margin: 20px 0 12px 0;
  color: #34495e !important;
  font-family: 'Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS', sans-serif;
}

.subsection p {
  margin: 12px 0;
  text-align: justify;
}

.subsection ul,
.subsection ol {
  margin: 12px 0;
  padding-left: 30px;
}

.subsection li {
  margin: 8px 0;
}

.info-table,
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
  font-size: 11pt;
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  display: table !important; /* 确保表格正确显示 */
  /* 防止表格被分页切断 */
  page-break-before: auto !important;
  page-break-after: auto !important;
  orphans: 3 !important; /* 至少保留3行在同一页 */
  widows: 3 !important; /* 至少保留3行在同一页 */
}

.info-table th,
.data-table th {
  background-color: #f5f7fa;
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
  font-weight: bold;
}

.info-table td,
.data-table td {
  border: 1px solid #ddd;
  padding: 10px;
}

.info-table tr:nth-child(even),
.data-table tr:nth-child(even) {
  background-color: #fafafa;
}

.image-note {
  margin-top: 15px;
  font-size: 10pt;
  color: #666;
  font-style: italic;
}

/* 图表容器样式 - 确保不被分页截断 */
.chart-container {
  margin: 20px 0;
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  display: block !important;
  width: 100%;
}

.chart-title {
  margin: 15px 0 10px 0;
  font-size: 11pt;
  font-weight: bold;
  text-align: center;
  page-break-after: avoid;
  break-after: avoid;
}

.chart-image {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  margin: 10px auto;
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  page-break-before: auto;
  page-break-after: auto;
  /* 确保图片清晰 */
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}

.report-footer {
  margin-top: 40px;
  padding-top: 20px;
  padding-bottom: 20px; /* 确保页脚有足够空间 */
  border-top: 1px solid #ddd;
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  display: block !important; /* 确保正确显示 */
  min-height: 80px; /* 确保有最小高度 */
  visibility: visible !important; /* 确保可见 */
  opacity: 1 !important; /* 确保不透明 */
}

.report-footer blockquote {
  margin: 0;
  padding: 15px;
  background-color: #f9f9f9;
  border-left: 4px solid #409eff;
  font-size: 10pt;
  color: #666;
}

.report-footer blockquote p {
  margin: 8px 0;
}

/* PDF分页控制样式 */
/* 确保所有文本元素都有正确的颜色和字体 */
.report-container * {
  color: inherit;
  font-family: inherit;
}

.report-container {
  page-break-inside: auto;
}

.report-header {
  page-break-after: avoid;
  page-break-inside: avoid;
}

.divider {
  page-break-after: avoid;
  page-break-before: avoid;
}

.table-of-contents {
  page-break-after: avoid;
  page-break-inside: avoid;
}

.report-section {
  page-break-inside: auto; /* 改为auto，允许在节内分页，避免节前产生过大间隔 */
  page-break-before: auto;
  page-break-after: auto;
  break-inside: auto;
  min-height: 0; /* 移除最小高度，避免强制分页 */
  display: block !important; /* 确保正确显示 */
  orphans: 2; /* 至少保留2行在同一页 */
  widows: 2; /* 至少保留2行在同一页 */
}

.report-section h2 {
  page-break-after: avoid;
  page-break-before: auto;
  break-after: avoid;
}

.subsection {
  page-break-inside: avoid;
  break-inside: avoid;
  /* 确保subsection有足够空间，避免被截断 */
  min-height: 0;
  orphans: 3; /* 至少保留3行在同一页 */
  widows: 3; /* 至少保留3行在同一页 */
  page-break-before: auto;
  page-break-after: auto;
}

.subsection h3 {
  page-break-after: avoid;
  break-after: avoid;
}

.info-table,
.data-table {
  page-break-inside: avoid;
  break-inside: avoid;
}

.info-table tr,
.data-table tr {
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  display: table-row !important; /* 确保行正确显示 */
  page-break-before: auto !important;
  page-break-after: auto !important;
}

.info-table td,
.data-table td,
.info-table th,
.data-table th {
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  display: table-cell !important; /* 确保单元格正确显示 */
  vertical-align: top; /* 确保内容对齐 */
}

/* 确保表格前后有足够的空间，避免被切断 */
.subsection:has(.info-table),
.subsection:has(.data-table) {
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  margin-bottom: 20px !important;
}

.subsection ul,
.subsection ol {
  page-break-inside: avoid;
  break-inside: avoid;
}

.subsection li {
  page-break-inside: avoid;
  break-inside: avoid;
  margin-bottom: 4px; /* 确保列表项之间有适当间距 */
}

/* 确保列表完整显示 */
.subsection ol,
.subsection ul {
  padding-bottom: 10px; /* 给列表底部留空间 */
  display: block !important; /* 确保列表正确显示 */
}

/* 表格容器分页控制 - 确保表格前后不被切断 */
.subsection:has(table),
.subsection:has(.info-table),
.subsection:has(.data-table) {
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  margin-bottom: 20px !important;
  padding-bottom: 10px !important;
}

/* 如果浏览器不支持:has()，使用类名方式 */
.table-wrapper {
  page-break-inside: avoid !important;
  break-inside: avoid !important;
  margin-bottom: 20px !important;
}

/* 确保图表容器及其父元素不被截断 */
.subsection:has(.chart-container),
.subsection:has(.chart-image) {
  page-break-inside: avoid !important;
  break-inside: avoid !important;
}

/* 如果不支持:has()，直接使用类名 */
.chart-container {
  page-break-inside: avoid !important;
  break-inside: avoid !important;
}

/* 确保图表前后有足够空间 */
.chart-container + .subsection,
.subsection + .chart-container {
  margin-top: 20px;
  page-break-before: auto;
}

/* 确保第三部分和页脚都能显示 */
#section-3 {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  min-height: 100px; /* 确保有足够高度，但避免过多空白 */
  page-break-inside: avoid;
  break-inside: avoid;
}

#section-3 ol {
  display: block !important;
  visibility: visible !important;
}

#section-3 li {
  display: list-item !important;
  visibility: visible !important;
}

.report-footer {
  page-break-before: auto;
  page-break-inside: avoid;
}

/* 打印样式 */
@media print {
  .report-container {
    padding: 15mm;
  }
}
</style>
