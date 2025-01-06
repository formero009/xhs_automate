<template>
  <div class="agent-page">
    <n-card class="agent-card">
      <template #header>
        <div class="card-header">
          <span>{{ formTitle }}</span>
          <div class="button-group">
            <n-button v-if="isEditing" @click="handleCancel">取消</n-button>
            <n-button type="primary" @click="handleSubmit">{{ submitButtonText }}</n-button>
          </div>
        </div>
      </template>

      <n-form 
        ref="formRef"
        :model="agentForm" 
        :rules="formRules"
        label-placement="left" 
        label-width="120"
      >
        <n-form-item label="托管名称" path="name">
          <n-input v-model:value="agentForm.name" placeholder="给你的托管起个名字" />
        </n-form-item>

        <n-form-item label="内容主题" path="topic">
          <n-input
            v-model:value="agentForm.topic"
            type="textarea"
            placeholder="描述你想要生成的内容主题和风格"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="发布账号" path="account_id">
          <n-select
            v-model:value="agentForm.account_id"
            placeholder="选择要发布的账号"
            :options="accounts.map(acc => ({
              label: acc.nickname || acc.username,
              value: acc.id.toString()
            }))"
          />
        </n-form-item>

        <n-form-item label="工作流" path="workflow_id">
          <n-select
            v-model:value="agentForm.workflow_id"
            placeholder="选择要使用的工作流"
            :options="workflows.map(wf => ({
              label: wf.name,
              value: wf.id,
              disabled: !wf.status
            }))"
          />
        </n-form-item>

        <n-form-item label="发布频率" path="schedule_type">
          <n-select
            v-model:value="agentForm.schedule_type"
            placeholder="选择发布频率类型"
            :options="[
              { label: '固定时间', value: 'fixed_time' },
              { label: '每天多次', value: 'times_per_day' },
              { label: '间隔天数', value: 'days_interval' },
              { label: '每周固定', value: 'weekly' }
            ]"
          />
        </n-form-item>

        <!-- 调度配置 -->
        <n-form-item label="调度设置" path="schedule_config">
          <!-- 固定时间 -->
          <template v-if="agentForm.schedule_type === 'fixed_time'">
            <n-time-picker
              v-model:value="scheduleTime"
              format="HH:mm"
              placeholder="选择每天执行时间"
              :default-value="getDefaultTime()"
            />
          </template>

          <!-- 每天多次 -->
          <template v-if="agentForm.schedule_type === 'times_per_day'">
            <n-input-number
              v-model:value="agentForm.schedule_config.times"
              :min="1"
              :max="24"
              :show-button="true"
              placeholder="每天执行次数"
            />
          </template>

          <!-- 间隔天数 -->
          <template v-if="agentForm.schedule_type === 'days_interval'">
            <div style="display: flex; gap: 12px; align-items: center">
              <n-input-number
                v-model:value="agentForm.schedule_config.days"
                :min="1"
                :show-button="true"
                placeholder="间隔天数"
                style="width: 120px"
              />
              <span>天</span>
              <n-time-picker
                v-model:value="scheduleTime"
                format="HH:mm"
                placeholder="选择执行时间"
                :default-value="getDefaultTime()"
              />
            </div>
          </template>

          <!-- 每周固定 -->
          <template v-if="agentForm.schedule_type === 'weekly'">
            <div style="display: flex; gap: 12px; align-items: center">
              <n-select
                v-model:value="agentForm.schedule_config.weekdays"
                multiple
                placeholder="选择星期"
                :options="[
                  { label: '周一', value: 0 },
                  { label: '周二', value: 1 },
                  { label: '周三', value: 2 },
                  { label: '周四', value: 3 },
                  { label: '周五', value: 4 },
                  { label: '周六', value: 5 },
                  { label: '周日', value: 6 }
                ]"
                style="width: 200px"
              />
              <n-time-picker
                v-model:value="scheduleTime"
                format="HH:mm"
                placeholder="选择执行时间"
                :default-value="getDefaultTime()"
              />
            </div>
          </template>
        </n-form-item>

        <n-form-item label="图片生成设置" path="image_count">
          <n-input-number
            v-model:value="agentForm.image_count"
            :min="1"
            :max="15"
            :show-button="true"
            placeholder="生成图片数量"
          />
        </n-form-item>

        <n-form-item label="高级设置">
          <n-collapse>
            <n-collapse-item title="提示词设置" name="1">
              <n-input
                v-model:value="agentForm.prompt_template"
                type="textarea"
                placeholder="自定义提示词模板"
                :rows="3"
              />
            </n-collapse-item>
            <n-collapse-item title="图片风格设置" name="2">
              <n-input
                v-model:value="agentForm.image_style"
                type="textarea"
                placeholder="定义图片生成风格"
                :rows="3"
              />
            </n-collapse-item>
          </n-collapse>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card class="agent-list" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>已创建的托管</span>
        </div>
      </template>

      <n-data-table
        :columns="columns"
        :data="agents"
        :pagination="{ pageSize: 10 }"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h, computed, watch } from 'vue'
