<template>
  <div class="app">
    <n-dialog-provider>
    <n-message-provider>
      <n-config-provider>
        <header class="header">
          <h1>小红书自动生成</h1>
          <div class="service-status" :class="{ 'is-error': !serviceAvailable }">
            {{ serviceAvailable ? '服务正常' : '服务不可用' }}
          </div>
        </header>
        <div class="main-container">
          <NavMenu />
          <div class="content">
            <router-view></router-view>
          </div>
        </div>
      </n-config-provider>
    </n-message-provider>
  </n-dialog-provider>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import NavMenu from './components/NavMenu.vue'
import { checkHealth } from './api/functions'
import { useRoute } from 'vue-router'

export default defineComponent({
  components: {
    NavMenu
  },
  setup() {
    const route = useRoute()
    const serviceAvailable = ref(false)
    
    const updateTitle = (routeName: string) => {
      const baseTitle = '小红书自动生成'
      const pageTitles: Record<string, string> = {
        '/theme': '主题',
        '/generate': '生成',
        '/publish': '发布'
      }
      document.title = `${baseTitle} - ${pageTitles[routeName] || ''}`
    }

    const checkServiceHealth = async () => {
      try {
        const response = await checkHealth()
        serviceAvailable.value = response.success
        if (!response.success) {
          console.error('服务异常:', response.message)
        }
      } catch (error) {
        serviceAvailable.value = false
        console.error('服务健康检查失败:', error)
      }
    }

    // 定期检查服务健康状态
    const startHealthCheck = () => {
      // 立即检查一次
      checkServiceHealth()
      
      // 每30秒检查一次
      const intervalId = setInterval(checkServiceHealth, 30000)

      // 组件卸载时清除定时器
      return () => clearInterval(intervalId)
    }

    onMounted(() => {
      updateTitle(route.path)
      startHealthCheck()
    })

    return {
      serviceAvailable
    }
  }
})
</script>

<style>
.app {
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.header {
  background: linear-gradient(135deg, #27ff00 0%, #0077ff 100%);
  padding: 1.2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

.service-status {
  position: absolute;
  top: 50%;
  right: 1.5rem;
  transform: translateY(-50%);
  padding: 0.4rem 0.8rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  background-color: #4caf50;
  color: white;
  transition: all 0.3s ease;
}

.service-status.is-error {
  background-color: #f44336;
}

h1 {
  margin: 0;
  color: white;
  text-align: center;
  font-size: 1.8rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.main-container {
  flex: 1;
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.content {
  flex: 1;
  border-radius: 12px;
  padding: 1.5rem;
  background-color: white;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
  /* max-width: 70rem; */
}

@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
    padding: 1rem;
  }
  
  .content {
    padding: 1rem;
  }

  .service-status {
    position: static;
    transform: none;
    display: inline-block;
    margin-top: 0.5rem;
    font-size: 0.75rem;
    padding: 0.3rem 0.6rem;
  }

  .header {
    text-align: center;
    padding: 1rem;
  }
}
</style>