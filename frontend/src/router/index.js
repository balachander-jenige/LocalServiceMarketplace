import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import WelcomePage from '@/views/WelcomePage.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import TestAPI from '@/views/TestAPI.vue'
import ProviderTaskDetail from '@/views/ProviderTaskDetail.vue'
import CustomerTaskDetail from '@/views/CustomerTaskDetail.vue'
import OrderDetail from '@/views/OrderDetail.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import UserManagement from '@/views/UserManagement.vue'
import UserDetail from '@/views/UserDetail.vue'
import OrderManagement from '@/views/OrderManagement.vue'
import TaskManagement from '@/views/TaskManagement.vue'
import NotificationManagement from '@/views/NotificationManagement.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: WelcomePage
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/test-api',
    name: 'TestAPI',
    component: TestAPI
  },
  {
    path: '/task/:id',
    name: 'TaskDetail',
    component: (route) => {
      // Determine which component to use based on role parameter
      const role = route?.query?.role
      if (role === 'customer') {
        return CustomerTaskDetail
      } else {
        return ProviderTaskDetail
      }
    },
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/order/:id',
    name: 'OrderDetail',
    component: OrderDetail,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/publish-task',
    name: 'PublishTask',
    component: () => import('@/views/PublishTask.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/my-tasks',
    name: 'MyTasks',
    component: () => import('@/views/MyTasks.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('@/views/Messages.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: UserManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/users/:id',
    name: 'UserDetail',
    component: UserDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/orders',
    name: 'OrderManagement',
    component: OrderManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/orders/:id',
    name: 'OrderDetail',
    component: OrderDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/tasks',
    name: 'TaskManagement',
    component: TaskManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/notifications',
    name: 'NotificationManagement',
    component: NotificationManagement,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    // 检查用户是否已登录
    const currentUser = sessionStorage.getItem('currentUser')
    if (currentUser) {
      // 用户已登录，允许访问
      next()
    } else {
      // 用户未登录，重定向到欢迎页面
      next('/welcome')
    }
  } else {
    // 不需要认证的页面，直接访问
    next()
  }
})

export default router