import { useMessage, useDialog, NButton } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { createAgent, listAgents, toggleAgent, deleteAgent, listActiveUsers, updateAgent, listWorkflow } from '@/api/functions'
import type { Agent, AgentForm, ActiveUser } from '@/api/functions'
import type { ApiResponse } from '@/api/config'

interface Account extends ActiveUser {}

interface Workflow {
  id: number
  name: string
  original_name: string
  status: boolean
}

const message = useMessage()
const dialog = useDialog()

// 添加表单规则
const formRules = {
  name: {
    required: true,
    message: '请输入托管名称',
    trigger: ['blur', 'input']
  },
  account_id: {
    required: true,
    message: '请选择发布账号',
    trigger: ['blur', 'change']
  },
  schedule_type: {
    required: true,
    message: '请选择发布频率类型',
    trigger: ['blur', 'change']
  },
  image_count: {
    required: true,
    type: 'number',
    message: '请设置图片数量(1-15)',
    trigger: ['blur', 'change', 'input'],
    validator: (rule: any, value: number) => {
      if (typeof value !== 'number' || value < 1 || value > 15) {
        return new Error('图片数量必须在1-15之间')
      }
      return true
    }
  }
}

// 添加时间选择器的值
const scheduleTime = ref<number>(getDefaultTime())

// 获取默认时间（10:00）
function getDefaultTime(): number {
  const date = new Date()
  date.setHours(10, 0, 0, 0)
  return date.getTime()
}

// 转换时间为小时和分钟
function getTimeComponents(timestamp: number): { hour: number, minute: number } {
  const date = new Date(timestamp)
  return {
    hour: date.getHours(),
    minute: date.getMinutes()
  }
}

const agentForm = ref<AgentForm>({
  name: '',
  topic: '',
  account_id: '',
  schedule_type: 'fixed_time',
  schedule_config: {
    hour: 10,
    minute: 0
  },
  image_count: 3,
  prompt_template: '',
  image_style: '',
  workflow_id: undefined
})

// 监听调度类型变化，初始化对应的配置
watch(() => agentForm.value.schedule_type, (newType) => {
  if (newType === 'fixed_time') {
    const { hour, minute } = getTimeComponents(scheduleTime.value)
    agentForm.value.schedule_config = { hour, minute }
  } else if (newType === 'times_per_day') {
    agentForm.value.schedule_config = { times: 3 }
  } else if (newType === 'days_interval') {
    const { hour, minute } = getTimeComponents(scheduleTime.value)
    agentForm.value.schedule_config = { days: 1, hour, minute }
  } else if (newType === 'weekly') {
    const { hour, minute } = getTimeComponents(scheduleTime.value)
    agentForm.value.schedule_config = { weekdays: [0], hour, minute }
  }
})

// 监听时间选择器变化
watch(scheduleTime, (newTime) => {
  const { hour, minute } = getTimeComponents(newTime)
  if (agentForm.value.schedule_type === 'fixed_time') {
    agentForm.value.schedule_config = { hour, minute }
  } else if (agentForm.value.schedule_type === 'days_interval' || agentForm.value.schedule_type === 'weekly') {
    agentForm.value.schedule_config = {
      ...agentForm.value.schedule_config,
      hour,
      minute
    }
  }
})

const accounts = ref<Account[]>([])
const agents = ref<Agent[]>([])
const workflows = ref<Workflow[]>([])

// 添加编辑状态变量
const isEditing = ref(false)
const editingId = ref<number | null>(null)

// 修改表单标题和按钮
const formTitle = computed(() => isEditing.value ? '编辑托管' : '自动化托管配置')
const submitButtonText = computed(() => isEditing.value ? '保存修改' : '创建托管')

// 格式化调度显示
function formatSchedule(agent: Agent): string {
  const config = agent.schedule_config
  const time = (config.hour !== undefined && config.minute !== undefined) 
    ? `${config.hour.toString().padStart(2, '0')}:${config.minute.toString().padStart(2, '0')}` 
    : ''
  
  switch (agent.schedule_type) {
    case 'fixed_time':
      return `每天 ${time}`
    case 'times_per_day':
      return config.times ? `每天 ${config.times} 次` : '每天 1 次'
    case 'days_interval':
      return `每 ${config.days || 1} 天 ${time}`
    case 'weekly':
      const weekdays = config.weekdays?.map(d => ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][d]).join('、') || '周一'
      return `每周 ${weekdays} ${time}`
    default:
      return '-'
  }
}

