<template>
  <AdminLayout 
    page-title="User Management" 
    :breadcrumb="[{ name: 'Admin', path: '/admin' }, { name: 'User Management' }]"
  >
    <AdminPage 
      title="User List"
      description="Manage all platform user information"
      :loading="loading"
      :error="error"
      @retry="loadUsers"
    >
      <template #headerActions>
        <div class="filter-controls">
          <select v-model="selectedRole" @change="onRoleFilterChange" class="role-filter">
            <option value="">All Roles</option>
            <option value="1">Customer</option>
            <option value="2">Service Provider</option>
            <option value="3">Admin</option>
          </select>
          <div class="search-box">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search username or email..."
              class="search-input"
            />
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="search-icon">
              <path d="M21 21L16.514 16.506L21 21ZM19 10.5C19 15.194 15.194 19 10.5 19C5.806 19 2 15.194 2 10.5C2 5.806 5.806 2 10.5 2C15.194 2 19 5.806 19 10.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </template>

      <AdminTable
        :data="filteredUsers"
        :columns="tableColumns"
        :loading="loading"
        :show-pagination="true"
        :page-size="10"
        empty-title="No User Data"
        empty-description="No users found matching the criteria"
      >
        <template #cell-role_id="{ value }">
          <span :class="getUserTypeClass(value)">{{ getUserTypeName(value) }}</span>
        </template>
        
        <template #cell-actions="{ row }">
          <div class="action-buttons">
            <button @click="viewUser(row.user_id)" class="action-btn view-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 12S5 4 12 4S23 12 23 12S19 20 12 20S1 12 1 12Z" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
              </svg>
              View
            </button>
            <button @click="deleteUser(row.user_id, row.username)" class="action-btn delete-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Delete
            </button>
          </div>
        </template>
      </AdminTable>
    </AdminPage>
  </AdminLayout>
</template>

<script>
import AdminLayout from '@/components/AdminLayout.vue'
import AdminPage from '@/components/AdminPage.vue'
import AdminTable from '@/components/AdminTable.vue'
import { adminAPI } from '@/api/auth.js'

export default {
  name: 'UserManagement',
  components: {
    AdminLayout,
    AdminPage,
    AdminTable
  },
  data() {
    return {
      users: [],
      loading: false,
      error: null,
      selectedRole: '',
      searchQuery: '',
      tableColumns: [
        { key: 'username', title: 'Username', sortable: true },
        { key: 'role_id', title: 'User Type', sortable: true },
        { key: 'email', title: 'Email', sortable: true },
        { key: 'created_at', title: 'Registration Time', sortable: true },
        { key: 'actions', title: 'Actions', sortable: false }
      ]
    }
  },
  computed: {
    filteredUsers() {
      let filtered = this.users

      // Filter by role
      if (this.selectedRole) {
        filtered = filtered.filter(user => user.role_id == this.selectedRole)
      }

      // Filter by search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query)
        )
      }

      return filtered
    }
  },
  async mounted() {
    await this.loadUsers()
  },
  methods: {
    async loadUsers(roleId = null) {
      this.loading = true
      this.error = null
      try {
        // Call real API to get user list
        const response = await adminAPI.getAllUsers(roleId)
        
        if (response.success) {
          this.users = response.data
        } else {
          throw new Error(response.message || 'Failed to get user data')
        }
      } catch (error) {
        this.error = 'Failed to load user data: ' + error.message
        console.error('Failed to load users:', error)
      } finally {
        this.loading = false
      }
    },
    onRoleFilterChange() {
      // When role filter changes, reload user data
      this.loadUsers(this.selectedRole || null)
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
        1: 'role-customer',
        2: 'role-provider',
        3: 'role-admin'
      }
      return classMap[roleId] || 'role-unknown'
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        return new Date(dateString).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        return 'Invalid Date'
      }
    },
    viewUser(userId) {
      this.$router.push(`/admin/users/${userId}`)
    },
    async deleteUser(userId, username) {
      if (confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
        try {
          // Call real API to delete user
          const response = await adminAPI.deleteUser(userId)
          
          if (response.success) {
            // Remove user from list
            this.users = this.users.filter(user => user.user_id !== userId)
            alert('User deleted successfully')
          } else {
            alert('Failed to delete user: ' + (response.message || 'Unknown error'))
          }
        } catch (error) {
          // Check if Token expired
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
    }
  }
}
</script>

<style scoped>
.filter-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-filter {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  color: #374151;
  min-width: 120px;
}

.role-filter:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  padding: 8px 12px 8px 36px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  color: #374151;
  width: 250px;
}

.search-input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.search-icon {
  position: absolute;
  left: 12px;
  color: #9ca3af;
  pointer-events: none;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn {
  background: #f3f4f6;
  color: #374151;
}

.view-btn:hover {
  background: #e5e7eb;
}

.delete-btn {
  background: #fef2f2;
  color: #dc2626;
}

.delete-btn:hover {
  background: #fee2e2;
}

/* Role badges */
.role-customer {
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-provider {
  background: #dcfce7;
  color: #166534;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-admin {
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-unknown {
  background: #f3f4f6;
  color: #6b7280;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    gap: 12px;
    width: 100%;
  }
  
  .search-input {
    width: 100%;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .action-btn {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .role-filter {
    min-width: 100px;
  }
  
  .action-btn {
    padding: 4px 8px;
    font-size: 12px;
  }
}
</style>