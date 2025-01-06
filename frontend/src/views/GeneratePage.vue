<template>
  <div class="generate-page">
    <h2>内容生成</h2>
    <n-message-provider>
      <n-grid x-gap="24" cols="2">
        <!-- 左侧生成表单 -->
        <n-grid-item span="1">
          <n-card size="large" class="form-card">
            <n-form
              ref="formRef"
              :model="formData"
              label-placement="left"
              label-width="auto"
              require-mark-placement="right-hanging"
              size="large"
            >
              <!-- 工作流选择 -->
              <n-form-item label="工作流选择" path="workflow_id">
                <n-select
                  v-model:value="formData.workflow_id"
                  :options="workflows.map(w => ({ 
                    label: w.name, 
                    value: w.id,
                    disabled: !w.status 
                  }))"
                  placeholder="请选择工作流"
                  clearable
                  @update:value="handleWorkflowChange"
                />
              </n-form-item>

              <!-- 动态表单部分 -->
              <template v-for="(variables, groupType) in groupedInputVariables" :key="groupType">
                <n-card
                  :title="groupLabels[groupType]"
                  size="small"
                  class="input-group-card"
                >
                  <n-space vertical :size="12">
                    <template v-if="groupType.endsWith('-text')">
                      <!-- 文本输入框垂直排列 -->
                      <n-form-item
                        v-for="variable in variables"
                        :key="variable.id"
                        :label="variable.title.split(' ').slice(1).join(' ')"
                        :path="variable.value_path"
                      >
                        <n-input
                          v-model:value="dynamicFormData[variable.id]"
                          type="textarea"
                          :placeholder="variable.description"
                          :autosize="{
                            minRows: 3,
                            maxRows: 10
                          }"
                        />
                        <template #feedback>
                          {{ variable.description }}
                        </template>
                      </n-form-item>
                    </template>
                    
                    <template v-else>
                      <!-- 其他类型的输入框使用网格布局 -->
                      <n-grid :cols="variables.length > 1 ? variables.length : 1" :x-gap="12">
                        <n-grid-item
                          v-for="variable in variables"
                          :key="variable.id"
                          :span="1"
                        >
                          <n-form-item
                            :label="variable.title.split(' ').slice(1).join(' ')"
                            :path="variable.value_path"
                          >
                            <template v-if="groupType.endsWith('-number')">
                              <n-space vertical :size="4" style="width: 100%">
                                <n-input-number
                                  v-model:value="dynamicFormData[variable.id]"
                                  :placeholder="variable.description"
                                  class="full-width"
                                />
                                <n-space v-if="variable.description?.toLowerCase().includes('种子') || variable.value_path?.toLowerCase().includes('seed')" align="center" justify="end" :size="8">
                                  <span style="font-size: 12px; color: #666">自动随机</span>
                                  <n-switch
                                    v-model:value="autoRandomSeeds[variable.id]"
                                    size="small"
                                  />
                                </n-space>
                              </n-space>
                            </template>
                            
                            <template v-else-if="groupType.endsWith('-switch')">
                              <n-switch
                                v-model:value="dynamicFormData[variable.id]"
                              />
                            </template>
                            
                            <template #feedback>
                              {{ variable.description }}
                            </template>
                          </n-form-item>
                        </n-grid-item>
                      </n-grid>
                    </template>
                  </n-space>
                </n-card>
              </template>

              <!-- 生成按钮 -->
              <n-space justify="center" align="center">
                <n-button
                  type="primary"
                  size="large"
                  :loading="isGenerating"
                  :disabled="isGenerating"
                  @click="handleGenerate"
                >
                  {{ isGenerating ? '生成中...' : '生成图片' }}
                </n-button>
                <n-button
                  type="error"
                  size="large"
                  secondary
                  @click="clearCache"
                >
                  清除缓存
                </n-button>
              </n-space>
            </n-form>
          </n-card>
        </n-grid-item>

        <!-- 右侧图片展示 -->
        <n-grid-item span="1">
          <n-card title="生成历史" size="medium" class="history-card">
            <template #header-extra>
              <n-space>
                <n-text v-if="selectedImages.length > 0">
                  已选择 {{ selectedImages.length }}/9 张
                </n-text>
                <n-button
                  v-if="selectedImages.length > 0"
                  type="error"
                  secondary
                  @click="clearSelection"
                >
                  取消选中
                </n-button>
                <n-button
                  type="primary"
                  secondary
                  @click="loadHistoryImages"
                >
                  刷新
                </n-button>
              </n-space>
            </template>

            <div class="history-content">
              <n-scrollbar>
                <n-grid
                  :cols="3"
                  :x-gap="12"
                  :y-gap="12"
                  responsive="screen"
                >
                  <n-grid-item
                    v-for="(image, index) in displayImages"
                    :key="index"
                  >
                    <n-card
                      :class="['image-card', { selected: isImageSelected(image) }]"
                      :bordered="false"
                      size="small"
                    >
                      <template v-if="image.loading">
                        <div class="image-wrapper">
                          <n-spin size="large">
                            <template #description>
                              生成中...
                            </template>
                          </n-spin>
                        </div>
                      </template>
                      <template v-else>
                        <div class="image-wrapper">
                          <n-image
                            :src="getImageUrl(image)"
                            :alt="`图片 ${index + 1}`"
                            object-fit="cover"
                            lazy
                            style="opacity: 1"
                          />
                          <n-button
                            quaternary
                            circle
                            class="select-button"
                            @click.stop="toggleImageSelection(image)"
                          >
                            <template #icon>
                              <n-icon>
                                <svg v-if="isImageSelected(image)" viewBox="0 0 24 24">
                                  <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
                                </svg>
                                <svg v-else viewBox="0 0 24 24">
                                  <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                                </svg>
                              </n-icon>
                            </template>
                          </n-button>
                        </div>
                        <n-space justify="space-between" align="center" size="small">
                          <n-text depth="3">#{{ pagination.totalImages - ((pagination.currentPage - 1) * pagination.pageSize + index) }}</n-text>
                          <n-text depth="3">{{ formatTime(image.timestamp) }}</n-text>
                        </n-space>
                      </template>
                    </n-card>
                  </n-grid-item>
                </n-grid>

                <n-empty
                  v-if="!loadingImagePlaceholder && displayImages.length === 0"
                  description="还没有生成任何图片"
                >
                  <template #icon>
                    <n-icon>
                      <svg viewBox="0 0 24 24">
                        <path fill="currentColor" d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                      </svg>
                    </n-icon>
                  </template>
                </n-empty>
              </n-scrollbar>
            </div>

            <n-pagination
              v-model:page="pagination.currentPage"
              v-model:page-size="pagination.pageSize"
              :page-count="pagination.totalPages"
              :page-sizes="[12, 20, 32, 48]"
              show-size-picker
              :page-slot="4"
              @update:page="handlePageChange"
              @update:page-size="handlePageSizeChange"
            />

            <n-space
              v-if="selectedImages.length > 0"
              justify="center"
              style="margin-top: 16px;"
            >
              <n-button
                v-if="selectedImages.length > 0"
                type="success"
                @click="handlePublish"
              >
                发布选中图片
              </n-button>
              <n-button
                type="warning"
                @click="generateCombinedImage"
              >
                生成组合图
              </n-button>
            </n-space>
          </n-card>
        </n-grid-item>
      </n-grid>
    </n-message-provider>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useMessage } from 'naive-ui'
