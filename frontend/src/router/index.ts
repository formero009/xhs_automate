import { createRouter, createWebHistory } from 'vue-router'
import GeneratePage from '@/views/GeneratePage.vue'
import ThemePage from '@/views/ThemePage.vue'
import UserPage from '@/views/UserPage.vue'
import PublishPage from '@/views/PublishPage.vue'
import WorkflowPage from '@/views/WorkflowPage.vue'
import AgentPage from '@/views/AgentPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/generate'
    },
    {
      path: '/generate',
      name: 'generate',
      component: GeneratePage
    },
    {
      path: '/theme',
      name: 'theme',
      component: ThemePage
    },
    {
      path: '/publish',
      name: 'publish',
      component: PublishPage
    },
    {
      path: '/workflow',
      name: 'workflow',
      component: WorkflowPage
    },
    {
      path: '/users',
      name: 'users',
      component: UserPage
    },
    {
      path: '/agent',
      name: 'agent',
      component: AgentPage
    }
  ]
})

export default router 