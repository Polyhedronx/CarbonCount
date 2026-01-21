import axios from 'axios'

// 始终走同域反向代理的 /api
const API_BASE_URL = '/api'

export const zonesAPI = {
  getZones: async () => {
    const response = await axios.get(`${API_BASE_URL}/zones/`)
    return response.data
  },

  createZone: async (zoneData) => {
    const response = await axios.post(`${API_BASE_URL}/zones/`, zoneData)
    return response.data
  },

  getZone: async (zoneId) => {
    const response = await axios.get(`${API_BASE_URL}/zones/${zoneId}`)
    return response.data
  },

  updateZone: async (zoneId, zoneData) => {
    const response = await axios.put(`${API_BASE_URL}/zones/${zoneId}`, zoneData)
    return response.data
  },

  deleteZone: async (zoneId) => {
    const response = await axios.delete(`${API_BASE_URL}/zones/${zoneId}`)
    return response.data
  }
}