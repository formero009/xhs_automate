<template>
  <div class="theme-page">
    <div class="page-header">
      <div class="header-left">
        <h2>提示词生成</h2>
      </div>
      <n-button 
        @click="clearCache" 
        type="error" 
        secondary 
        size="small"
      >
        <template #icon>
          <n-icon><TrashOutline /></n-icon>
        </template>
        清除缓存
      </n-button>
    </div>
    <div class="content-wrapper">
      <n-card class="input-card" title="输入提示词">
        <n-input
          v-model:value="promptText"
          type="textarea"
          placeholder="从一个简单的想法开始,比如'一只狗'或'一棵树'"
          :autosize="{ minRows: 20, maxRows: 20 }"
        />
        <template #footer>
          <div class="button-group">
            <n-button
              type="primary"
              @click="enhancePromptHandler"
              :loading="isLoading"
              :disabled="isLoading"
              block
            >
              <template #icon>
                <n-icon><ColorWandOutline /></n-icon>
              </template>
              {{ isLoading ? '生成中...' : '魔法增强' }}
            </n-button>
            
            <n-button
              @click="useDirectlyHandler"
              :disabled="isLoading"
              block
            >
              <template #icon>
                <n-icon><CheckmarkCircleOutline /></n-icon>
              </template>
              直接使用
            </n-button>
          </div>
        </template>
      </n-card>

      <n-card class="result-card">
        <template #header>
          <div class="result-header">
            <span>生成结果</span>
            <n-button
              @click="translateResultHandler"
              :disabled="isLoading || !resultText || resultText === '您的生成结果将显示在这里'"
              :loading="isLoading"
              secondary
              size="small"
            >
              <template #icon>
                <n-icon><TranslateOutlined /></n-icon>
              </template>
              {{ isLoading ? '翻译中...' : '翻译' }}
            </n-button>
          </div>
        </template>

        <n-scrollbar style="max-height: 35rem; border-radius: 10px; border: 1px solid #e0e0e0; padding: 10px;" trigger="hover">
          <div class="result-text" :class="{ placeholder: !resultText || resultText === '您的生成结果将显示在这里' }">
            {{ resultText }}
          </div>
          <n-divider v-if="translatedText" />
          <div v-if="translatedText" class="translated-text">{{ translatedText }}</div>
        </n-scrollbar>

        <template #footer>
          <n-button
            type="success"
            @click="sendToGenerate"
            :disabled="!resultText || resultText === '您的生成结果将显示在这里'"
            block
          >
            <template #icon>
              <n-icon><SendOutline /></n-icon>
            </template>
            发送到正向提示词
          </n-button>
        </template>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { translateText, enhancePrompt } from '../api/functions'
import {
  TrashOutline,
  ColorWandOutline,
  CheckmarkCircleOutline,
  SendOutline
} from '@vicons/ionicons5'
import { TranslateOutlined } from '@vicons/material'
import {
  NButton,
  NCard,
  NInput,
  NIcon,
  NDivider,
  NScrollbar
} from 'naive-ui'

const STORAGE_KEY = 'theme_page_cache'

const router = useRouter()
const promptText = ref('')
const resultText = ref('您的生成结果将显示在这里')
const translatedText = ref('')
const isLoading = ref(false)

// 从缓存加载数据
onMounted(() => {
  const cached = localStorage.getItem(STORAGE_KEY)
  if (cached) {
    const data = JSON.parse(cached)
    promptText.value = data.promptText || ''
    resultText.value = data.resultText || '您的生成结果将显示在这里'
    translatedText.value = data.translatedText || ''
  }
})

// 监听数据变化，自动保存到缓存
watch(
  [promptText, resultText, translatedText],
  ([newPrompt, newResult, newTranslated]) => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        promptText: newPrompt,
        resultText: newResult === '您的生成结果将显示在这里' ? '' : newResult,
        translatedText: newTranslated
      })
    )
  },
  { deep: true }
)

const enhancePromptHandler = async () => {
  if (!promptText.value.trim()) {
    alert('请输入提示词')
    return
  }
  
  try {
    isLoading.value = true
    translatedText.value = '' // 清空之前的翻译
    const response = await enhancePrompt(promptText.value)
    if (response.success && response.data) {
      resultText.value = response.data.prompt
    } else {
      throw new Error(response.message || '增强失败')
    }
  } catch (error) {
    console.error('增强提示词失败:', error)
    alert('增强提示词失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const translateResultHandler = async () => {
  if (!resultText.value || resultText.value === '您的生成结果将显示在这里') {
    alert('请先生成内容')
    return
  }

  try {
    isLoading.value = true
    const response = await translateText(resultText.value)
    if (response.success && response.data?.translated_text) {
      translatedText.value = response.data.translated_text
      
      // 可选：验证翻译结果是否与原文相符
      if (response.data.original_text !== resultText.value) {
        console.warn('翻译的原文与当前文本不匹配')
      }
    } else {
      throw new Error(response.message || '翻译失败')
    }
  } catch (error) {
    console.error('翻译失败:', error)
    alert('翻译失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const useDirectlyHandler = () => {
  if (!promptText.value.trim()) {
    alert('请输入提示词')
    return
  }
  
  resultText.value = promptText.value.trim()
  translatedText.value = '' // 清空之前的翻译
}

const sendToGenerate = () => {
  // 保存提示词到本地存储
  localStorage.setItem('theme_prompt', resultText.value)
  router.push('/generate')
}

// 添加清除缓存的方法（可选）
const clearCache = () => {
  localStorage.removeItem(STORAGE_KEY)
  promptText.value = ''
  resultText.value = '您的生成结果将显示在这里'
  translatedText.value = ''
}
</script>

<style scoped>
.theme-page {
  min-height: calc(80vh - 64px);
  max-height: 800px;
  padding: 32px;
  overflow: hidden;
}

.page-header {
  margin-bottom: 32px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  flex: 1;
}

h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--n-text-color);
}

.subtitle {
  margin: 8px 0 0;
  color: var(--n-text-color-3);
  font-size: 14px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.input-card, .result-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.button-group {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 12px;
  margin-top: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-content {
  max-height:20rem;
  flex: 1;
  margin: -12px;
  padding: 12px;
  border-radius: 6px;
  background-color: var(--n-card-color);
}

.result-text {
  font-size: 15px;
  line-height: 1.8;
  white-space: pre-wrap;
  margin-bottom: 12px;
  word-break: break-all;
}

.result-text.placeholder {
  color: #999;
}

.translated-text {
  color: var(--n-primary-color);
  font-size: 15px;
  line-height: 1.8;
  padding-top: 12px;
}

@media (max-width: 768px) {
  .theme-page {
    height: auto;
    overflow: visible;
  }
  
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .input-card, .result-card {
    height: 400px;
  }
}
</style> 