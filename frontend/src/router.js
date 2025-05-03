import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'
import { userResource } from '@/data/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    meta: { public: true },
  },
  {
    name: 'Login',
    path: '/account/login',
    component: () => import('@/pages/Login.vue'),
  },
  // Client routes
  {
    path: '/client/dashboard',
    name: 'ClientDashboard',
    component: () => import('@/pages/client/ClientDashboard.vue'),
    // meta: { requiresAuth: true, requiredRole: 'Client' }
  },
  {
    path: '/client/projects',
    name: 'ClientProjects',
    component: () => import('@/pages/client/Project.vue'),
    // meta: { requiresAuth: true, requiredRole: 'Client' }
  },
  {
    path: '/client/deliverables',
    name: 'ClientDeliverables',
    component: () => import('@/pages/client/Deliverable.vue'),
    // meta: { requiresAuth: true, requiredRole: 'Client' }
  },
  {
    path: '/client/team',
    name: 'ClientTeam',
    component: () => import('@/pages/client/TeamMember.vue'),
    // meta: { requiresAuth: true, requiredRole: 'Client' }
  },
  {
    path: '/client/Projects/:id',
    name: 'ClientProjectDetails',
    component: () => import('@/pages/client/ProjectDetails.vue'),
    // meta: { requiresAuth: true, requiredRole: 'Client' }
  },
  {
    path: '/vendor/dashboard',
    name: 'VendorDashboard',
    component: () => import('@/pages/vendor/VendorDashboard.vue'),
    // meta: { requiresAuth: true, requiredRole: 'Client' }
  },
  {
    path: '/submit-deliverable',
    name: 'SubmitDeliverable',
    component: () => import('@/pages/vendor/SubmitDeliverable.vue')
  },
  {
    path: '/thank-you',
    name: 'ThankYou',
    component: () => import('@/pages/vendor/ThankYou.vue')
  },
  {
    path: '/vendor/tasks',
    name: 'Tasks',
    component: () => import('@/components/TaskTable.vue'),
  },
  {
    path: '/vendor/deliverables',
    name: 'Deliverables',
    component: () => import('@/pages/vendor/DeliverableTable.vue'), 
  },
  {
    path: '/vendor/task-detail/:name',
    name: 'TaskDetails',
    component: () => import('@/components/TaskDetails.vue')
  }

]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  if (to.meta.public) {
    return next();
  }
  
  let isLoggedIn = session.isLoggedIn
  try {
    await userResource.promise
  } catch (error) {
    isLoggedIn = false
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Home' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
