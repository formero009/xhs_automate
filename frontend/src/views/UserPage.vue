<template>
  <div class="user-page">
    <n-card title="用户管理">
      <template #header-extra>
        <n-button type="primary" @click="showCreateModal = true">
          新增用户
        </n-button>
      </template>

      <n-data-table
        :columns="columns"
        :data="users"
        :loading="loading"
      />
    </n-card>

    <!-- Create User Modal -->
    <n-modal v-model:show="showCreateModal" preset="dialog" title="新增用户">
      <n-form
        ref="createFormRef"
        :model="createForm"
        :rules="formRules"
      >
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="createForm.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="昵称" path="nickname">
          <n-input v-model:value="createForm.nickname" placeholder="请输入昵称" />
        </n-form-item>
        <n-form-item label="Cookie" path="cookie">
          <n-input
            v-model:value="createForm.cookie"
            type="textarea"
            placeholder="请输入小红书Cookie"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showCreateModal = false">取消</n-button>
        <n-button type="primary" :loading="submitting" @click="handleCreate">
          确定
        </n-button>
      </template>
    </n-modal>

    <!-- Edit User Modal -->
    <n-modal v-model:show="showEditModal" preset="dialog" title="编辑用户">
      <n-form
        ref="editFormRef"
        :model="editForm"
        :rules="formRules"
      >
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="editForm.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="昵称" path="nickname">
          <n-input v-model:value="editForm.nickname" placeholder="请输入昵称" />
        </n-form-item>
        <n-form-item label="Cookie" path="cookie">
          <n-input
            v-model:value="editForm.cookie"
            type="textarea"
            placeholder="请输入小红书Cookie"
          />
        </n-form-item>
        <n-form-item label="状态" path="status">
          <n-switch v-model:value="editForm.status" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showEditModal = false">取消</n-button>
        <n-button type="primary" :loading="submitting" @click="handleEdit">
          确定
        </n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useMessage, NButton } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { listUsers, createUser, updateUser, deleteUser } from '../api/functions'

interface User {
  id: number
  username: string
  nickname: string
  cookie: string
  status: boolean
  created_at: string
}

const message = useMessage()

// Table data
const users = ref<User[]>([])
const loading = ref(false)

// Modal visibility
const showCreateModal = ref(false)
const showEditModal = ref(false)
const submitting = ref(false)

// Form data
const createForm = ref({
  username: '',
  nickname: '',
  cookie: ''
})

const editForm = ref({
  id: 0,
  username: '',
  nickname: '',
  cookie: '',
  status: true
})

// Form rules
const formRules = {
  username: {
    required: true,
    message: '请输入用户名',
    trigger: 'blur'
  },
  cookie: {
    required: true,
    message: '请输入Cookie',
    trigger: 'blur'
  }
}

// Table columns
const columns: DataTableColumns = [
  {
    title: '用户名',
    key: 'username'
  },
  {
    title: '昵称',
    key: 'nickname'
  },
  {
    title: '状态',
    key: 'status',
    render(row: User) {
      return row.status ? '启用' : '禁用'
    }
  },
  {
    title: '创建时间',
    key: 'created_at'
  },
  {
    title: '操作',
    key: 'actions',
    render(row: User) {
      return [
        h(
          NButton,
          {
            text: true,
            type: 'primary',
            onClick: () => handleEditClick(row)
          },
          { default: () => '编辑' }
        ),
        h(
          NButton,
          {
            text: true,
            type: 'error',
            onClick: () => handleDelete(row.id)
          },
          { default: () => '删除' }
        )
      ]
    }
  }
]

// Methods
const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await listUsers()
    if (res.success) {
      users.value = res.data
    }
  } catch (error) {
    message.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  submitting.value = true
  try {
    const res = await createUser(createForm.value)
    if (res.success) {
      message.success('创建成功')
      showCreateModal.value = false
      createForm.value = {
        username: '',
        nickname: '',
        cookie: ''
      }
      fetchUsers()
    }
  } catch (error) {
    message.error('创建失败')
  } finally {
    submitting.value = false
  }
}

const handleEditClick = (row: User) => {
  editForm.value = { ...row }
  showEditModal.value = true
}

const handleEdit = async () => {
  submitting.value = true
  try {
    const res = await updateUser(editForm.value.id, {
      username: editForm.value.username,
      nickname: editForm.value.nickname,
      cookie: editForm.value.cookie,
      status: editForm.value.status
    })
    if (res.success) {
      message.success('更新成功')
      showEditModal.value = false
      fetchUsers()
    }
  } catch (error) {
    message.error('更新失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id: number) => {
  try {
    const res = await deleteUser(id)
    if (res.success) {
      message.success('删除成功')
      fetchUsers()
    }
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-page {
  padding: 24px;
}
</style> 