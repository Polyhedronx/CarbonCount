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
import { ref, computed, watch } from 'vue'
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
        currentPrice.value = data.price
        priceTimestamp.value = new Date(data.timestamp).toLocaleString('zh-CN')
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
          ElMessage.success('监测区创建成功')

          // 清理临时数据
          cancelCreateZone()
          
          // 重新加载区域列表以获取完整数据
          await loadZones()
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
      router.push(`/zones/${zone.id}`)
    }

    // 刷新价格
    const refreshPrice = async () => {
      await loadCurrentPrice()
      ElMessage.success('价格已更新')
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
