import request from './request'
import type { 
  ApiResponse, 
  PublishNoteParams, 
  PublishNoteResponse, 
  HealthCheckResponse, 
  GenerateImageParams, 
  GenerateImageResponse, 
  UploadImageResponse, 
  GenerateCaptionParams, 
  GenerateCaptionResponse,
  ListImagesParams,
  ListImagesResponse,
  TranslationResult,
  EnhanceResult,
  CreateWorkflowParams,
  UpdateWorkflowParams,
  WorkflowResponse,
  UploadWorkflowResponse,
  ListWorkflowParams,
  ListWorkflowResponse,
  GetWorkflowVariablesResponse,
  User,
  ActiveUser,
  Agent,
  AgentForm
} from './config'

export const publishNote = async (params: PublishNoteParams): Promise<ApiResponse<PublishNoteResponse>> => {
  return request.post<any, ApiResponse<PublishNoteResponse>>('/api/publish', params)
}

export const checkHealth = async (): Promise<ApiResponse> => {
  try {
    const response = await request.get<any, HealthCheckResponse>('/api/health')
    // 将后端响应转换为统一的 ApiResponse 格式
    return {
      success: response.data.status === 'healthy',
      message: response.data.message,
      data: {
        status: response.data.status,
        message: response.data.message,
        comfyui_status: response.data.comfyui_status
      }
    }
  } catch (error) {
    return {
      success: false,
      message: '服务连接失败',
      data: {
        status: 'error',
        message: '服务连接失败',
        comfyui_status: {
          running: false,
          message: '无法连接到服务'
        }
      }
    }
  }
}

export const generateImage = async (params: GenerateImageParams): Promise<ApiResponse<GenerateImageResponse>> => {
  return request.post<any, ApiResponse<GenerateImageResponse>>('/api/generate-image', params)
}

export const listImages = async (params?: ListImagesParams): Promise<ApiResponse<ListImagesResponse>> => {
  return request.get<any, ApiResponse<ListImagesResponse>>('/api/list-images', {
    params: {
      page: params?.page || 1,
      page_size: params?.page_size || 20
    }
  })
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

export const uploadWorkflow = async (file: FormData): Promise<ApiResponse<UploadWorkflowResponse>> => {
  return request.post<any, ApiResponse<UploadWorkflowResponse>>('/api/workflow/upload', file, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const listWorkflow = async (params: ListWorkflowParams): Promise<ApiResponse<ListWorkflowResponse>> => {
  return request.get<any, ApiResponse<ListWorkflowResponse>>('/api/workflow/list', { params })
}

export const toggleWorkflowStatus = async (id: number): Promise<ApiResponse<null>> => {
  return request.post<any, ApiResponse<null>>(`/api/workflow/${id}/toggle-status`)
}

export const getWorkflowVariables = async (id: number): Promise<ApiResponse<GetWorkflowVariablesResponse>> => {
  return request.get<any, ApiResponse<GetWorkflowVariablesResponse>>(`/api/workflow/${id}/variables`)
}

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

// User Management APIs
export async function listUsers() {
  return request.get('/api/user/list')
}

export async function listActiveUsers(): Promise<ApiResponse<ActiveUser[]>> {
  return request.get<any, ApiResponse<ActiveUser[]>>('/api/user/active')
}

export async function createUser(data: {
  username: string
  nickname?: string
  cookie: string
}) {
  return request.post('/api/user/create', data)
}

export async function updateUser(userId: number, data: {
  username?: string
  nickname?: string
  cookie?: string
  status?: boolean
}) {
  return request.put(`/api/user/update/${userId}`, data)
}

export async function deleteUser(userId: number) {
  return request.delete(`/api/user/delete/${userId}`)
}

// Agent APIs
export async function createAgent(data: AgentForm): Promise<ApiResponse<Agent>> {
  return request.post<any, ApiResponse<Agent>>('/api/agent/agents', data)
}

export async function listAgents(): Promise<ApiResponse<Agent[]>> {
  return request.get<any, ApiResponse<Agent[]>>('/api/agent/agents')
}

export async function toggleAgent(agentId: number): Promise<ApiResponse<Agent>> {
  return request.put<any, ApiResponse<Agent>>(`/api/agent/agents/${agentId}/toggle`)
}

export async function deleteAgent(agentId: number): Promise<ApiResponse<void>> {
  return request.delete<any, ApiResponse<void>>(`/api/agent/agents/${agentId}`)
}

export async function updateAgent(agentId: number, data: AgentForm): Promise<ApiResponse<Agent>> {
  return request.put<any, ApiResponse<Agent>>(`/api/agent/agents/${agentId}`, data)
} 