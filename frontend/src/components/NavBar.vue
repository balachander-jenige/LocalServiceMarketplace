<template>
  <nav class="navbar" :class="{ 'customer-theme': currentRole === 'customer' }">
    <div class="navbar-container">
      <div class="navbar-brand">
        <h2>freelancer</h2>
      </div>
      
      <!-- Logged-in user menu -->
      <ul v-if="isLoggedIn" class="navbar-menu">
        <li class="navbar-item" v-for="item in menuItems" :key="item.path">
          <router-link :to="item.path" class="navbar-link" :class="{ active: $route.path === item.path }">
            {{ item.label }}
          </router-link>
        </li>
      </ul>
      
      <!-- User status area -->
      <div class="navbar-user">
        <div v-if="isLoggedIn" class="user-info">
          <span class="user-name">{{ currentUser.username }}</span>
          <span class="user-role">{{ currentUser.role === 'customer' ? 'Customer' : 'Service Provider' }}</span>
          <button @click="handleLogout" class="logout-btn">Logout</button>
        </div>
        <div v-else class="auth-buttons">
          <router-link to="/login" class="auth-btn login-btn">Login</router-link>
          <router-link to="/register" class="auth-btn register-btn">Register</router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar',
  data() {
    return {
      currentUser: null
    }
  },
  computed: {
    isLoggedIn() {
      return !!this.currentUser
    },
    currentRole() {
      if (this.currentUser) {
        return this.currentUser.role
      }
      // If no logged-in user info, use route parameter, default to customer
      return this.$route.query.role || 'customer'
    },
    menuItems() {
      if (this.currentRole === 'admin') {
        return [
          { path: '/admin', label: 'Admin Dashboard' },
          { path: '/admin/users', label: 'User Management' },
          { path: '/admin/tasks', label: 'Task Management' },
          { path: '/admin/settings', label: 'System Settings' }
        ]
      } else if (this.currentRole === 'provider') {
        return [
          { path: '/?role=provider', label: 'Find Tasks' },
          { path: '/my-tasks?role=provider', label: 'My Tasks' },
          { path: '/messages?role=provider', label: 'My Messages' },
          { path: '/profile?role=provider', label: 'Profile' }
        ]
      } else {
        return [
          { path: '/?role=customer', label: 'Unassigned Tasks' },
          { path: '/my-tasks?role=customer', label: 'My Tasks' },
          { path: '/messages?role=customer', label: 'My Messages' },
          { path: '/profile?role=customer', label: 'Profile' }
        ]
      }
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
      sessionStorage.removeItem('currentUser')
      this.currentUser = null
      alert('Logged out successfully')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar.customer-theme {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
}

.user-role {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.auth-btn {
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-btn {
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.register-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.register-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.navbar-brand h2 {
  color: white;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.navbar-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 30px;
}

.navbar-item {
  margin: 0;
}

.navbar-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-weight: 500;
  position: relative;
}

.navbar-link:hover {
  background-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.navbar-link.active {
  background-color: rgba(255, 255, 255, 0.25);
  font-weight: 600;
}

.navbar-link.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background-color: white;
  border-radius: 1px;
}

@media (max-width: 768px) {
  .navbar-container {
    flex-direction: column;
    height: auto;
    padding: 15px 20px;
  }
  
  .navbar-menu {
    margin-top: 15px;
    gap: 15px;
  }
  
  .navbar-brand h2 {
    font-size: 20px;
  }
}
</style>
