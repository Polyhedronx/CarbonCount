<template>
  <div ref="mapContainer" class="map-view" :class="{ loading: isLoading }">
    <div v-if="isLoading" class="map-loading">
      <el-icon class="is-loading" :size="40">
        <Loading />
      </el-icon>
      <p>地图加载中...</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// 修复Leaflet默认图标问题
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl
})

export default {
  name: 'MapView',
  components: {
    Loading
  },
  props: {
    zones: {
      type: Array,
      default: () => []
    },
    selectedZoneId: {
      type: Number,
      default: null
    },
    isCreatingZone: {
      type: Boolean,
      default: false
    },
    tempPoints: {
      type: Array,
      default: () => []
    }
  },
  emits: ['map-click', 'zone-select', 'map-ready'],
  setup(props, { emit }) {
    const mapContainer = ref(null)
    const isLoading = ref(true)
    let map = null
    let tempPolygon = null
    let tempMarkers = []
    let tempLine = null
    let zonePolygons = {}
    let selectedPolygon = null

    // 初始化地图
    const initMap = () => {
      if (!mapContainer.value) return

      try {
        const initialCenter = [22.5828, 113.9686]
        map = L.map(mapContainer.value, {
          preferCanvas: true, // 使用Canvas渲染提升性能
          zoomControl: true,
          attributionControl: false
        }).setView(initialCenter, 16)

        // 使用国内高德地图瓦片服务
        const tileUrls = [
          // 高德地图
          {
            url: 'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
            subdomains: ['1', '2', '3', '4'],
            attribution: '© 高德地图'
          },
          // 备用：天地图
          {
            url: 'http://t{s}.tianditu.gov.cn/vec_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=YOUR_TOKEN',
            subdomains: ['0', '1', '2', '3', '4', '5', '6', '7'],
            attribution: '© 天地图'
          }
        ]

        // 使用高德地图
        const tileConfig = tileUrls[0]
        L.tileLayer(tileConfig.url, {
          subdomains: tileConfig.subdomains,
          attribution: tileConfig.attribution,
          maxZoom: 18,
          minZoom: 3
        }).addTo(map)

        // 地图点击事件
        map.on('click', handleMapClick)
        
        // 地图加载完成
        map.whenReady(() => {
          isLoading.value = false
          emit('map-ready', map)
        })

      } catch (error) {
        console.error('地图初始化失败:', error)
        ElMessage.error('地图初始化失败')
        isLoading.value = false
      }
    }

    // 地图点击处理
    const handleMapClick = (e) => {
      if (!props.isCreatingZone) return
      
      if (props.tempPoints.length >= 7) {
        ElMessage.warning('最多只能选择7个点')
        return
      }

      emit('map-click', e.latlng)
    }

    // 添加点标记
    const addPointMarker = (lat, lng, index) => {
      const marker = L.circleMarker([lat, lng], {
        radius: 6,
        color: '#ff4500',
        fillColor: '#ff6347',
        fillOpacity: 0.8,
        weight: 2
      }).addTo(map)
      
      marker.bindTooltip(`点 ${index}`, {
        permanent: true,
        direction: 'top',
        className: 'point-label'
      })
      
      tempMarkers.push(marker)
    }

    // 更新临时图形
    const updateTempPolygon = () => {
      // 清除之前的图形
      if (tempLine) {
        map.removeLayer(tempLine)
        tempLine = null
      }
      if (tempPolygon) {
        map.removeLayer(tempPolygon)
        tempPolygon = null
      }

      const pointCount = props.tempPoints.length
      if (pointCount === 0) return

      const latlngs = props.tempPoints.map(p => [p.lat, p.lng])

      // 两个点时显示连线
      if (pointCount === 2) {
        tempLine = L.polyline(latlngs, {
          color: '#ff4500',
          weight: 2,
          opacity: 0.8,
          dashArray: '5, 5'
        }).addTo(map)
      }
      // 三个或更多点时显示多边形
      else if (pointCount >= 3) {
        tempPolygon = L.polygon(latlngs, {
          color: '#ff4500',
          weight: 2,
          opacity: 0.8,
          fillColor: '#ff6347',
          fillOpacity: 0.2
        }).addTo(map)
      }
    }

    // 清除临时图形
    const clearTempShapes = () => {
      tempMarkers.forEach(marker => {
        if (marker) map.removeLayer(marker)
      })
      tempMarkers = []

      if (tempLine) {
        map.removeLayer(tempLine)
        tempLine = null
      }

      if (tempPolygon) {
        map.removeLayer(tempPolygon)
        tempPolygon = null
      }
    }

    // 显示所有区域
    const displayZones = () => {
      if (!map) return

      // 清除现有区域
      Object.values(zonePolygons).forEach(polygon => {
        if (polygon) map.removeLayer(polygon)
      })
      zonePolygons = {}

      // 添加所有区域到地图
      props.zones.forEach(zone => {
        try {
          const coords = typeof zone.coordinates === 'string' 
            ? JSON.parse(zone.coordinates) 
            : zone.coordinates
          
          if (coords && coords.length >= 3) {
            const latlngs = coords.map(c => [c.lat, c.lng])
            const polygon = L.polygon(latlngs, {
              color: '#409eff',
              weight: 2,
              opacity: 0.8,
              fillColor: '#409eff',
              fillOpacity: 0.2
            }).addTo(map)

            const area = zone.area >= 10000 
              ? `${(zone.area / 10000).toFixed(2)} 公顷`
              : `${zone.area.toFixed(2)} 平方米`

            polygon.bindPopup(`<b>${zone.name}</b><br/>面积: ${area}`)
            
            // 点击区域时选中
            polygon.on('click', () => {
              emit('zone-select', zone)
            })

            zonePolygons[zone.id] = polygon
          }
        } catch (error) {
          console.error('显示区域失败:', error, zone)
        }
      })
    }

    // 高亮选中的区域
    const highlightZone = (zoneId) => {
      // 重置之前选中的区域
      if (selectedPolygon) {
        selectedPolygon.setStyle({
          color: '#409eff',
          fillColor: '#409eff',
          fillOpacity: 0.2,
          weight: 2
        })
        selectedPolygon = null
      }

      // 如果 zoneId 为 null，则清除所有高亮
      if (!zoneId) {
        return
      }

      // 高亮新选中的区域
      const polygon = zonePolygons[zoneId]
      if (polygon) {
        selectedPolygon = polygon
        polygon.setStyle({
          color: '#67c23a',
          fillColor: '#67c23a',
          fillOpacity: 0.4,
          weight: 3
        })
        map.fitBounds(polygon.getBounds(), { padding: [50, 50] })
      }
    }

    // 移除区域
    const removeZone = (zoneId) => {
      if (zonePolygons[zoneId]) {
        map.removeLayer(zonePolygons[zoneId])
        delete zonePolygons[zoneId]
      }
    }

    // 监听props变化
    watch(() => props.zones, displayZones, { deep: true })
    watch(() => props.selectedZoneId, (newId) => {
      highlightZone(newId) // 无论是选中还是取消选中，都需要调用highlightZone来处理
    })
    watch(() => props.tempPoints, (newPoints) => {
      if (props.isCreatingZone && map) {
        // 添加新点的标记
        if (newPoints.length > tempMarkers.length) {
          const lastPoint = newPoints[newPoints.length - 1]
          addPointMarker(lastPoint.lat, lastPoint.lng, newPoints.length)
        }
        updateTempPolygon()
      }
    }, { deep: true })
    watch(() => props.isCreatingZone, (isCreating) => {
      if (!isCreating && map) {
        clearTempShapes()
      }
    })

    onMounted(() => {
      initMap()
    })

    onUnmounted(() => {
      if (map) {
        map.remove()
      }
    })

    // 暴露方法给父组件
    return {
      mapContainer,
      isLoading,
      clearTempShapes,
      removeZone
    }
  }
}
</script>

<style scoped>
.map-view {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  padding: 30px 40px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.map-loading p {
  margin-top: 12px;
  color: #666;
  font-size: 14px;
}
</style>

<style>
/* 全局样式：点标签 */
.point-label {
  background-color: rgba(255, 69, 0, 0.9) !important;
  border: none !important;
  color: white !important;
  font-size: 12px !important;
  font-weight: bold !important;
  padding: 4px 8px !important;
  border-radius: 4px !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
}

.point-label::before {
  border-top-color: rgba(255, 69, 0, 0.9) !important;
}
</style>
