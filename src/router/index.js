import { createRouter, createWebHistory } from 'vue-router'

import { loadSession } from '@/services/session'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      meta: { requiresAuth: true },
      component: () => import('../views/DashboardView.vue')
    },
    {
      path: '/matches',
      name: 'matches',
      meta: { requiresAuth: true },
      component: () => import('../views/MatchesView.vue')
    },
    {
      path: '/messages',
      name: 'messages',
      meta: { requiresAuth: true },
      component: () => import('../views/MessagesView.vue')
    },
    {
      path: '/notifications',
      name: 'notifications',
      meta: { requiresAuth: true },
      component: () => import('../views/NotificationsView.vue')
    },
    {
      path: '/login',
      name: 'login',
      meta: { guestOnly: true },
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/signup',
      name: 'signup',
      meta: { guestOnly: true },
      component: () => import('../views/SignupView.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      meta: { requiresAuth: true },
      component: () => import('../views/ProfileView.vue')
    },
    {
      path: '/edit-profile',
      name: 'edit-profile',
      meta: { requiresAuth: true },
      component: () => import('../views/EditProfileView.vue')
    }
  ]
})

router.beforeEach(async (to) => {
  const account = await loadSession()

  if (to.meta.guestOnly && account) {
    return { name: 'dashboard' }
  }

  if (to.meta.requiresAuth && !account) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  return true
})

export default router