import { 
  listWorkflow, 
  generateImage, 
  listImages,
  generateCaption,
  getWorkflowVariables
} from '@/api/functions'
import type { WorkflowVariable } from '@/api/config'

interface HistoryImage {
  url: string
  loading?: boolean
  timestamp?: number | string
  id?: number
  created_at?: string
  variables?: any[]
}

interface FormData {
  workflow_id: number | null
  workflow_name: string
}

export default defineComponent({
  setup() {
    const message = useMessage()
    return {
      message,
    }
  },
  data() {
    return {
      STORAGE_KEY: 'generate_form_cache',
      GENERATING_KEY: 'generate_status_cache',
      formData: {
        workflow_id: null,
        workflow_name: ''
      } as FormData,
      workflows: [] as Array<{
        id: number;
        name: string;
        status: boolean;
      }>,
      isGenerating: false,
      historyImages: [] as HistoryImage[],
      loadingImagePlaceholder: null as string | null,
      selectedImages: [] as string[],
      selectedMap: new Map<string, boolean>(),
      isProcessing: false,
      pagination: {
        currentPage: 1,
        pageSize: 20,
        totalPages: 1,
        totalImages: 0
      },
      workflowVariables: [] as WorkflowVariable[],
      workflowInputVars: [] as number[],
      workflowOutputVars: [] as number[],
      dynamicFormData: {} as Record<string, any>,
      autoRandomSeeds: {} as Record<number, boolean>,
    }
  },
  async created() {
    try {
      // 1. 先从缓存中获取工作流 ID
      const cached = localStorage.getItem(this.STORAGE_KEY)
      const cachedData = cached ? JSON.parse(cached) : null
      const cachedWorkflowId = cachedData?.workflow_id

      // 初始化自动随机种子的状态
      this.autoRandomSeeds = {}
      
      // 2. 加载工作流列表
      await this.loadWorkflows()

      // 3. 如果有缓存的工作流 ID 且该工作流存在，则加载它
      if (cachedWorkflowId && this.workflows.find(w => w.id === cachedWorkflowId)) {
        await this.loadWorkflowVariables(cachedWorkflowId)
        // 恢复缓存的表单数据
        if (cachedData.dynamicFormData) {
          const validVariableIds = this.inputVariables.map(v => v.id)
          const filteredFormData: Record<string, any> = {}
          for (const [key, value] of Object.entries(cachedData.dynamicFormData)) {
            if (validVariableIds.includes(Number(key))) {
              filteredFormData[key] = value
            }
          }
          this.dynamicFormData = filteredFormData
        }
      }

      // 4. 检查是否有来自主题页面的提示词
      const themePrompt = localStorage.getItem('theme_prompt')
      if (themePrompt) {
        // 找到正向提示词的变量ID
        const positivePromptVariable = this.inputVariables.find(v => {
          const titleMatch = v.title?.toLowerCase().includes('正向提示词')
          const descMatch = v.description?.toLowerCase().includes('正向提示词')
          const pathMatch = v.value_path?.toLowerCase().includes('positive')
          return titleMatch || descMatch || pathMatch
        })

        if (positivePromptVariable) {
          this.dynamicFormData[positivePromptVariable.id] = themePrompt
          // 使用后清除缓存
          localStorage.removeItem('theme_prompt')
          this.message.success('已自动填入提示词')
        } else {
          this.message.warning('未找到正向提示词输入框，请手动填写')
        }
      }

      // 5. 加载历史图片
      await this.loadHistoryImages()

      // 6. 检查是否有未完成的生成任务
      const generatingStatus = localStorage.getItem(this.GENERATING_KEY)
      if (generatingStatus === 'true') {
        this.checkGenerateResult()
      }
    } catch (error) {
      this.handleError(error, '初始化失败')
    }
  },
  computed: {
    displayImages(): any[] {
      const images = this.historyImages.map(img => ({
        url: typeof img === 'string' ? img : img.url,
        timestamp: typeof img === 'string' ? undefined : img.timestamp
      }))
      if (this.loadingImagePlaceholder) {
        return [{ loading: true }, ...images]
      }
      return images
    },
    inputVariables(): WorkflowVariable[] {
      return this.workflowVariables.filter(v => 
        this.workflowInputVars.includes(v.id) && v.value_path
      )
    },
    groupedInputVariables(): Record<string, WorkflowVariable[]> {
      const groups: Record<string, WorkflowVariable[]> = {}
      
      // 首先按类型分组
      this.inputVariables.forEach(variable => {
        const inputType = this.getInputType(variable)
        const prefix = variable.title.split(' ')[0]
        const key = `${prefix}-${inputType}`
        
        if (!groups[key]) {
          groups[key] = []
        }
        groups[key].push(variable)
      })

      // 定义类型的优先级
      const typeOrder = {
        'text': 0,    // 文本框最优先
        'number': 1,  // 数字输入框次之
        'switch': 2   // 开关放最后
      }

      // 按照类型优先级和前缀排序
      return Object.fromEntries(
        Object.entries(groups)
          .sort(([a], [b]) => {
            const [aPrefix, aType] = a.split('-')
            const [bPrefix, bType] = b.split('-')
            
            // 首先按类型优先级排序
            const aTypeOrder = typeOrder[aType as keyof typeof typeOrder] ?? 999
            const bTypeOrder = typeOrder[bType as keyof typeof typeOrder] ?? 999
            if (aTypeOrder !== bTypeOrder) {
              return aTypeOrder - bTypeOrder
            }
            
            // 同类型则按前缀排序
            return aPrefix.localeCompare(bPrefix)
          })
      )
    },
    groupLabels(): Record<string, string> {
      return Object.keys(this.groupedInputVariables).reduce((acc, key) => {
        const [prefix] = key.split('-')
        acc[key] = prefix
        return acc
      }, {} as Record<string, string>)
    }
  },
  methods: {
    handleError(error: any, defaultMessage: string) {
      console.error(error)
      const errorMessage = error?.message || defaultMessage
      this.message.error(errorMessage)
    },

    async loadWorkflows() {
      try {
        const response = await listWorkflow({
          page: 1,
          per_page: 100,
          sort_by: 'created_at',
          sort_order: 'desc'
        })
        
        if (response.success && response.data) {
          this.workflows = response.data.workflows
            .filter(w => w.status)
            .map(w => ({
              id: w.id,
              name: w.original_name.replace('.json', ''),
              status: w.status
            }))
          
          if (!this.formData.workflow_id && this.workflows.length > 0) {
            this.formData.workflow_id = this.workflows[0].id
            this.formData.workflow_name = this.workflows[0].name
            await this.loadWorkflowVariables(this.workflows[0].id)
          }
        } else {
          throw new Error(response.message || '加载工作流失败')
        }
      } catch (error) {
        this.handleError(error, '加载工作流失败')
      }
    },

    async loadFromCache() {
      // 这个方法可以删除，因为逻辑已经移到 created 钩子中
    },

    saveToCache() {
      const cacheData = {
        workflow_id: this.formData.workflow_id,
        workflow_name: this.formData.workflow_name,
        dynamicFormData: { ...this.dynamicFormData }  // 创建一个副本以确保数据完整性
      }
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(cacheData))
    },

    clearCache() {
      localStorage.removeItem(this.STORAGE_KEY)
      localStorage.removeItem(this.GENERATING_KEY)
      
      // 重置所有相关状态
      this.formData = {
        workflow_id: null,
        workflow_name: ''
      }
      this.dynamicFormData = {}
      this.workflowVariables = []
      this.workflowInputVars = []
      
      // 如果有默认工作流，加载它
      if (this.workflows.length > 0) {
        this.formData.workflow_id = this.workflows[0].id
        this.formData.workflow_name = this.workflows[0].name
        this.loadWorkflowVariables(this.workflows[0].id)
      }
      
      this.message.success('缓存已清除')
    },

    async handleGenerate() {
      if (!this.validateForm()) {
        return
      }

      this.isGenerating = true
      this.loadingImagePlaceholder = 'loading'
      this.saveGeneratingStatus(true)
      
      try {
        // 为所有开启了自动随机的种子生成新的随机数
        this.inputVariables.forEach(variable => {
          if (
            this.autoRandomSeeds[variable.id] && 
            (variable.description?.toLowerCase().includes('种子') || 
             variable.value_path?.toLowerCase().includes('seed'))
          ) {
            // 生成一个随机数 (0 到 1000000000 之间)
            this.dynamicFormData[variable.id] = Math.floor(Math.random() * 1000000000)
          }
        })

        // Build request data
        const requestData = {
          workflow_id: this.formData.workflow_id!,
          variables: this.inputVariables.map(variable => ({
            id: variable.id,
            value: this.dynamicFormData[variable.id]
          })),
          output_vars: this.workflowOutputVars
        }
        
        this.saveToCache()
        const response = await generateImage(requestData)
        if (response.success && response.data) {
          await this.loadHistoryImages()
          this.message.success('图片生成成功')
        } else {
          throw new Error(response.message || '生成失败')
        }
      } catch (error: any) {
        this.message.error(error.message || '生成失败，请重试')
      } finally {
        this.isGenerating = false
        this.loadingImagePlaceholder = null
        this.saveGeneratingStatus(false)
      }
    },

    validateForm() {
      if (!this.formData.workflow_id) {
        this.message.error('请选择工作流')
        return false
      }
      
      for (const variable of this.inputVariables) {
        const value = this.dynamicFormData[variable.id]
        if (value === undefined || value === '') {
          this.message.error(`请填写${variable.title}`)
          return false
        }
      }
      
      return true
    },

    getImageUrl(image: any): string {
      if (image.loading) {
        return ''
      }
      const filename = image.url || image
      if (filename.startsWith('http')) {
        return filename
      }
      return filename.startsWith('/') ? filename : `/images/${filename}`
    },

    async loadHistoryImages() {
      try {
        const response = await listImages({
          page: this.pagination.currentPage,
          page_size: this.pagination.pageSize
        })
        
        if (response.success && response.data) {
          this.historyImages = response.data.images.map(image => ({
            url: image.url,
            id: image.id,
            created_at: image.created_at,
            variables: image.variables
          }))
          
          const { pagination } = response.data
          this.pagination = {
            currentPage: pagination.current_page,
            pageSize: pagination.page_size,
            totalPages: pagination.total_pages,
            totalImages: pagination.total_images
          }
        }
      } catch (error: any) {
        console.error('加载历史图片失败:', error)
        this.message.error('加载历史图片失败')
      }
    },

    formatTime(timestamp: string | number | undefined): string {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleString('zh-CN', {
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    toggleImageSelection(image: any) {
      const imageUrl = this.getImageUrl(image)
      const index = this.selectedImages.indexOf(imageUrl)
      
      if (index === -1) {
        if (this.selectedImages.length >= 9) {
          this.message.warning('最多只能选9张图片')
          return
        }
        
        const fullImage = this.historyImages.find(img => this.getImageUrl(img) === imageUrl)
        
        if (fullImage?.variables) {
          // 检查是否有不同的变量值
          let hasChanges = false
          let newFormData: Record<string, any> = {}
          
          // 遍历图片中的变量
          for (const [varId, varValues] of Object.entries(fullImage.variables)) {
            const variableId = Number(varId)
            // 找到对应的变量定义
            const variable = this.inputVariables.find(v => v.id === variableId)
            if (variable) {
              // 获取变量的值（假设每个变量对象只有一个值）
              const value = Object.values(varValues)[0]
              if (this.dynamicFormData[variableId] !== value) {
                hasChanges = true
                newFormData[variableId] = value
              }
            }
          }
          this.selectedImages.push(imageUrl)
          this.selectedMap.set(imageUrl, true)
          // if (hasChanges) {
          //   window.$dialog.warning({
          //     title: '变量值不同',
          //     content: '选中图片的变量值与当前表单不同，是否更新表单？',
          //     positiveText: '更新',
          //     negativeText: '保持当前',
          //     onPositiveClick: () => {
          //       this.dynamicFormData = {
          //         ...this.dynamicFormData,
          //         ...newFormData
          //       }
          //       this.selectedImages.push(imageUrl)
          //       this.selectedMap.set(imageUrl, true)
          //       this.message.success('已更新表单值')
          //     },
          //     onNegativeClick: () => {
          //       this.selectedImages.push(imageUrl)
          //       this.selectedMap.set(imageUrl, true)
          //       this.message.info('保持当前表单值不变')
          //     }
          //   })
          // } else {
          //   this.selectedImages.push(imageUrl)
          //   this.selectedMap.set(imageUrl, true)
          // }
        } else {
          this.selectedImages.push(imageUrl)
          this.selectedMap.set(imageUrl, true)
        }
      } else {
        this.selectedImages.splice(index, 1)
        this.selectedMap.delete(imageUrl)
      }
    },

    isImageSelected(image: any): boolean {
      return this.selectedImages.includes(this.getImageUrl(image))
    },

    clearSelection() {
      this.selectedImages = []
      this.selectedMap.clear()
    },

    async handlePublish() {
      if (this.isProcessing) return;
      this.isProcessing = true;
      
      try {
        // 检查是否有选中的图片
        if (this.selectedImages.length === 0) {
          throw new Error('请选择要发布的图片');
        }

        // 从当前表单中获取正向提示词
        let prompt = '';
        const positivePromptVariable = this.inputVariables.find(v => v.description === '正向提示词' || v.title == '正向提示词');
        
        if (positivePromptVariable && this.dynamicFormData[positivePromptVariable.id]) {
          prompt = this.dynamicFormData[positivePromptVariable.id];
        }

        if (!prompt) {
          throw new Error('请先填写正向提示词');
        }

        this.message.info('正在生成文案...');
        const requestData = {
          prompt: prompt
        };
        
        const response = await generateCaption(requestData);
        if (!response.success) {
          throw new Error(response.message || '生成文案失败');
        }

        const { data } = response;
        if (!data) {
          throw new Error('生成文案失败：未获取到数据');
        }

        const publishData = {
          images: this.selectedImages,
          title: data.title || '新笔记',
          description: '',
          topics: data.topics || []
        };

        // 保存到本地存储
        localStorage.setItem('selectedImages', JSON.stringify(publishData.images));
        localStorage.setItem('xhs_Title', JSON.stringify(publishData.title));
        localStorage.setItem('xhs_Caption', JSON.stringify(publishData.description));
        localStorage.setItem('xhs_Topics', JSON.stringify(publishData.topics));

        this.message.success('文案生成成功，即将跳转到发布页面');

        // 延迟跳转到发布页面
        setTimeout(() => {
          this.$router.push('/publish');
        }, 1500);

      } catch (error: any) {
        console.error('处理发布失败:', error);
        this.message.error(error.message || '生成文案失败，请重试');
      } finally {
        this.isProcessing = false;
      }
    },

    async generateCombinedImage() {
      if (this.selectedImages.length === 0) return;

      const imageSize = 300;
      const gap = 10;
      const imagesPerRow = Math.ceil(Math.sqrt(this.selectedImages.length));
      const totalRows = Math.ceil(this.selectedImages.length / imagesPerRow);
      
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = imagesPerRow * imageSize + (imagesPerRow - 1) * gap;
      canvas.height = totalRows * imageSize + (totalRows - 1) * gap;
      
      if (ctx) {
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }
      
      const loadImage = (url: string) => {
        return new Promise((resolve, reject) => {
          const img = new Image();
          img.crossOrigin = 'anonymous';
          img.onload = () => resolve(img);
          img.onerror = reject;
          img.src = url;
        });
      };

      try {
        this.message.info('正在生成组合图片...');

        for (let i = 0; i < this.selectedImages.length; i++) {
          const row = Math.floor(i / imagesPerRow);
          const col = i % imagesPerRow;
          const x = col * (imageSize + gap);
          const y = row * (imageSize + gap);
          
          if (ctx) {
            const img = await loadImage(this.selectedImages[i]);
            if (img instanceof HTMLImageElement) {
              ctx.drawImage(img, x, y, imageSize, imageSize);
            }
          }
        }
        
        if (ctx) {
          const dataUrl = canvas.toDataURL('image/png');
          const link = document.createElement('a');
          link.download = `combined-images-${Date.now()}.png`;
          link.href = dataUrl;
          link.click();
        }
          
        this.message.success('组合图已生成并下载');
      } catch (error) {
        console.error('生成组合图片失败:', error);
        this.message.error('生成组合图片失败');
      }
    },

    saveGeneratingStatus(status: boolean) {
      if (status) {
        localStorage.setItem(this.GENERATING_KEY, 'true')
      } else {
        localStorage.removeItem(this.GENERATING_KEY)
      }
    },

    loadGeneratingStatus() {
      const status = localStorage.getItem(this.GENERATING_KEY)
      if (status === 'true') {
        this.isGenerating = true
        this.loadingImagePlaceholder = 'loading'
        this.checkGenerateResult()
      }
    },

    async checkGenerateResult() {
      if (!this.isGenerating) return
      
      try {
        const response = await listImages({
          page: 1,
          page_size: 1
        })
        
        if (response.success && response.data) {
          const totalImages = response.data.pagination.total_images
          if (totalImages > this.pagination.totalImages) {
            this.message.success('图片生成成功')
            await this.loadHistoryImages()
            this.isGenerating = false
            this.loadingImagePlaceholder = null
            this.saveGeneratingStatus(false)
          } else if (this.isGenerating) {
            setTimeout(() => this.checkGenerateResult(), 3000)
          }
        }
      } catch (error) {
        this.handleError(error, '检查生成结果失败')
        this.resetGeneratingStatus()
      }
    },

    resetGeneratingStatus() {
      this.isGenerating = false
      this.loadingImagePlaceholder = null
      this.saveGeneratingStatus(false)
    },

    handlePageChange(page: number) {
      this.pagination.currentPage = page
      this.loadHistoryImages()
    },

    handlePageSizeChange(pageSize: number) {
      this.pagination.pageSize = pageSize
      this.pagination.currentPage = 1
      this.loadHistoryImages()
    },

    async handleWorkflowChange(workflowId: number | null) {
      if (workflowId) {
        const workflow = this.workflows.find(w => w.id === workflowId)
        if (workflow) {
          this.formData.workflow_name = workflow.name
          this.workflowVariables = []
          this.workflowInputVars = []
          this.workflowOutputVars = []
          // 切换工作流时清空表单数据
          this.dynamicFormData = {}
          await this.loadWorkflowVariables(workflowId)
          this.saveToCache()
        }
      } else {
        this.formData.workflow_name = ''
        this.workflowVariables = []
        this.workflowInputVars = []
        this.workflowOutputVars = []
        this.dynamicFormData = {}
        this.saveToCache()
      }
    },

    async loadWorkflowVariables(workflowId: number) {
      try {
        const response = await getWorkflowVariables(workflowId)
        if (response.success && response.data) {
          this.workflowVariables = response.data.variables
          this.workflowInputVars = response.data.workflow.input_vars
          this.workflowOutputVars = response.data.workflow.output_vars
          // 只在没有缓存数据时初始化默认值
          if (Object.keys(this.dynamicFormData).length === 0) {
            this.initDynamicFormData()
          }
        }
      } catch (error) {
        this.handleError(error, '加载工作流变量失败')
      }
    },

    initDynamicFormData() {
      const newFormData = {}
      this.inputVariables.forEach(variable => {
        switch (variable.value_type) {
          case 'long':
          case 'integer':
            newFormData[variable.id] = 0
            break
          case 'float':
          case 'double':
            newFormData[variable.id] = 0.0
            break
          case 'boolean':
            newFormData[variable.id] = false
            break
          case 'string':
          default:
            newFormData[variable.id] = ''
        }
      })
      this.dynamicFormData = newFormData
    },

    getInputType(variable: WorkflowVariable) {
      switch (variable.value_type) {
        case 'long':
        case 'integer':
        case 'float':
        case 'double':
          return 'number'
        case 'boolean':
          return 'switch'
        default:
          return 'text'
      }
    }
  },
  mounted() {
    const savedPrompt = localStorage.getItem('promptText')
    if (savedPrompt) {
      this.formData.positive_prompt = savedPrompt
      localStorage.removeItem('promptText')
      this.saveToCache()
    }
  },
  beforeUnmount() {
    if (this.isGenerating) {
      this.saveGeneratingStatus(true)
    }
  },
  watch: {
    'formData': {
      handler() {
        this.saveToCache()
      },
      deep: true
    },
    'dynamicFormData': {
      handler() {
        this.saveToCache()
      },
      deep: true
    }
  }
})
</script>

<style scoped>
.generate-page {
  min-height: calc(80vh - 64px);
  margin: 12px;
  padding: 0 12px;
}

/* 历史记录片式 */
.history-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.history-card :deep(.n-card__content) {
  flex: 1;
  overflow: hidden;
  padding: 16px !important;
  display: flex;
  flex-direction: column;
}

/* 修改历史内容区域的样式 */
.history-content {
  flex: 1;
  min-height: 0; /* 重要：确保flex子元素可以正确滚动 */
  position: relative;
}

/* 滚动器样式 */
:deep(.history-content .n-scrollbar) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

:deep(.n-scrollbar-container) {
  padding: 0 4px; /* 添加一些水平内边距 */
}

/* 确保网格布局正确显示 */
:deep(.n-grid) {
  width: 100%;
  margin: 0;
  height: 100%;
}

/* 优化图片网格的间距 */
:deep(.n-grid-item) {
  padding: 8px;
}

/* 图网格布局 */
.image-wrapper {
  position: relative;
  padding-top: 100%; /* 保持1:1的宽高比 */
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
  cursor: pointer;
}

:deep(.n-image) {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 图片卡片样式 */
.image-card {
  position: relative;
  transition: all 0.3s ease;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* 选中态下的卡片样式 */
.image-card.selected {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
}

/* 选择按钮样式 */
.select-button {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
  opacity: 0;
  transition: all 0.2s ease;
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.image-card:hover .select-button {
  opacity: 1;
}

/* 选中状态下的按钮样式 */
.image-card.selected .select-button {
  opacity: 1;
  background-color: var(--primary-color);
  color: white;
  border: none;
}

/* 加载状态样式 */
.image-card :deep(.n-spin) {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.image-card :deep(.n-spin-description) {
  margin-top: 8px;
  color: #606266;
}

/* 时间和序号样式 */
:deep(.n-space) {
  padding: 8px;
}

:deep(.n-text) {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

/* 响应式布局 */
@media (max-width: 1280px) {
  :deep(.n-grid) {
    --n-cols: 2 !important;
  }
}

@media (max-width: 768px) {
  :deep(.n-grid) {
    --n-cols: 1 !important;
  }
  
  .history-card {
    min-height: 400px;
  }
}

/* 添加预览按钮样式 */
.preview-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  opacity: 0;
  transition: all 0.2s ease;
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.1);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-wrapper:hover .preview-button {
  opacity: 1;
}

.preview-button:hover {
  background-color: rgba(255, 255, 255, 1);
  transform: translate(-50%, -50%) scale(1.1);
}

/* 加图片加载过效果 */
.image-wrapper :deep(.n-image) {
  opacity: 0;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.image-wrapper :deep(.n-image.loaded) {
  opacity: 1;
}

/* 优化动端体验 */
@media (hover: none) {
  .select-button,
  .preview-button {
    opacity: 0.8; /* 在触摸设备上始终显示按钮 */
  }
  
  .image-card:hover {
    transform: none; /* 移除悬浮效果 */
  }
}

/* 暗色主题 */
:root[data-theme='dark'] {
  .image-card {
    border-color: rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.05);
  }
  
  .preview-button,
  .select-button {
    background-color: rgba(0, 0, 0, 0.6);
    border-color: rgba(255, 255, 255, 0.2);
  }
}

/* 优化滚动条样式 */
.result-content {
  scrollbar-width: thin;
  scrollbar-color: var(--scrollbar-color) transparent;
}

.result-content::-webkit-scrollbar {
  width: 6px;
}

.result-content::-webkit-scrollbar-thumb {
  background-color: var(--scrollbar-color);
  border-radius: 3px;
}

/* 添加加载状态的平滑过渡 */
.loading-placeholder {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 0.8; }
  100% { opacity: 0.6; }
}

/* 添加分页样式 */
:deep(.n-pagination) {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

/* 调整历史内容区域的高度，分页腾出空间 */
.history-content {
  flex: 1;
  min-height: 0;
  max-height: calc(100vh - 300px); /* 整这个值以适应你的布局 */
  position: relative;
}

/* 输入分组卡片样式 */
.input-group-card {
  margin-bottom: 16px;
}

.input-group-card :deep(.n-card__content) {
  padding: 16px;
}

.input-group-card :deep(.n-card__title) {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-color-1);
}

/* 文本框组样式优化 */
.input-group-card :deep(.n-space) {
  width: 100%;
}

/* 调整文本框间距 */
.input-group-card :deep(.n-form-item) {
  margin-bottom: 8px;
}

.input-group-card :deep(.n-form-item:last-child) {
  margin-bottom: 0;
}

/* 文本框样式优化 */
:deep(.n-input__textarea) {
  min-height: 80px;
  resize: vertical;
}

/* 确保所有输入框占满宽度 */
:deep(.n-input),
:deep(.n-input-number),
.full-width {
  width: 100%;
}

/* 表单项标签样式 */
:deep(.n-form-item-label) {
  font-size: 14px;
  font-weight: 500;
}

/* 响应式布局调整 */
@media (max-width: 768px) {
  .input-group-card {
    margin-bottom: 12px;
  }
  
  :deep(.n-grid) {
    --n-cols: 1 !important;
  }
}
</style>