<template>
  <div class="publish-page">
    <h2>内容发布</h2>
    <n-card size="small">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
        size="large"
      >
        <n-form-item label="标题" path="title">
          <n-input 
            v-model:value="formData.title" 
            placeholder="请输入笔记标题"
            clearable
          />
        </n-form-item>

        <n-form-item label="描述" path="description">
          <n-input 
            v-model:value="formData.description" 
            type="textarea" 
            placeholder="请输入笔记描述内容"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>

        <n-form-item label="话题标签" path="topics">
          <n-select
            v-model:value="selectedTopics"
            multiple
            filterable
            tag
            :options="topicOptions"
            placeholder="搜索或输入话题标签"
            :max-tag-count="5"
            @update:value="handleTopicsChange"
          />
          <template #feedback>
            最多可选择10个话题标签
          </template>
        </n-form-item>

        <n-form-item label="图片" path="images">
          <n-upload
            v-model:file-list="uploadFiles"
            :custom-request="customUpload"
            :max="9"
            accept="image/*"
            @change="handleUploadChange"
            @preview="handlePreview"
            list-type="image-card"
            multiple
            directory-dnd
          >
          </n-upload>
        </n-form-item>

        <n-form-item label="是否私密笔记">
          <n-space size="large">
            <n-switch 
              v-model:value="formData.is_private"
              size="medium"
              :round="false"
            >
              <template #checked>私密</template>
              <template #unchecked>公开</template>
            </n-switch>
          </n-space>
        </n-form-item>
      </n-form>
      <n-space justify="space-around" size="large">
        <n-button
          type="primary"
          size="medium"
          :loading="isPublishing"
          :disabled="isPublishing"
          @click="handlePublish"
          style="min-width: 120px;"
        >
          {{ isPublishing ? '发布中...' : '发布笔记' }}
        </n-button>
      </n-space>



    </n-card>

    <n-modal
      v-model:show="showPreview"
      preset="card"
      style="width: 800px"
      title="图片预览"
    >
      <img :src="previewImageUrl" style="width: 100%">
    </n-modal>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'
import { publishNote, uploadImage } from '../api/functions'
import type { PublishNoteParams } from '../api/config'
import emitter from '../utils/eventBus'
import type { UploadFileInfo } from 'naive-ui'
import { useMessage } from 'naive-ui'
import type { FormInst } from 'naive-ui'

// 热门话题示例数据
const HOT_TOPICS = [
  '头像分享', '可爱头像', '原创头像', '头像壁纸', '头像设计', '头像定制', '头像制作', '头像设计', '头像定制', '头像制作'
].map(topic => ({ label: `#${topic}`, value: topic }))