const columns: DataTableColumns<Agent> = [
  { title: '名称', key: 'name' },
  { title: '状态', key: 'status' },
  { 
    title: '发布频率', 
    key: 'schedule',
    render(row) {
      return formatSchedule(row)
    }
  },
  { 
    title: '上次运行', 
    key: 'last_run',
    render(row) {
      return row.last_run ? new Date(row.last_run).toLocaleString() : '-'
    }
  },
  { 
    title: '下次运行', 
    key: 'next_run',
    render(row) {
      return row.next_run ? new Date(row.next_run).toLocaleString() : '-'
    }
  },
  {
    title: '操作',
    key: 'actions',
    render(row) {
      return h('div', [
        h(
          NButton,
          {
            size: 'small',
            type: row.status === 'running' ? 'warning' : 'success',
            onClick: () => {
              dialog.warning({
                title: '确认操作',
                content: `确定要${row.status === 'running' ? '暂停' : '启动'}该托管吗？`,
                positiveText: '确定',
                negativeText: '取消',
                onPositiveClick: () => {
                  handleToggleAgent(row)
                }
              })
            }
          },
          { default: () => row.status === 'running' ? '暂停' : '启动' }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'info',
            style: 'margin-left: 8px',
            onClick: () => handleEdit(row)
          },
          { default: () => '编辑' }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'error',
            style: 'margin-left: 8px',
            onClick: () => {
              dialog.warning({
                title: '确认删除',
                content: '删除后无法恢复，确定要删除该托管吗？',
                positiveText: '确定',
                negativeText: '取消',
                onPositiveClick: () => {
                  handleDeleteAgent(row)
                }
              })
            }
          },
          { default: () => '删除' }
        )
      ])
    }
  }
]

const formRef = ref<any>(null)

// 修改 handleCreateAgent 为统一的提交处理函数
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    const submitData = {
      ...agentForm.value,
      account_id: agentForm.value.account_id.toString()
    }
    
    const response = isEditing.value
      ? await updateAgent(editingId.value!, submitData)
      : await createAgent(submitData)
    
    if (response.success) {
      message.success(isEditing.value ? '托管修改成功' : '托管创建成功')
      loadAgents()
      // 重置表单
      handleCancel()
    } else {
      message.error(response.message || '操作失败')
    }
  } catch (e) {
    console.error(e)
    message.error('表单验证失败')
  }
}

// 添加编辑处理函数
const handleEdit = (agent: Agent) => {
  isEditing.value = true
  editingId.value = agent.id
  
  // 设置表单数据
  agentForm.value = {
    name: agent.name,
    topic: agent.topic || '',
    account_id: agent.account_id.toString(),
    schedule_type: agent.schedule_type,
    schedule_config: agent.schedule_config,
    image_count: agent.image_count,
    prompt_template: agent.prompt_template || '',
    image_style: agent.image_style || '',
    workflow_id: agent.workflow_id
  }
  
  // 设置时间选择器的值
  if (agent.schedule_config.hour !== undefined && agent.schedule_config.minute !== undefined) {
    const date = new Date()
    date.setHours(agent.schedule_config.hour, agent.schedule_config.minute, 0, 0)
    scheduleTime.value = date.getTime()
  }
}

// 添加取消编辑函数
const handleCancel = () => {
  isEditing.value = false
  editingId.value = null
  agentForm.value = {
    name: '',
    topic: '',
    account_id: '',
    schedule_type: 'fixed_time',
    schedule_config: {
      hour: 10,
      minute: 0
    },
    image_count: 3,
    prompt_template: '',
    image_style: '',
    workflow_id: undefined
  }
}

const handleToggleAgent = async (agent: Agent) => {
  try {
    const response = await toggleAgent(agent.id)
    if (response.success) {
      message.success(`托管${agent.status === 'running' ? '已暂停' : '已启动'}`)
      loadAgents()
    } else {
      message.error(response.message || '操作失败')
    }
  } catch (error: any) {
    message.error(error.message || '操作失败')
  }
}

const handleDeleteAgent = async (agent: Agent) => {
  try {
    const response = await deleteAgent(agent.id)
    if (response.success) {
      message.success('托管已删除')
      loadAgents()
    } else {
      message.error(response.message || '删除失败')
    }
  } catch (error: any) {
    message.error(error.message || '删除失败')
  }
}

const loadAgents = async () => {
  try {
    const response = await listAgents()
    if (response.success) {
      agents.value = response.data
    } else {
      message.error(response.message || '加载托管列表失败')
    }
  } catch (error: any) {
    message.error(error.message || '加载托管列表失败')
  }
}

const loadAccounts = async () => {
  try {
    const response = await listActiveUsers()
    if (response.success) {
      accounts.value = response.data
    } else {
      message.error(response.message || '加载账号列表失败')
    }
  } catch (error: any) {
    message.error(error.message || '加载账号列表失败')
  }
}

// Add workflow loading function
const loadWorkflows = async () => {
  try {
    const response = await listWorkflow({
      page: 1,
      per_page: 100,
      sort_by: 'created_at',
      sort_order: 'desc'
    })
    if (response.success) {
      workflows.value = response.data.workflows.map(w => ({
        id: w.id,
        name: w.original_name,
        original_name: w.original_name,
        status: w.status
      }))
    } else {
      message.error(response.message || '加载工作流列表失败')
    }
  } catch (error: any) {
    message.error(error.message || '加载工作流列表失败')
  }
}

onMounted(async () => {
  await Promise.all([
    loadAccounts(),
    loadAgents(),
    loadWorkflows()
  ])
})
</script>

<style scoped>
.agent-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.button-group {
  display: flex;
  gap: 8px;
}

.agent-card {
  margin-bottom: 20px;
}
</style> 