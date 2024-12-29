<template>
  <div class="app">
    <n-message-provider>
      <n-dialog-provider>
        <n-config-provider>
          <AppContent />
        </n-config-provider>
      </n-dialog-provider>
    </n-message-provider>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import AppContent from './components/AppContent.vue'

export default defineComponent({
  components: {
    AppContent
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
</style>