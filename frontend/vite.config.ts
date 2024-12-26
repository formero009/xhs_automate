import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

import AutoImport from 'unplugin-auto-import/vite'
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'
import Components from 'unplugin-vue-components/vite'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
     imports: [
        {
          'naive-ui': ['useDialog', 'useMessage', 'useNotification', 'useLoadingBar', 'createDiscreteApi']
        }
      ],
      // vue3 组件 js 语句中自动引入组件
      resolvers: [NaiveUiResolver()]
    }),
    // vue3 组件中自动引入组件
    Components({
      resolvers: [NaiveUiResolver()]
    })
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/images': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      }
    }
  }
})