export default defineComponent({
  setup() {
    const formRef = ref<FormInst | null>(null)
    const uploadFiles = ref([])
    const isPublishing = ref(false)
    const selectedTopics = ref<string[]>([])
    const message = useMessage()

    const formData = ref({
      title: '',
      description: '',
      is_private: true,
      images: [] as string[],
      topics: [] as string[]
    } as PublishNoteParams)

    const rules = {
      title: {
        required: true,
        message: '请输入笔记标题',
        trigger: ['blur', 'input']
      },
      description: {
        required: true,
        message: '请输入笔记描述',
        trigger: ['blur', 'input']
      },
      images: {
        validator: (rule: any, value: string[]) => {
          return formData.value.images.length > 0
        },
        message: '请至少上传一张图片',
        trigger: ['change']
      }
    }

    const topicOptions = ref(HOT_TOPICS)

    const showPreview = ref(false)
    const previewImageUrl = ref('')

    onMounted(() => {
      // 检查是否有保存的标题
      const savedTitle = localStorage.getItem('xhs_Title')
      if (savedTitle) {
        formData.value.title = JSON.parse(savedTitle)
        localStorage.removeItem('xhs_Title')
      }

      // 检查是否有保存的文案
      const savedCaption = localStorage.getItem('xhs_Caption')
      if (savedCaption) {
        formData.value.description = JSON.parse(savedCaption)
        localStorage.removeItem('xhs_Caption')
      }

      // 检查是否有保存的话题
      const savedTopics = localStorage.getItem('xhs_Topics')
      if (savedTopics) {
        selectedTopics.value = JSON.parse(savedTopics)
        localStorage.removeItem('xhs_Topics')
      }

      // 检查是否有选中的图片
      const selectedImages = localStorage.getItem('selectedImages')
      if (selectedImages) {
        const imageUrls = JSON.parse(selectedImages)
        formData.value.images = imageUrls
        uploadFiles.value = imageUrls.map((url: string) => ({
          id: url,
          name: url.split('/').pop(),
          status: 'finished',
          url
        }))
        localStorage.removeItem('selectedImages')
      }
    })

    onUnmounted(() => {
      emitter.all.clear()
    })

    const handleTopicsChange = (values: string[]) => {
      if (values.length > 10) {
        selectedTopics.value = values.slice(0, 10)
        message.warning('最多只能选择10个话题')
        return
      }
      
      // 只更新话题，不改描述内容
      selectedTopics.value = values
    }

    const handlePreview = (file: UploadFileInfo) => {
      previewImageUrl.value = file.url || ''
      showPreview.value = true
    }

    const customUpload = async ({ file, onFinish, onError }: any) => {
      try {
        const uploadImageData = new FormData()
        uploadImageData.append('file', file.file)

        const response = await uploadImage(uploadImageData)
        
        if (response.success) {
          // 更新文件状态和URL
          file.status = 'finished'
          file.url = response.data.path
          
          // 更新表单数据中的图片路径
          const currentFiles = uploadFiles.value
            .filter((f: any) => f.status === 'finished' && f.url)
            .map((f: any) => f.url)
          formData.value.images = currentFiles

          onFinish()
        } else {
          throw new Error(response.message || '上传失败')
        }
      } catch (error: any) {
        file.status = 'error'
        onError()
        message.error(error.message || '上传失败')
      }
    }

    const handleUploadChange = ({ fileList }: any) => {
      uploadFiles.value = fileList
      // 更新表单数据中的图片路径，确保只包含已完成上传的图片
      const finishedFiles = fileList
        .filter((file: any) => file.status === 'finished' && file.url)
        .map((file: any) => file.url)
      formData.value.images = finishedFiles
    }

    const handlePublish = async () => {
      try {
        if (!formRef.value) return
        await formRef.value.validate()
        isPublishing.value = true

        // 修改发布数据的构造方式，直接传递话题数组
        const publishData = {
          ...formData.value,
          topics: selectedTopics.value // 直接传递话题数组
        }

        const response = await publishNote(publishData)
        if (response.success) {
          message.success('笔记发布成功！')
          // 重置表单
          formRef.value?.restoreValidation()
          formData.value = {
            title: '',
            description: '',
            is_private: true,
            images: [],
            topics: []
          }
          uploadFiles.value = []
          selectedTopics.value = []
        } else {
          throw new Error(response.message || '发布失败')
        }
      } catch (error: any) {
        console.error(error)
        message.error(error?.message || '发布失败')
      } finally {
        isPublishing.value = false
      }
    }

    return {
      formRef,
      formData,
      rules,
      uploadFiles,
      isPublishing,
      selectedTopics,
      topicOptions,
      handleTopicsChange,
      customUpload,
      handleUploadChange,
      handlePublish,
      showPreview,
      previewImageUrl,
      handlePreview
    }
  }
})
</script>

<style scoped>
.publish-page {
  min-height: calc(80vh - 64px);
  margin: 0px auto;
  padding: 0px;
}

/* :deep(.n-card) {
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
} */

:deep(.n-card-header) {
  text-align: center;
  font-size: 1.5em;
  font-weight: 600;
  padding: 24px 24px 0;
}

:deep(.n-form) {
  padding: 12px;
}

:deep(.n-form-item) {
  margin-bottom: 24px;
}

:deep(.n-form-item-label) {
  font-weight: 500;
  font-size: 0.95em;
  color: #333;
}

:deep(.n-input) {
  border-radius: 8px;
}

:deep(.n-input-wrapper) {
  transition: all 0.3s ease;
}

:deep(.n-input-wrapper:hover) {
  transform: translateY(-1px);
}

:deep(.n-upload) {
  margin-top: 8px;
}

:deep(.n-upload-trigger) {
  width: 112px;
  height: 112px;
  border-radius: 12px;
  border: 2px dashed #e5e5e5;
  transition: all 0.3s ease;
}

:deep(.n-upload-trigger:hover) {
  border-color: var(--n-primary-color);
  transform: translateY(-2px);
}

:deep(.n-upload-file-list) {
  display: grid;
  grid-template-columns: repeat(auto-fill, 112px);
  gap: 16px;
  margin-top: 16px;
}

:deep(.n-upload-file--image-card) {
  width: 112px;
  height: 112px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

:deep(.n-upload-file--image-card:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.n-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.n-button:not(.n-button--disabled):hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.n-switch) {
  transition: all 0.3s ease;
}

:deep(.n-switch:hover) {
  transform: translateY(-1px);
}

:deep(.n-modal-mask) {
  backdrop-filter: blur(8px);
}

:deep(.n-modal-wrapper .n-card) {
  border-radius: 16px;
  overflow: hidden;
}

/* 添加响应式布局 */
@media (max-width: 600px) {
  .publish-page {
    padding: 0 12px;
  }
  
  :deep(.n-form-item-label) {
    margin-bottom: 8px;
  }
  
  :deep(.n-upload-file-list) {
    gap: 12px;
  }
}
</style> 