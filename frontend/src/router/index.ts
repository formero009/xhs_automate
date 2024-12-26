import { createRouter, createWebHistory } from 'vue-router'
import ThemePage from '../views/ThemePage.vue'
import GeneratePage from '../views/GeneratePage.vue'
import PublishPage from '../views/PublishPage.vue'
import WorkflowPage from '../views/WorkflowPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/theme'
    },
    {
      path: '/theme',
      component: ThemePage
    },
    {
      path: '/workflow',
      name: 'workflow',
      component: WorkflowPage
    },
    {
      path: '/generate',
      component: GeneratePage
    },
    {
      path: '/publish',
      component: PublishPage
    }
  ]
})

export default router 