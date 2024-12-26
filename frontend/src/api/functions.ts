import request from './request'
import type { ApiResponse, PublishNoteParams, PublishNoteResponse, HealthCheckResponse, WorkflowsResponse, GenerateImageParams, GenerateImageResponse, UploadImageResponse, GenerateCaptionParams, GenerateCaptionResponse, CreateWorkflowParams, UpdateWorkflowParams, WorkflowResponse } from './config'

export const publishNote = async (params: PublishNoteParams): Promise<ApiResponse<PublishNoteResponse>> => {
  return request.post<any, ApiResponse<PublishNoteResponse>>('/api/publish', params)
}

export const checkHealth = async (): Promise<ApiResponse> => {
  try {
    const response = await request.get<any, HealthCheckResponse>('/api/health')
    // 将后端响应转换为统一的 ApiResponse 格式
    return {
      success: response.data.status === 'healthy',
      message: response.data.message
    }
  } catch (error) {
    return {
      success: false,
      message: '服务连接失败'
    }
  }
}

export const generateImage = async (params: GenerateImageParams): Promise<ApiResponse<GenerateImageResponse>> => {
  return request.post<any, ApiResponse<GenerateImageResponse>>('/api/generate-image', params)
}

// 添加分页参数接口
interface ListImagesParams {
  page?: number;
  page_size?: number;
}

// 添加图片信息接口
interface ImageInfo {
  created_at: string;
  id: number;
  url: string;
  prompt: string;
}

// 修改返回数据接口，更新 images 类型
interface ListImagesResponse {
  images: ImageInfo[];
  pagination: {
    current_page: number;
    page_size: number;
    total_pages: number;
    total_images: number;
  };
}

// 修改 listImages 函数，支持分页参数
export const listImages = async (params?: ListImagesParams): Promise<ApiResponse<ListImagesResponse>> => {
  return request.get<any, ApiResponse<ListImagesResponse>>('/api/list-images', {
    params: {
      page: params?.page || 1,
      page_size: params?.page_size || 20
    }
  })
}

export interface TranslationResult {
  original_text: string
  translated_text: string
}

export interface EnhanceResult {
  prompt: string
}

export const translateText = async (text: string): Promise<ApiResponse<TranslationResult>> => {
  return request.post<any, ApiResponse<TranslationResult>>('/api/translate', {
    text
  })
}

export const enhancePrompt = async (prompt: string): Promise<ApiResponse<EnhanceResult>> => {
  return request.post<any, ApiResponse<EnhanceResult>>('/api/enhance-prompt', {
    prompt
  })
}

export const uploadImage = async (file: FormData): Promise<ApiResponse<UploadImageResponse>> => {
  return request.post<any, ApiResponse<UploadImageResponse>>('/api/upload-image', file, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const generateCaption = async (params: GenerateCaptionParams): Promise<ApiResponse<GenerateCaptionResponse>> => {
  return request.post<any, ApiResponse<GenerateCaptionResponse>>('/api/generate-caption', params)
}

export const createWorkflow = async (params: CreateWorkflowParams): Promise<ApiResponse<WorkflowResponse>> => {
  return request.post<any, ApiResponse<WorkflowResponse>>('/api/workflows', params)
}

export const updateWorkflow = async (id: string, params: UpdateWorkflowParams): Promise<ApiResponse<WorkflowResponse>> => {
  return request.put<any, ApiResponse<WorkflowResponse>>(`/api/workflows/${id}`, params)
}

export const deleteWorkflow = async (id: string): Promise<ApiResponse> => {
  return request.delete<any, ApiResponse>(`/api/workflows/${id}`)
}

// 添加工作流文件上传接口
interface UploadWorkflowResponse {
  id: number;
  name: string;
  original_name: string;
}

export const uploadWorkflow = async (file: FormData): Promise<ApiResponse<UploadWorkflowResponse>> => {
  return request.post<any, ApiResponse<UploadWorkflowResponse>>('/api/workflow/upload', file, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 添加工作流列表查询参数接口
interface ListWorkflowParams {
  page: number;
  per_page: number;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}

// 修改工作流列表响应接口
interface ListWorkflowResponse {
  workflows: Array<{
    id: number;
    original_name: string;
    preview_image: string;
    input_vars: string[];
    output_vars: string[];
    created_at: string;
    updated_at: string;
    status: boolean;
    file_size: number;
    variables_count: number;
  }>;
  pagination: {
    current_page: number;
    per_page: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

// 修改工作流列表查询方法
export const listWorkflow = async (params: ListWorkflowParams): Promise<ApiResponse<ListWorkflowResponse>> => {
  return request.get<any, ApiResponse<ListWorkflowResponse>>('/api/workflow/list', { params })
}

// 添加切换工作流状态的方法
export const toggleWorkflowStatus = async (id: number): Promise<ApiResponse<null>> => {
  return request.post<any, ApiResponse<null>>(`/api/workflow/${id}/toggle-status`)
}

// 添加工作流变量响应接口
interface WorkflowVariable {
  id: number;
  node_id: string;
  class_type: string;
  title: string;
  created_at: string;
}

interface GetWorkflowVariablesResponse {
  workflow: {
    id: number;
    original_name: string;
    status: boolean;
  };
  variables: WorkflowVariable[];
}

// 添加获取工作流变量的方法
export const getWorkflowVariables = async (id: number): Promise<ApiResponse<GetWorkflowVariablesResponse>> => {
  return request.get<any, ApiResponse<GetWorkflowVariablesResponse>>(`/api/workflow/${id}/variables`)
}

// 添加类型定义
interface WorkflowData {
  id: number
  name: string
  original_name: string
  created_at: string
  updated_at: string
  file_size: number
  status: boolean
  variables_count: number
}

interface PaginationData {
  total: number
  current_page: number
  per_page: number
}

interface ListWorkflowResponse {
  success: boolean
  message?: string
  data?: {
    workflows: WorkflowData[]
    pagination: PaginationData
  }
}

interface UploadWorkflowResponse {
  success: boolean
  message?: string
  data?: {
    id: number
    original_name: string
  }
}

// 添加更新工作流变量的函数
export async function updateWorkflowVars(
  workflowId: number, 
  inputVars: string[], 
  outputVars: string[],
  previewImage?: string
) {
  return await request.post(`/api/workflow/${workflowId}/update-vars`, {
    input_vars: inputVars,
    output_vars: outputVars,
    preview_image: previewImage
  })
} 