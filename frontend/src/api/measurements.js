import axios from 'axios'

// 始终走同域反向代理的 /api
const API_BASE_URL = '/api'

export const measurementsAPI = {
  getZoneMeasurements: async (zoneId, params = {}) => {
    const response = await axios.get(`${API_BASE_URL}/measurements/zone/${zoneId}`, { params })
    return response.data
  },

  getZoneChartData: async (zoneId) => {
    const response = await axios.get(`${API_BASE_URL}/measurements/zone/${zoneId}/chart`)
    return response.data
  },

  createMeasurement: async (measurementData) => {
    const response = await axios.post(`${API_BASE_URL}/measurements/`, measurementData)
    return response.data
  }
}