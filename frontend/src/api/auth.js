import axios from 'axios'

// 始终走同域反向代理的 /api
// 本地开发：Vite proxy 将 /api 转发到后端
// 生产/静态：Nginx 将 /api 反代到后端
const API_BASE_URL = '/api'

export const authAPI = {
  login: async (credentials) => {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, credentials, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      transformRequest: [(data) => {
        const formData = new URLSearchParams()
        formData.append('username', data.username)
        formData.append('password', data.password)
        return formData
      }]
    })
    return response.data
  },

  register: async (userData) => {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, userData)
    return response.data
  }
}