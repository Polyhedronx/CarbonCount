<template>
  <div class="chart-card">
    <h3>{{ title }}</h3>
    <div class="chart-container">
      <v-chart
        v-if="hasData"
        :option="chartOption"
        style="height: 300px;"
        :autoresize="true"
      />
      <div v-else class="no-data">
        <el-empty description="暂无监测数据" :image-size="80" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TooltipComponent,
  GridComponent,
  TitleComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

// 注册必要的组件
use([
  CanvasRenderer,
  LineChart,
  TooltipComponent,
  GridComponent,
  TitleComponent
])

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  chartOption: {
    type: Object,
    required: true
  },
  hasData: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
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
</style>
