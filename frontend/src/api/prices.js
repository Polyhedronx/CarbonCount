import axios from 'axios'

// 始终走同域反向代理的 /api
const API_BASE_URL = '/api'

export const pricesAPI = {
  getCurrentPrice: async () => {
    const response = await axios.get(`${API_BASE_URL}/prices/current`)
    return response.data
  },

  getPriceHistory: async (limit = 30) => {
    const response = await axios.get(`${API_BASE_URL}/prices/history`, { params: { limit } })
    return response.data
  },

  generateMockPrice: async () => {
    const response = await axios.post(`${API_BASE_URL}/prices/generate-mock`)
    return response.data
  }
}