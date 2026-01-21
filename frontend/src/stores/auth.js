import { defineStore } from 'pinia'
import axios from 'axios'
import { authAPI } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isAuthenticated: !!localStorage.getItem('token')
  }),

  getters: {
    getUser: (state) => state.user,
    getToken: (state) => state.token,
    isLoggedIn: (state) => state.isAuthenticated
  },

  actions: {
    async login(credentials) {
      try {
        const data = await authAPI.login(credentials)
        const { access_token } = data
        this.token = access_token
        this.isAuthenticated = true

        // 存储token
        localStorage.setItem('token', access_token)

        // 设置axios默认header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

        return { success: true }
      } catch (error) {
        console.error('Login failed:', error)
        return {
          success: false,
          error: error.response?.data?.detail || '登录失败'
        }
      }
    },

    async register(userData) {
      try {
        const data = await authAPI.register(userData)
        return { success: true, data }
      } catch (error) {
        console.error('Registration failed:', error)
        return {
          success: false,
          error: error.response?.data?.detail || '注册失败'
        }
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false

      // 清除本地存储
      localStorage.removeItem('token')

      // 清除axios默认header
      delete axios.defaults.headers.common['Authorization']
    },

    initializeAuth() {
      const token = localStorage.getItem('token')
      if (token) {
        this.token = token
        this.isAuthenticated = true
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      }
    }
  }
})