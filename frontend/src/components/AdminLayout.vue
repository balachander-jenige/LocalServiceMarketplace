<template>
  <div class="admin-layout">
    <div class="admin-container">
      <!-- Sidebar -->
      <div class="admin-sidebar">
        <div class="sidebar-header">
          <div class="logo">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2ZM12 18C14.21 18 16 16.21 16 14C16 11.79 14.21 10 12 10C9.79 10 8 11.79 8 14C8 16.21 9.79 18 12 18ZM12 20C8.69 20 6 17.31 6 14C6 10.69 8.69 8 12 8C15.31 8 18 10.69 18 14C18 17.31 15.31 20 12 20Z" fill="currentColor"/>
            </svg>
            <h2>Freelancer Admin</h2>
          </div>
        </div>
        <nav class="sidebar-nav">
          <ul class="nav-list">
            <li class="nav-item">
              <router-link to="/admin" class="nav-link" :class="{ active: $route.path === '/admin' }">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 13H11V3H3V13ZM3 21H11V15H3V21ZM13 21H21V11H13V21ZM13 3V9H21V3H13Z" fill="currentColor"/>
                </svg>
                <span>Dashboard</span>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/users" class="nav-link" :class="{ active: $route.path === '/admin/users' }">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
                </svg>
                <span>User Management</span>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/orders" class="nav-link" :class="{ active: $route.path === '/admin/orders' }">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V5H19V19ZM17 12H7V10H17V12ZM15 16H7V14H15V16ZM17 8H7V6H17V8Z" fill="currentColor"/>
                </svg>
                <span>Order Management</span>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/tasks" class="nav-link" :class="{ active: $route.path === '/admin/tasks' }">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 11H15M9 15H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H17C18.1046 3 19 3.89543 19 5V19C19 20.1046 18.1046 21 17 21Z" fill="currentColor"/>
                </svg>
                <span>Task Management</span>
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/notifications" class="nav-link" :class="{ active: $route.path === '/admin/notifications' }">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.36 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5S10.5 3.17 10.5 4V4.68C7.63 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="currentColor"/>
                </svg>
                <span>Notification Management</span>
              </router-link>
            </li>
          </ul>
        </nav>
      </div>
      
      <!-- Main Content -->
      <div class="admin-main">
        <!-- Header -->
        <div class="admin-header">
          <div class="header-left">
            <h1>{{ pageTitle }}</h1>
            <div class="breadcrumb" v-if="breadcrumb">
              <span v-for="(item, index) in breadcrumb" :key="index">
                <router-link v-if="item.path" :to="item.path" class="breadcrumb-link">{{ item.name }}</router-link>
                <span v-else class="breadcrumb-current">{{ item.name }}</span>
                <span v-if="index < breadcrumb.length - 1" class="breadcrumb-separator">/</span>
              </span>
            </div>
          </div>
          <div class="admin-info">
            <span class="welcome-text">Welcome back, {{ currentUser?.username || 'Admin' }}</span>
            <div class="admin-avatar">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
              </svg>
            </div>
            <button class="logout-btn" @click="handleLogout">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M17 7L15.59 8.41L18.17 11H8V13H18.17L15.59 15.59L17 17L22 12L17 7ZM4 5H12V3H4C2.9 3 2 3.9 2 5V19C2 20.1 2.9 21 4 21H12V19H4V5Z" fill="currentColor"/>
              </svg>
              <span>Logout</span>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="admin-content">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout',
  props: {
    pageTitle: {
      type: String,
      required: true
    },
    breadcrumb: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      currentUser: null
    }
  },
  created() {
    this.checkLoginStatus()
  },
  methods: {
    checkLoginStatus() {
      const user = sessionStorage.getItem('currentUser')
      if (user) {
        this.currentUser = JSON.parse(user)
      }
    },
    handleLogout() {
      if (confirm('Are you sure you want to logout?')) {
        // Clear user info
        sessionStorage.removeItem('currentUser')
        // Clear token
        localStorage.removeItem('access_token')
        // Jump to login page
        this.$router.push('/login')
        alert('Logged out successfully')
      }
    }
  }
}
</script>

<style scoped>
/* Admin Layout Styles */
.admin-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.admin-layout::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.admin-container {
  display: flex;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* Sidebar Styles */
.admin-sidebar {
  width: 280px;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: white;
  padding: 0;
  box-shadow: 4px 0 20px rgba(0,0,0,0.1);
  position: relative;
  backdrop-filter: blur(10px);
}

.admin-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255,255,255,0.05) 0%, transparent 50%);
  pointer-events: none;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo svg {
  color: #4f46e5;
  filter: drop-shadow(0 0 8px rgba(79, 70, 229, 0.3));
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-nav {
  padding: 20px 0;
  position: relative;
  z-index: 1;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  font-weight: 500;
}

.nav-link:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.nav-link.active {
  color: white;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.2), rgba(124, 58, 237, 0.2));
  border-right: 3px solid #4f46e5;
}

.nav-link.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #4f46e5, #7c3aed);
  border-radius: 0 2px 2px 0;
}

.nav-link svg {
  flex-shrink: 0;
}

.nav-link span {
  font-size: 14px;
}

/* Main Content Styles */
.admin-main {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px 0 0 20px;
  margin: 20px 20px 20px 0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.admin-header {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  padding: 24px 32px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  background: linear-gradient(135deg, #1e293b, #475569);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #64748b;
}

.breadcrumb-link {
  color: #4f46e5;
  text-decoration: none;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: #7c3aed;
}

.breadcrumb-current {
  color: #64748b;
  font-weight: 500;
}

.breadcrumb-separator {
  color: #cbd5e1;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.welcome-text {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

.admin-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.logout-btn:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.admin-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .admin-sidebar {
    width: 240px;
  }
  
  .admin-main {
    margin: 16px 16px 16px 0;
    border-radius: 16px 0 0 16px;
  }
  
  .admin-header {
    padding: 20px 24px;
  }
  
  .admin-content {
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .admin-container {
    flex-direction: column;
  }
  
  .admin-sidebar {
    width: 100%;
    height: auto;
    border-radius: 0 0 20px 20px;
    margin-bottom: 16px;
  }
  
  .admin-main {
    margin: 0 16px 16px 16px;
    border-radius: 20px;
  }
  
  .admin-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .admin-info {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .admin-main {
    margin: 0 8px 8px 8px;
    border-radius: 16px;
  }
  
  .admin-header {
    padding: 16px 20px;
  }
  
  .admin-content {
    padding: 20px;
  }
  
  .header-left h1 {
    font-size: 24px;
  }
}
</style>

