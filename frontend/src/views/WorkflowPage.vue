<template>
  <div class="workflow-management">
    <n-card title="工作流管理">
      <template #header-extra>
        <n-space>
          <n-input-group>
            <n-input
              v-model:value="searchName"
              placeholder="请输入工作流名称"
              @keyup.enter="handleSearch"
            />
            <n-button type="primary" @click="handleSearch">
              <template #icon>
                <n-icon><Search /></n-icon>
              </template>
              查询
            </n-button>
          </n-input-group>
          <n-button type="primary" @click="handleAdd">
            <template #icon>
              <n-icon><AddCircleOutline /></n-icon>
            </template>
            新增工作流
          </n-button>
        </n-space>
      </template>

      <n-data-table
        :columns="columns"
        :data="tableData"
        :pagination="pagination"
        :bordered="true"
        :single-line="false"
        :scroll-x="1200"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </n-card>

    <!-- 新增工作流������� -->
    <n-modal
      v-model:show="showAddModal"
      preset="card"
      :title="modalTitle"
      :style="{ width: '600px' }"
    >
      <n-form
        ref="formRef"
        :model="formModel"
        :rules="rules"
        label-placement="left"
        label-width="100"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="工作流名称" path="name">
          <n-input v-model:value="formModel.name" placeholder="请输入工作流名称" />
        </n-form-item>
        
        <n-form-item label="预览图片" path="previewImage">
          <n-upload
            accept="image/*"
            :max="1"
            list-type="image-card"
            :default-file-list="uploadFiles"
            :custom-request="customRequest"
            :show-remove-button="true"
            @remove="handleRemovePreview"
          >
          </n-upload>
          <n-text depth="3" style="margin-top: 8px; display: block">
            支持 jpg、png、gif 等常见图片格式
          </n-text>
        </n-form-item>

        <n-form-item label="入参列表" path="inputs">
          <n-select
            v-model:value="formModel.inputs"
            multiple
            :options="inputVariableOptions"
            placeholder="请选择入参"
          />
        </n-form-item>

        <n-form-item label="出参列表" path="outputs">
          <n-select
            v-model:value="formModel.outputs"
            multiple
            :options="outputVariableOptions"
            placeholder="请择出参"
          />
        </n-form-item>

        <n-form-item label="工作流文件" path="workflowFile">
          <n-upload
            accept=".json"
            :max="1"
            :custom-request="handleWorkflowUpload"
            :default-file-list="workflowFiles"
          >
            <n-button>上传工作流文件</n-button>
          </n-upload>
          <n-text depth="3" style="margin-top: 8px; display: block">
            请上传JSON格式的工作流配置文件
          </n-text>
        </n-form-item>

        <n-form-item label="调试信息">
          <pre>{{ JSON.stringify(formModel, null, 2) }}</pre>
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="handleCloseModal">取消</n-button>
          <n-button type="primary" @click="handleSubmit">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, h, onMounted, computed } from 'vue'
import type { FormValidationError } from 'naive-ui'
import { useMessage, useDialog, DataTableColumns, FormRules, FormInst, NButton, NSpace, NIcon, NImage, UploadFileInfo } from 'naive-ui'
import { AddCircleOutline, ImageOutline, Search, CreateOutline, PowerOutline } from '@vicons/ionicons5'
import { uploadImage, uploadWorkflow, listWorkflow, toggleWorkflowStatus, getWorkflowVariables, updateWorkflowVars } from '../api/functions'

interface FormModel {
  name: string;
  previewImage: string;
  inputs: number[];
  outputs: number[];
}

interface RowData {
  id: number;
  name: string;
  originalName: string;
  original_name: string;
  createTime: string;
  updateTime: string;
  created_at?: string;
  updated_at?: string;
  file_size: number;
  status: boolean;
  variablesCount: number;
  variables_count: number;
  input_vars: string[];
  output_vars: string[];
  preview_image: string;
}

