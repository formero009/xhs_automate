// API 配置
export const API_ENDPOINT = '/api'

// 健康检查响应类型
export interface HealthCheckResponse {
  message: string
  success: boolean
  data: {
    status: string
    message: string
  }
}

// API 响应类型定义
export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
}

// 笔记发布参数类型
export interface PublishNoteParams {
  title: string
  description: string
  cookie: string
  is_private: boolean
  images: string[]
  topics: string[]
}

// 笔记发布响应类型
export interface PublishNoteResponse {
  // 根据实际后端返回数据结构定义
  [key: string]: any
}

// 图片生成参数类型
export interface GenerateImageParams {
  workflow_id: number
  variables: Array<{
    id: number
    value: string | number | boolean
  }>
  output_vars: number[]
}

// 图片生成响应类型
export interface GenerateImageResponse {
  message: string
  result: any
} 

// 图片上传响应类型
export interface UploadImageResponse {
  filename: string
  path: string
}

// 生成文案参数类型
export interface GenerateCaptionParams {
  prompt: string
}

// 生成文案响应类型
export interface GenerateCaptionResponse {
  caption: string
}