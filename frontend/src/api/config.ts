// API 配置
export const API_ENDPOINT = '/api'

// API 响应类型定义
export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data: T
}

// 健康检查响应类型
export interface HealthCheckResponse extends ApiResponse<{
  status: string
  message: string
  comfyui_status: {
    running: boolean
    message: string
  }
}> {}

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
  note_id: string
  url: string
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
  url: string
  path: string
}

// 生成文案参数类型
export interface GenerateCaptionParams {
  prompt: string
}

// 生成文案响应类型
export interface GenerateCaptionResponse {
  caption: string
  title: string
  topics: string[]
}

// User interfaces
export interface User {
  id: number
  username: string
  nickname?: string
  status: boolean
  created_at: string
  updated_at: string
}

export interface ActiveUser {
  id: number
  username: string
  nickname?: string
}

// Agent interfaces
export interface ScheduleConfig {
  hour?: number
  minute?: number
  times?: number
  days?: number
  weekdays?: number[]
}

export interface AgentForm {
  name: string
  topic: string
  account_id: string
  schedule_type: 'fixed_time' | 'times_per_day' | 'days_interval' | 'weekly'
  schedule_config: ScheduleConfig
  image_count: number
  prompt_template?: string
  image_style?: string
  workflow_id?: number
}

export interface Agent {
  id: number
  name: string
  topic: string
  account_id: string
  schedule_type: 'fixed_time' | 'times_per_day' | 'days_interval' | 'weekly'
  schedule_config: ScheduleConfig
  image_count: number
  prompt_template?: string
  image_style?: string
  workflow_id?: number
  status: 'running' | 'paused' | 'error'
  last_run?: string
  next_run?: string
  created_at: string
  updated_at: string
}

// Image interfaces
export interface ListImagesParams {
  page?: number
  page_size?: number
}

export interface ImageInfo {
  created_at: string
  id: number
  url: string
  variables: any[]
}

export interface ListImagesResponse {
  images: ImageInfo[]
  pagination: {
    current_page: number
    page_size: number
    total_pages: number
    total_images: number
  }
}

// Translation interfaces
export interface TranslationResult {
  original_text: string
  translated_text: string
}

export interface EnhanceResult {
  prompt: string
}

// Workflow interfaces
export interface CreateWorkflowParams {
  name: string
}

export interface UpdateWorkflowParams {
  name: string
}

export interface WorkflowResponse {
  id: number
  name: string
}

export interface UploadWorkflowResponse {
  id: number
  name: string
  original_name: string
}

export interface ListWorkflowParams {
  page: number
  per_page: number
  search?: string
  sort_by?: string
  sort_order?: string
}

export interface WorkflowData {
  id: number
  name: string
  original_name: string
  created_at: string
  updated_at: string
  file_size: number
  status: boolean
  variables_count: number
}

export interface PaginationData {
  total: number
  current_page: number
  per_page: number
}

export interface ListWorkflowResponse {
  workflows: Array<{
    id: number
    original_name: string
    preview_image: string
    input_vars: string[]
    output_vars: string[]
    created_at: string
    updated_at: string
    status: boolean
    file_size: number
    variables_count: number
  }>
  pagination: {
    current_page: number
    per_page: number
    total: number
    pages: number
    has_next: boolean
    has_prev: boolean
  }
}

export interface WorkflowVariable {
  id: number
  node_id: string
  class_type: string
  title: string
  created_at: string
  description: string
  param_type: string
  value_path: string
  value_type: string
}

export interface GetWorkflowVariablesResponse {
  workflow: {
    id: number
    input_vars: number[]
    output_vars: number[]
    original_name: string
    preview_image: string
    status: boolean
  }
  variables: WorkflowVariable[]
}

export interface UserCookieResponse {
  cookie: string
}