interface UploadFile {
  id: string;
  name: string;
  status: 'finished';
  url?: string;
}

export default defineComponent({
  name: 'WorkflowManagement',
  components: {
    AddCircleOutline,
    ImageOutline,
    Search,
    CreateOutline,
    PowerOutline,
    NImage
  },
  setup() {
    const message = useMessage()
    const dialog = useDialog()
    const tableData = ref<RowData[]>([])
    const pagination = ref({
      page: 1,
      pageSize: 10,
      showSizePicker: true,
      pageSizes: [10, 20, 30, 50],
      itemCount: 0,
      onChange: (page: number) => {
        pagination.value.page = page
        fetchData()
      },
      onUpdatePageSize: (pageSize: number) => {
        pagination.value.pageSize = pageSize
        pagination.value.page = 1
        fetchData()
      }
    })

    const formatDate = (dateStr: string | undefined) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.getFullYear() + '年' + 
             (date.getMonth() + 1) + '月' + 
             date.getDate() + '日 ' + 
             date.getHours().toString().padStart(2, '0') + ':' + 
             date.getMinutes().toString().padStart(2, '0') + ':' + 
             date.getSeconds().toString().padStart(2, '0')
    }

    const columns: DataTableColumns<RowData> = [
      {
        title: 'ID',
        key: 'id',
        width: 50,
        align: 'center'
      },
      {
        title: '预览图',
        key: 'preview_image',
        width: 100,
        align: 'center',
        render(row) {
          if (!row.preview_image) {
            return h('span', '无')
          }
          
          // 获取处理后的图片URL
          const imageUrl = getImageUrl(row.preview_image)
          console.log('Image URL:', imageUrl) // 调试用
          
          return h(
            NImage,
            {
              src: imageUrl,
              width: 50,
              height: 50,
              style: {
                objectFit: 'cover',
                borderRadius: '4px'
              },
              previewDisabled: false,
              showToolbarTooltip: true,
              // 添加错误处理
              onError: () => {
                console.error('Image load failed:', imageUrl)
              }
            }
          )
        }
      },
      {
        title: '工作流名称',
        key: 'originalName',
        width: 160,
        ellipsis: {
          tooltip: true
        }
      },
      {
        title: '变量数量',
        key: 'variablesCount',
        width: 80,
        align: 'center',
        render(row) {
          return h('span', row.variablesCount || row.variables_count || 0)
        }
      },
      {
        title: '文件大小',
        key: 'fileSize',
        width: 80,
        align: 'center',
        render(row) {
          const size = row.file_size ? `${(row.file_size / 1024).toFixed(2)} KB` : '0 KB'
          return h(
            'span',
            size
          )
        }
      },
      {
        title: '状态',
        key: 'status',
        width: 60,
        align: 'center',
        render(row) {
          return h(
            'n-tag',
            {
              type: row.status ? 'success' : 'error'
            },
            { default: () => row.status ? '启用' : '禁用' }
          )
        }
      },
      {
        title: '创建时间',
        key: 'createTime',
        width: 160,
        align: 'center',
        ellipsis: {
          tooltip: true
        },
        render(row) {
          return formatDate(row.createTime || row.created_at)
        }
      },
      {
        title: '入参数量',
        key: 'inputVarsCount',
        width: 80,
        align: 'center',
        render(row) {
          return h('span', row.input_vars?.length || 0)
        }
      },
      {
        title: '出参数量',
        key: 'outputVarsCount',
        width: 80,
        align: 'center',
        render(row) {
          return h('span', row.output_vars?.length || 0)
        }
      },
      {
        title: '操作',
        key: 'actions',
        width: 100,
        align: 'center',
        fixed: 'right',
        render(row) {
          return h(
            NSpace,
            {
              align: 'center',
              justify: 'center'
            },
            {
              default: () => [
                h(
                  NButton,
                  {
                    size: 'small',
                    type: 'primary',
                    onClick: () => handleEdit(row)
                  },
                  {
                    default: () => h(NIcon, null, { default: () => h(CreateOutline) })
                  }
                ),
                h(
                  NButton,
                  {
                    size: 'small',
                    type: row.status ? 'error' : 'success',
                    onClick: () => handleToggleStatus(row)
                  },
                  {
                    default: () => h(NIcon, null, { default: () => h(PowerOutline) })
                  }
                )
              ]
            }
          )
        }
      }
    ]

    const searchName = ref('')

    // 获取工作流列表���据
    const fetchData = async () => {
      try {
        const res = await listWorkflow({
          page: pagination.value.page,
          per_page: pagination.value.pageSize,
          sort_by: 'created_at',
          sort_order: 'desc',
          search: searchName.value || undefined
        })
        
        if (res.success && res.data) {
          console.log('API response:', res.data)
          tableData.value = res.data.workflows.map(item => ({
            id: item.id,
            name: item.original_name,
            originalName: item.original_name,
            original_name: item.original_name,
            createTime: item.created_at,
            updateTime: item.updated_at,
            created_at: item.created_at,
            updated_at: item.updated_at,
            file_size: item.file_size,
            status: item.status,
            variablesCount: item.variables_count,
            variables_count: item.variables_count,
            input_vars: item.input_vars,
            output_vars: item.output_vars,
            preview_image: item.preview_image
          }))
          
          console.log('Processed table data:', tableData.value)
          // 更新分页信息
          pagination.value.itemCount = res.data.pagination.total
          pagination.value.page = res.data.pagination.current_page
          pagination.value.pageSize = res.data.pagination.per_page
        } else {
          message.error(res.message || '获取数据失败')
        }
      } catch (error) {
        console.error('Fetch error:', error)
        message.error('获取数据失败')
      }
    }

    // 新增相关的状态和法
    const showAddModal = ref(false)
    const formRef = ref<FormInst | null>(null)
    const formModel = ref<FormModel>({
      name: '',
      previewImage: '',
      inputs: [],
      outputs: []
    })

    const rules: FormRules = {
      name: [
        { required: true, message: '请输入工作流名称', trigger: ['blur', 'input'] }
      ],
      previewImage: [
        { required: true, message: '请上传预览图片', trigger: ['change', 'input'] }
      ],
      inputs: [
        { required: true, type: 'array', min: 1, message: '请至少添加一个入参', trigger: ['change', 'input'] }
      ],
      outputs: [
        { required: true, type: 'array', min: 1, message: '请至少添加一个出参', trigger: ['change', 'input'] }
      ]
    }

    const uploadFiles = ref<UploadFile[]>([])
    const workflowFiles = ref<UploadFile[]>([])

    // 修改 getImageUrl 函数
    const getImageUrl = (path: string) => {
      if (!path) return ''
      if (path.startsWith('http')) return path
      // 直接返回完整路径
      return path
    }

    // 修改 customRequest 方法
    const customRequest = async ({ file, onFinish, onError }: { file: { file: File }, onFinish: () => void, onError: () => void }) => {
      const formData = new FormData()
      formData.append('file', file.file)
      
      try {
        const res = await uploadImage(formData)
        if (res.success && res.data?.path) {
          // 保存原始路径到表单
          formModel.value.previewImage = res.data.path
          // 使用处理后的完整路径显示图片
          const previewImageUrl = res.data.path
          console.log('Upload success, image URL:', previewImageUrl) // 调试用
          
          uploadFiles.value = [{
            id: String(Date.now()),
            name: res.data.filename || file.file.name,
            status: 'finished',
            url: previewImageUrl
          }]
          formRef.value?.validate(['previewImage'])
          onFinish()
          message.success('上传成功')
        } else {
          onError()
          message.error(res.message || '上传失败')
        }
      } catch (error) {
        console.error('Upload error:', error)
        onError()
        message.error('上传失败')
      }
    }

    const handleWorkflowUpload = async ({ file, onFinish, onError }: { file: { file: File }, onFinish: () => void, onError: () => void }) => {
      const formData = new FormData()
      formData.append('file', file.file)
      
      try {
        const res = await uploadWorkflow(formData)
        if (res.success && res.data) {
          // 更新表单数据
          formModel.value.name = res.data.original_name
          currentWorkflowId.value = res.data.id
          // 获取工作流变量
          await loadWorkflowVariables(res.data.id)
          onFinish()
          message.success('工作流文件上传成功')
        } else {
          onError()
          message.error(res.message || '请上传一个JSON格式的API工作流文件')
        }
      } catch (error) {
        onError()
        message.error('请上传一个JSON格式的API工作流文件')
      }
    }

    const resetForm = () => {
      formModel.value = {
        name: '',
        previewImage: '',
        inputs: [],
        outputs: []
      }
      uploadFiles.value = []
      workflowFiles.value = []
      inputVariableOptions.value = []
      outputVariableOptions.value = []
      currentWorkflowId.value = null
    }

    // 添加关闭弹窗时的处理
    const handleCloseModal = () => {
      showAddModal.value = false
      resetForm()
    }

    // 修改现有的 handleAdd 方法
    const handleAdd = () => {
      // reset form
      resetForm()
      showAddModal.value = true
    }

    const handleSubmit = () => {
      formRef.value?.validate((errors: Array<FormValidationError[]> | undefined) => {
        if (!errors) {
          (async () => {
            try {
              if (!currentWorkflowId.value) {
                message.error('请先上传工作流文件')
                return
              }

              // 检查必填字段
              if (!formModel.value.previewImage || formModel.value.previewImage.trim() === '') {
                message.error('请上传预览图')
                return
              }

              // 提交给后端的数据使用 id
              const res = await updateWorkflowVars(
                currentWorkflowId.value,
                formModel.value.inputs,
                formModel.value.outputs,
                formModel.value.previewImage
              )

              if (res.success) {
                message.success('保存成功')
                showAddModal.value = false
                resetForm()
                fetchData()
              } else {
                message.error(res.message || '保存失败')
              }
            } catch (error) {
              console.error('Submit error:', error)
              message.error('保存失败')
            }
          })()
        }
      })
    }

    // 编辑工作流
    const handleEdit = async (row: RowData) => {
      try {
        console.log('Edit row data:', row)
        // 先清空当前状态
        resetForm()
        
        // 设置工作流 ID 和打开模态框
        currentWorkflowId.value = row.id
        showAddModal.value = true
        
        // 加载工作流变量
        await loadWorkflowVariables(row.id)
        
        // 设置表单数据
        formModel.value = {
          name: row.original_name || row.name,
          previewImage: row.preview_image || '',
          inputs: row.input_vars?.map(Number) || [],
          outputs: row.output_vars?.map(Number) || []
        }
        
        console.log('Preview image path:', row.preview_image)
        
        // 立即设置预览图
        if (row.preview_image) {
          const imageUrl = getImageUrl(row.preview_image)
          console.log('Processed image URL:', imageUrl)
          
          // 设置上传文件列表，显示已有的预览图
          uploadFiles.value = [{
            id: String(Date.now()),
            name: 'preview.png',
            status: 'finished',
            url: imageUrl
          }]
          
          console.log('Upload files:', uploadFiles.value[0].url)
        } else {
          uploadFiles.value = []
        }
        
        // 设置工作流文件
        workflowFiles.value = [{
          id: String(Date.now()),
          name: row.original_name || row.name,
          status: 'finished'
        }]
      } catch (error) {
        console.error('Edit error:', error)
        message.error('加载工作流数据失败')
        handleCloseModal()
      }
    }

    // 切换状态
    const handleToggleStatus = (row: RowData) => {
      const action = row.status ? '禁用' : '启用'
      dialog.warning({
        title: '提示',
        content: `确认${action}该工作流？`,
        positiveText: '确定',
        negativeText: '取消',
        onPositiveClick: async () => {
          try {
            const res = await toggleWorkflowStatus(row.id)
            if (res.success) {
              message.success(`${action}成功`)
              fetchData()  // 刷新列表
            } else {
              message.error(res.message || `${action}失败`)
            }
          } catch (error) {
            message.error(`${action}失败`)
          }
        }
      })
    }

    const handlePageChange = (page: number) => {
      pagination.value.page = page
    }

    const handlePageSizeChange = (pageSize: number) => {
      pagination.value.pageSize = pageSize
      pagination.value.page = 1
    }

    // 添加搜索法
    const handleSearch = () => {
      pagination.value.page = 1  // 重置页码
      fetchData()
    }

    // 添加变量选项
    const inputVariableOptions = ref<Array<{ label: string; value: number }>>([])
    const outputVariableOptions = ref<Array<{ label: string; value: number }>>([])
    const currentWorkflowId = ref<number | null>(null)

    // 修改 loadWorkflowVariables 方法
    const loadWorkflowVariables = async (workflowId: number) => {
      try {
        const res = await getWorkflowVariables(workflowId)
        if (res.success && res.data) {
          // 添加排序逻辑
          const sortedVariables = [...res.data.variables].sort((a, b) => {
            return a.id - b.id
          })

          // 分别过滤输入和输出变量
          const inputVariables = sortedVariables.filter(v => v.param_type === 'input')
          const outputVariables = sortedVariables.filter(v => v.param_type === 'output')

          // 只更新下拉框选项，不自动选中
          inputVariableOptions.value = inputVariables.map(variable => ({
            label: `${variable.node_id}-${variable.title}(${variable.description})(${variable.value_type})`,
            value: variable.id
          }))

          outputVariableOptions.value = outputVariables.map(variable => ({
            label: `${variable.node_id}-${variable.title}(${variable.description})`,
            value: variable.id
          }))

          // 只在编辑模式下设置已选择的变量
          if (res.data.workflow && res.data.workflow.input_vars && res.data.workflow.output_vars) {
            formModel.value.inputs = res.data.workflow.input_vars.map(Number)
            formModel.value.outputs = res.data.workflow.output_vars.map(Number)
          }
          // 新增模式下保持输入输出为空数组
          else if (!currentWorkflowId.value) {
            formModel.value.inputs = []
            formModel.value.outputs = []
          }
        } else {
          message.error('获取工作流变量失败')
        }
      } catch (error) {
        console.error('Load variables error:', error)
        message.error('获取工作流变量失败')
      }
    }

    onMounted(() => {
      fetchData()
    })

    // 修改弹窗标题，根据是否是编辑模式显示不同的标题
    const modalTitle = computed(() => {
      return currentWorkflowId.value ? '编辑工作流' : '新增工作流'
    })

    const handleRemovePreview = () => {
      formModel.value.previewImage = ''
      uploadFiles.value = []
    }

    return {
      tableData,
      columns,
      pagination,
      handleAdd,
      handlePageChange,
      handlePageSizeChange,
      showAddModal,
      formRef,
      formModel,
      rules,
      uploadFiles,
      customRequest,
      handleSubmit,
      workflowFiles,
      handleWorkflowUpload,
      searchName,
      handleSearch,
      handleToggleStatus,
      formatDate,
      inputVariableOptions,
      outputVariableOptions,
      currentWorkflowId,
      modalTitle,
      getImageUrl,
      handleCloseModal,
      handleRemovePreview
    }
  }
})
</script>

<style scoped>
.workflow-management {
  padding: 20px;
  height: 100%;
}

:deep(.n-data-table) {
  max-width: 100%;
}
</style> 