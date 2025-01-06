import axios from 'axios'
import type { ApiResponse } from './config'
import { API_ENDPOINT } from './config'

// 创建 axios 实例
const request = axios.create({
  baseURL: API_ENDPOINT,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
request.interceptors.response.use((response) => {
    const apiResponse: ApiResponse = {
      success: true,
      data: response.data.data,
      message: response.data.message
    }
    return apiResponse
  },
  (error) => {
    const apiResponse: ApiResponse = {
      success: false,
      data: null,
      message: error.response?.data?.message || error.message
    }
    return Promise.reject(apiResponse)
  }
)

export default request 