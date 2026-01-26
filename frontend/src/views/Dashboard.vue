<template>
  <div class="dashboard">
    <!-- 左侧面板 -->
    <div class="sidebar">
      <!-- 个人中心 -->
      <UserProfile :user="user" @logout="handleLogout" />

      <!-- 碳汇价格卡片 -->
      <PriceCard 
        :price="currentPrice" 
        :timestamp="priceTimestamp"
        @refresh="refreshPrice"
      />

      <!-- 操作面板 -->
      <ControlPanel 
        :is-creating="isCreatingZone"
        @start-create="startCreateZone"
        @finish-create="finishCreateZone"
        @cancel-create="cancelCreateZone"
      />

      <!-- 监测区列表 -->
      <ZoneList
        :zones="zones"
        :loading="zonesLoading"
        @select="goToZoneDetail"
        @toggle-status="toggleZoneStatus"
        @edit="editZone"
        @delete="deleteZone"
      />
    </div>

    <!-- 右侧地图区域 -->
    <div class="map-container">
      <MapView
        ref="mapViewRef"
        :zones="zones"
        :is-creating-zone="isCreatingZone"
        :temp-points="tempPoints"
        @map-click="handleMapClick"
        @zone-select="goToZoneDetail"
        @map-ready="onMapReady"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { zonesAPI } from '../api/zones'
import { pricesAPI } from '../api/prices'
import { measurementsAPI } from '../api/measurements'

// 导入组件
import UserProfile from '../components/UserProfile.vue'
import PriceCard from '../components/PriceCard.vue'
import ControlPanel from '../components/ControlPanel.vue'
import ZoneList from '../components/ZoneList.vue'
import MapView from '../components/MapView.vue'

