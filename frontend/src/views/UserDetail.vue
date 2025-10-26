<template>
  <div class="user-detail">
    <div class="admin-container">
      <div class="admin-sidebar">
        <div class="sidebar-header">
          <h2>Admin Dashboard</h2>
        </div>
        <nav class="sidebar-nav">
          <ul class="nav-list">
            <li class="nav-item">
              <router-link to="/admin" class="nav-link">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 13H11V3H3V13ZM3 21H11V15H3V21ZM13 21H21V11H13V21ZM13 3V9H21V3H13Z" fill="currentColor"/>
                </svg>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/users" class="nav-link active">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
                </svg>
                User Management
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/orders" class="nav-link">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V5H19V19ZM17 12H7V10H17V12ZM15 16H7V14H15V16ZM17 8H7V6H17V8Z" fill="currentColor"/>
                </svg>
                Order Management
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/tasks" class="nav-link">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 11H15M9 15H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H17C18.1046 3 19 3.89543 19 5V19C19 20.1046 18.1046 21 17 21Z" fill="currentColor"/>
                </svg>
                Task Management
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/notifications" class="nav-link">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.36 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5S10.5 3.17 10.5 4V4.68C7.63 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="currentColor"/>
                </svg>
                Notification Management
              </router-link>
            </li>
          </ul>
        </nav>
      </div>
      
      <div class="admin-main">
        <div class="admin-header">
          <div class="header-left">
            <button @click="goBack" class="back-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Back
            </button>
            <h1>User Details</h1>
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
              Logout
            </button>
          </div>
        </div>
        
        <div class="admin-content">
          <div v-if="loading" class="loading">
            <div class="loading-spinner"></div>
            <p>Loading...</p>
          </div>
          
          <div v-else-if="error" class="error">
            <p>{{ error }}</p>
            <button @click="loadUserDetail" class="retry-btn">Retry</button>
          </div>
          
          <div v-else-if="user" class="user-detail-content">
            <div class="user-header">
              <div class="user-avatar-large">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
                </svg>
              </div>
              <div class="user-info">
                <h2>{{ user.username }}</h2>
                <span class="user-type" :class="getUserTypeClass(user.role_id)">
                  {{ getUserTypeName(user.role_id) }}
                </span>
              </div>
              <div class="user-actions">
                <button @click="deleteUser" class="delete-user-btn">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 6H5H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Delete User
                </button>
              </div>
            </div>
            
            <div class="user-details-grid">
              <!-- Basic Information Card -->
              <div class="detail-card">
                <div class="card-header">
                  <h3>Basic Information</h3>
                </div>
                <div class="card-content">
                  <div class="detail-item">
                    <label>User ID</label>
                    <span>{{ user.user_id }}</span>
                  </div>
                  <div class="detail-item">
                    <label>Username</label>
                    <span>{{ user.username }}</span>
                  </div>
                  <div class="detail-item">
                    <label>Email</label>
                    <span>{{ user.email }}</span>
                  </div>
                  <div class="detail-item">
                    <label>User Type</label>
                    <span class="user-type" :class="getUserTypeClass(user.role_id)">
                      {{ getUserTypeName(user.role_id) }}
                    </span>
                  </div>
                  <div class="detail-item">
                    <label>Registration Date</label>
                    <span>{{ formatDate(user.created_at) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- Customer Specific Information -->
              <div v-if="user.role_id === 1" class="detail-card">
                <div class="card-header">
                  <h3>Customer Information</h3>
                </div>
                <div class="card-content">
                  <div class="detail-item">
                    <label>Location</label>
                    <span>{{ user.profile?.location || 'Not Set' }}</span>
                  </div>
                  <div class="detail-item">
                    <label>Address</label>
                    <span>{{ user.profile?.address || 'Not Set' }}</span>
                  </div>
                  <div class="detail-item">
                    <label>Budget Preference</label>
                    <span>{{ user.profile?.budget_preference ? 'S$' + user.profile.budget_preference : 'Not Set' }}</span>
                  </div>
                </div>
              </div>
              
              <!-- Provider Specific Information -->
              <div v-if="user.role_id === 2" class="detail-card">
                <div class="card-header">
                  <h3>Provider Information</h3>
                </div>
                <div class="card-content">
                  <div class="detail-item">
                    <label>Skills</label>
                    <div class="skills-container">
                      <template v-if="user.profile?.skills && user.profile.skills.length > 0">
                        <span class="skill-tag" v-for="skill in user.profile.skills" :key="skill">
                          {{ skill }}
                        </span>
                      </template>
                      <span v-else class="no-data">Not Set</span>
                    </div>
                  </div>
                  <div class="detail-item">
                    <label>Experience</label>
                    <span>{{ user.profile?.experience_years || 0 }} years</span>
                  </div>
                  <div class="detail-item">
                    <label>Hourly Rate</label>
                    <span>{{ user.profile?.hourly_rate ? 'S$' + user.profile.hourly_rate : 'Not Set' }}</span>
                  </div>
                  <div class="detail-item">
                    <label>Availability</label>
                    <span>{{ user.profile?.availability || 'Not Set' }}</span>
                  </div>
                  <div class="detail-item">
                    <label>Rating</label>
                    <span class="rating">
                      <span class="rating-value">{{ user.profile?.rating || 5.0 }}</span>
                      <span class="rating-count">({{ user.profile?.total_reviews || 0 }} reviews)</span>
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- Account Status Card -->
              <div class="detail-card">
                <div class="card-header">
                  <h3>Account Status</h3>
                </div>
                <div class="card-content">
                  <div class="detail-item">
                    <label>Account Status</label>
                    <span class="status-active">Active</span>
                  </div>
                  <div class="detail-item">
                    <label>Last Login</label>
                    <span>{{ formatDate(user.last_login_at || user.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminAPI } from '@/api/auth'

export default {
  name: 'UserDetail',
  data() {
    return {
      user: null,
      loading: false,
      error: null,
      currentUser: null
    }
  },
  created() {
    this.checkLoginStatus()
    this.loadUserDetail()
  },
  methods: {
    checkLoginStatus() {
      const user = sessionStorage.getItem('currentUser')
      if (user) {
        this.currentUser = JSON.parse(user)
      }
    },
    async loadUserDetail() {
      this.loading = true
      this.error = null
      try {
        const userId = this.$route.params.id
        
        // Check if token exists
        const token = localStorage.getItem('access_token')
        if (!token) {
          this.error = 'Not logged in or login expired, please login again'
          return
        }

        // Call real API to get user details
        const response = await adminAPI.getUserDetail(userId)
        
        if (response.success) {
          this.user = response.data
        } else {
          this.error = response.message || 'Failed to get user details'
        }
      } catch (error) {
        // Check if token expired
        if (error.message.includes('expired') || error.status === 401) {
          this.error = 'Login expired, please login again'
          localStorage.removeItem('access_token')
          sessionStorage.removeItem('currentUser')
          setTimeout(() => {
            this.$router.push('/login')
          }, 2000)
        } else {
          this.error = 'Failed to load user details: ' + error.message
        }
        console.error('Failed to load user details:', error)
      } finally {
        this.loading = false
      }
    },
    getUserTypeName(roleId) {
      const roleMap = {
        1: 'Customer',
        2: 'Service Provider',
        3: 'Admin'
      }
      return roleMap[roleId] || 'Unknown'
    },
    getUserTypeClass(roleId) {
      const classMap = {
        1: 'customer',
        2: 'provider',
        3: 'admin'
      }
      return classMap[roleId] || 'unknown'
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    async deleteUser() {
      if (confirm(`Are you sure you want to delete user "${this.user.username}"? This action cannot be undone.`)) {
        try {
          // Call real API to delete user
          const response = await adminAPI.deleteUser(this.user.user_id)
          
          if (response.success) {
            alert('User deleted successfully')
            this.$router.push('/admin/users')
          } else {
            alert('Failed to delete user: ' + (response.message || 'Unknown error'))
          }
        } catch (error) {
          // Check if token expired
          if (error.message.includes('expired') || error.status === 401) {
            alert('Login expired, please login again')
            localStorage.removeItem('access_token')
            sessionStorage.removeItem('currentUser')
            this.$router.push('/login')
          } else {
            alert('Failed to delete user: ' + error.message)
          }
          console.error('Failed to delete user:', error)
        }
      }
    },
    goBack() {
      this.$router.push('/admin/users')
    },
    handleLogout() {
      if (confirm('Are you sure you want to logout?')) {
        sessionStorage.removeItem('currentUser')
        localStorage.removeItem('access_token')
        this.$router.push('/login')
        alert('Logged out successfully')
      }
    }
  }
}
</script>

<style scoped>
.user-detail {
  min-height: 100vh;
  background: #f8f9fa;
}

.admin-container {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: 250px;
  background: #2c3e50;
  color: white;
  padding: 0;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #34495e;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.sidebar-nav {
  padding: 20px 0;
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
  color: #bdc3c7;
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-link:hover {
  background: #34495e;
  color: white;
}

.nav-link.active {
  background: #34495e;
  color: white;
  border-left-color: #3498db;
}

.nav-link svg {
  flex-shrink: 0;
}

.admin-main {
  flex: 1;
  padding: 0;
}

.admin-header {
  background: white;
  padding: 20px 30px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f8f9fa;
  color: #666;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #e9ecef;
  border-color: #3498db;
  color: #3498db;
}

.admin-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.welcome-text {
  color: #666;
  font-size: 14px;
}

.admin-avatar {
  width: 40px;
  height: 40px;
  background: #3498db;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: #c0392b;
  transform: translateY(-1px);
}

.admin-content {
  padding: 30px;
}

.loading, .error {
  padding: 40px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #e74c3c;
}

.retry-btn {
  margin-top: 15px;
  padding: 8px 16px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.user-detail-content {
  max-width: 1000px;
}

.user-header {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar-large {
  width: 80px;
  height: 80px;
  background: #3498db;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-info {
  flex: 1;
}

.user-info h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.user-type {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
}

.user-type.customer {
  background: #e3f2fd;
  color: #1976d2;
}

.user-type.provider {
  background: #f3e5f5;
  color: #7b1fa2;
}

.user-type.admin {
  background: #fff3e0;
  color: #f57c00;
}

.user-actions {
  display: flex;
  gap: 10px;
}

.delete-user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #ffebee;
  color: #d32f2f;
  border: 1px solid #ffcdd2;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-user-btn:hover {
  background: #ffcdd2;
  border-color: #ef9a9a;
}

.user-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.detail-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.card-header {
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.card-content {
  padding: 20px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f8f9fa;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item label {
  font-weight: 500;
  color: #666;
  font-size: 14px;
}

.detail-item span {
  color: #2c3e50;
  font-size: 14px;
}

.status-active {
  color: #27ae60 !important;
  font-weight: 500;
}

/* 技能标签样式 */
.skills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.skill-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.no-data {
  color: #999;
  font-style: italic;
}

/* 评分样式 */
.rating {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rating-value {
  color: #ff9800;
  font-weight: 600;
  font-size: 16px;
}

.rating-count {
  color: #666;
  font-size: 12px;
}

@media (max-width: 768px) {
  .admin-container {
    flex-direction: column;
  }
  
  .admin-sidebar {
    width: 100%;
  }
  
  .admin-content {
    padding: 20px;
  }
  
  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .user-header {
    flex-direction: column;
    text-align: center;
  }
  
  .user-details-grid {
    grid-template-columns: 1fr;
  }
}
</style>