export default {
  name: 'Dashboard',
  components: {
    UserProfile,
    PriceCard,
    ControlPanel,
    ZoneList,
    MapView
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    // 响应式数据
    const zones = ref([])
    const zonesLoading = ref(false)
    const currentPrice = ref('--')
    const priceTimestamp = ref('')
    const isCreatingZone = ref(false)
    const tempPoints = ref([])
    const mapViewRef = ref(null)
    const pricePollingTimer = ref(null)

    // 用户信息
    const user = computed(() => authStore.user)

    // 初始化
    const init = async () => {
      await Promise.all([
        loadZones(),
        loadCurrentPrice()
      ])
    }


    // 加载监测区
    const loadZones = async () => {
      try {
        zonesLoading.value = true
        const data = await zonesAPI.getZones()
        zones.value = data
      } catch (error) {
        console.error('加载监测区失败:', error)
        ElMessage.error('加载监测区失败')
      } finally {
        zonesLoading.value = false
      }
    }


    // 加载当前价格
    const loadCurrentPrice = async () => {
      try {
        const data = await pricesAPI.getCurrentPrice()
        const oldPrice = currentPrice.value
        currentPrice.value = data.price
        priceTimestamp.value = new Date(data.timestamp).toLocaleString('zh-CN')
        
        // 如果价格发生变化，给出提示（仅在非首次加载时）
        if (oldPrice !== '--' && oldPrice !== data.price) {
          const priceChange = parseFloat(data.price) - parseFloat(oldPrice)
          const changeText = priceChange > 0 ? `上涨 ${priceChange.toFixed(2)}` : `下跌 ${Math.abs(priceChange).toFixed(2)}`
          ElMessage.info(`碳汇价格已更新：${changeText} 元/吨`)
        }
      } catch (error) {
        console.error('加载价格失败:', error)
        // 尝试生成模拟数据
        try {
          await pricesAPI.generateMockPrice()
          await loadCurrentPrice()
        } catch (mockError) {
          console.error('生成模拟价格失败:', mockError)
        }
      }
    }

    // 启动价格轮询
    const startPricePolling = () => {
      // 每5分钟轮询一次价格（比后端更新频率更短，确保及时获取）
      pricePollingTimer.value = setInterval(() => {
        // 只在页面可见时轮询
        if (!document.hidden) {
          loadCurrentPrice()
        }
      }, 5 * 60 * 1000) // 5分钟 = 300000毫秒
    }

    // 停止价格轮询
    const stopPricePolling = () => {
      if (pricePollingTimer.value) {
        clearInterval(pricePollingTimer.value)
        pricePollingTimer.value = null
      }
    }

    // 地图准备完成
    const onMapReady = (map) => {
      console.log('地图加载完成')
    }

    // 地图点击处理
    const handleMapClick = (latlng) => {
      if (!isCreatingZone.value) return
      
      if (tempPoints.value.length >= 7) {
        return
      }

      tempPoints.value.push(latlng)
    }

    // 开始创建监测区
    const startCreateZone = () => {
      isCreatingZone.value = true
      tempPoints.value = []
      ElMessage.info('请在地图上点击选择监测区域的边界点（最多7个）')
    }

    // 完成创建监测区
    const finishCreateZone = async () => {
      if (tempPoints.value.length < 3) {
        ElMessage.warning('至少需要3个点来创建监测区')
        return
      }

      try {
        await ElMessageBox.prompt('请输入监测区名称', '创建监测区', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /^.{2,20}$/,
          inputErrorMessage: '名称长度必须在2-20字符之间'
        }).then(async ({ value }) => {
          const zoneData = {
            name: value,
            coordinates: tempPoints.value
          }

          const newZone = await zonesAPI.createZone(zoneData)
          zones.value.push(newZone)
          ElMessage.success('监测区创建成功，正在生成历史数据...')

          // 清理临时数据
          cancelCreateZone()
          
          // 立即刷新一次以显示基本信息
          await loadZones()
          
          // 轮询检查历史数据是否生成完成（最多等待30秒）
          let pollCount = 0
          const maxPolls = 15 // 15次 * 2秒 = 30秒
          const pollInterval = setInterval(async () => {
            pollCount++
            await loadZones()
            
            // 检查新创建的监测区是否有数据了
            const updatedZone = zones.value.find(z => z.id === newZone.id)
            if (updatedZone && updatedZone.measurements_count > 0) {
              clearInterval(pollInterval)
              ElMessage.success('历史数据生成完成')
            } else if (pollCount >= maxPolls) {
              clearInterval(pollInterval)
              ElMessage.info('历史数据正在后台生成中，请稍后刷新查看')
            }
          }, 2000) // 每2秒检查一次
        })
      } catch (error) {
        if (error !== 'cancel') {
          console.error('创建监测区失败:', error)
          ElMessage.error('创建监测区失败')
        }
      }
    }

    // 取消创建监测区
    const cancelCreateZone = () => {
      isCreatingZone.value = false
      tempPoints.value = []
      // 地图组件会自动清理临时图形
    }

    // 跳转到监测区详情页
    const goToZoneDetail = (zone) => {
      console.log('goToZoneDetail 被调用:', zone)
      if (!zone || !zone.id) {
        console.error('无效的监测区数据:', zone)
        ElMessage.error('无法跳转到详情页：监测区数据无效')
        return
      }
      router.push(`/zones/${zone.id}`).catch(err => {
        // 忽略重复导航错误
        if (err.name !== 'NavigationDuplicated') {
          console.error('路由跳转失败:', err)
          ElMessage.error('跳转失败，请稍后重试')
        }
      })
    }

    // 刷新价格
    const refreshPrice = async () => {
      try {
        // 先生成新的价格数据
        await pricesAPI.generateMockPrice()
        // 然后加载最新价格
        await loadCurrentPrice()
        ElMessage.success('价格已更新')
      } catch (error) {
        console.error('刷新价格失败:', error)
        ElMessage.error('刷新价格失败')
      }
    }

    // 登出
    const handleLogout = async () => {
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        authStore.logout()
        router.push('/login')
      } catch (error) {
        // 用户取消操作
      }
    }

    // 切换监测区状态
    const toggleZoneStatus = async (zone) => {
      try {
        const newStatus = zone.status === 'active' ? 'inactive' : 'active'
        await zonesAPI.updateZone(zone.id, { status: newStatus })
        // 重新加载列表以获取最新的统计数据
        await loadZones()
        ElMessage.success(`监测区已${newStatus === 'active' ? '启动' : '停止'}`)
      } catch (error) {
        console.error('更新状态失败:', error)
        ElMessage.error('更新状态失败')
      }
    }

    // 编辑监测区
    const editZone = async (zone) => {
      try {
        await ElMessageBox.prompt('请输入新的监测区名称', '编辑监测区', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputValue: zone.name,
          inputPattern: /^.{2,20}$/,
          inputErrorMessage: '名称长度必须在2-20字符之间'
        }).then(async ({ value }) => {
          await zonesAPI.updateZone(zone.id, { name: value })
          // 重新加载列表以获取最新的统计数据
          await loadZones()
          ElMessage.success('监测区更新成功')
        })
      } catch (error) {
        if (error !== 'cancel') {
          console.error('编辑监测区失败:', error)
          ElMessage.error('编辑监测区失败')
        }
      }
    }

    // 删除监测区
    const deleteZone = async (zone) => {
      try {
        await ElMessageBox.confirm('确定要删除该监测区吗？此操作不可恢复。', '删除确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await zonesAPI.deleteZone(zone.id)
        
        // 从地图移除
        if (mapViewRef.value) {
          mapViewRef.value.removeZone(zone.id)
        }
        
        // 重新加载列表以确保数据一致性（包括统计数据的更新）
        await loadZones()
        
        ElMessage.success('监测区已删除')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除监测区失败:', error)
          ElMessage.error('删除监测区失败')
        }
      }
    }

    // 初始化
    init()
    
    // 启动价格轮询
    startPricePolling()
    
    // 组件卸载时清理定时器
    onUnmounted(() => {
      stopPricePolling()
    })

    return {
      zones,
      zonesLoading,
      currentPrice,
      priceTimestamp,
      isCreatingZone,
      tempPoints,
      mapViewRef,
      user,
      handleMapClick,
      startCreateZone,
      finishCreateZone,
      cancelCreateZone,
      refreshPrice,
      handleLogout,
      toggleZoneStatus,
      editZone,
      deleteZone,
      goToZoneDetail,
      onMapReady
    }
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

.sidebar {
  width: 350px;
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.map-container {
  flex: 1;
  position: relative;
}
</style>
