<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Publish System Announcement</h3>
        <button class="close-btn" @click="closeModal">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="publishNotification">
          <!-- Target User Type Selection -->
          <div class="form-group">
            <label>Target User Type</label>
            <div class="radio-group">
              <label class="radio-item">
                <input 
                  type="radio" 
                  v-model="formData.targetType" 
                  value="all"
                  @change="onTargetTypeChange"
                >
                <span>All Users</span>
              </label>
              <label class="radio-item">
                <input 
                  type="radio" 
                  v-model="formData.targetType" 
                  value="customers"
                  @change="onTargetTypeChange"
                >
                <span>Customer Users</span>
              </label>
              <label class="radio-item">
                <input 
                  type="radio" 
                  v-model="formData.targetType" 
                  value="providers"
                  @change="onTargetTypeChange"
                >
                <span>Provider Users</span>
              </label>
            </div>
          </div>

          <!-- User Selection (shown when selecting specific user types) -->
          <div v-if="formData.targetType !== 'all'" class="form-group">
            <div class="selection-header">
              <label>Select Users</label>
              <div class="bulk-actions">
                <button 
                  type="button" 
                  class="bulk-btn select-all-btn"
                  @click="selectAllUsers"
                  :disabled="loadingUsers || filteredUsers.length === 0"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Select All {{ getCurrentRoleName() }}
                </button>
                <button 
                  type="button" 
                  class="bulk-btn clear-all-btn"
                  @click="clearAllUsers"
                  :disabled="formData.selectedUsers.length === 0"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Clear Selection
                </button>
              </div>
            </div>
            
            <div class="selection-info">
              <span class="selection-count">
                Selected {{ formData.selectedUsers.length }} / {{ filteredUsers.length }} users
              </span>
            </div>
            
            <div class="user-selection">
              <div class="search-box">
                <input 
                  type="text" 
                  v-model="searchKeyword" 
                  placeholder="Search by username or email..."
                  @input="searchUsers"
                >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              
              <div class="user-list">
                <div v-if="loadingUsers" class="loading">Loading users...</div>
                <div v-else-if="filteredUsers.length === 0" class="no-users">No users found</div>
                <div v-else class="user-items">
                  <label 
                    v-for="user in filteredUsers" 
                    :key="user.user_id" 
                    class="user-item"
                  >
                    <input 
                      type="checkbox" 
                      :value="user.user_id" 
                      v-model="formData.selectedUsers"
                    >
                    <div class="user-info">
                      <div class="user-name">{{ user.username }}</div>
                      <div class="user-email">{{ user.email }}</div>
                      <div class="user-role">{{ getUserRoleName(user.role_id) }}</div>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Notification Content -->
          <div class="form-group">
            <label>Notification Content <span class="required">*</span></label>
            <textarea 
              v-model="formData.message" 
              placeholder="Enter notification content..."
              rows="4"
              required
            ></textarea>
            <div class="char-count">{{ formData.message.length }}/500</div>
          </div>

          <!-- Preview -->
          <div v-if="formData.message" class="form-group">
            <label>Preview</label>
            <div class="preview">
              <div class="preview-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>System Notification</span>
              </div>
              <div class="preview-content">{{ formData.message }}</div>
            </div>
          </div>
        </form>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn-cancel" @click="closeModal">Cancel</button>
        <button 
          type="button" 
          class="btn-publish" 
          @click="publishNotification"
          :disabled="!canPublish || publishing"
        >
          <svg v-if="publishing" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinning">
            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ publishing ? 'Publishing...' : 'Publish Notification' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { adminAPI } from '@/api/auth'

export default {
  name: 'PublishNotificationModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      formData: {
        targetType: 'all',
        message: '',
        selectedUsers: []
      },
      searchKeyword: '',
      users: [],
      filteredUsers: [],
      loadingUsers: false,
      publishing: false
    }
  },
  computed: {
    canPublish() {
      if (!this.formData.message.trim()) return false
      if (this.formData.message.length > 500) return false
      if (this.formData.targetType !== 'all' && this.formData.selectedUsers.length === 0) return false
      return true
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        this.resetForm()
        this.loadUsers()
      }
    }
  },
  methods: {
    resetForm() {
      this.formData = {
        targetType: 'all',
        message: '',
        selectedUsers: []
      }
      this.searchKeyword = ''
      this.users = []
      this.filteredUsers = []
    },
    
    async loadUsers() {
      this.loadingUsers = true
      try {
        if (this.formData.targetType === 'customers') {
          // Load only customer users
          const customersResponse = await adminAPI.getAllUsers(1)
          this.users = customersResponse.data || []
        } else if (this.formData.targetType === 'providers') {
          // Load only provider users
          const providersResponse = await adminAPI.getAllUsers(2)
          this.users = providersResponse.data || []
        } else {
          // Load all users (for 'all' option)
          const customersResponse = await adminAPI.getAllUsers(1)
          const providersResponse = await adminAPI.getAllUsers(2)
          const customers = customersResponse.data || []
          const providers = providersResponse.data || []
          this.users = [...customers, ...providers]
        }
        
        this.filteredUsers = this.users
      } catch (error) {
        console.error('Failed to load users:', error)
        this.$emit('error', 'Failed to load user list')
      } finally {
        this.loadingUsers = false
      }
    },
    
    async onTargetTypeChange() {
      this.formData.selectedUsers = []
      await this.loadUsers()
    },
    
    getCurrentRoleName() {
      if (this.formData.targetType === 'customers') {
        return 'Customers'
      } else if (this.formData.targetType === 'providers') {
        return 'Providers'
      }
      return 'Users'
    },
    
    getUserRoleName(roleId) {
      const roleMap = {
        1: 'Customer',
        2: 'Provider',
        3: 'Admin'
      }
      return roleMap[roleId] || 'Unknown'
    },
    
    selectAllUsers() {
      this.formData.selectedUsers = this.filteredUsers.map(user => user.user_id)
    },
    
    clearAllUsers() {
      this.formData.selectedUsers = []
    },
    
    searchUsers() {
      if (!this.searchKeyword.trim()) {
        this.filteredUsers = this.users
        return
      }
      
      const keyword = this.searchKeyword.toLowerCase()
      this.filteredUsers = this.users.filter(user => 
        user.username.toLowerCase().includes(keyword) ||
        user.email.toLowerCase().includes(keyword)
      )
    },
    
    async publishNotification() {
      if (!this.canPublish) return
      
      this.publishing = true
      try {
        if (this.formData.targetType === 'all') {
          // Send to all users
          await this.sendToAllUsers()
        } else if (this.formData.targetType === 'customers') {
          // Send to selected customers
          await this.sendToSelectedUsers('customer')
        } else if (this.formData.targetType === 'providers') {
          // Send to selected providers
          await this.sendToSelectedUsers('provider')
        }
        
        this.$emit('success', 'Notification published successfully')
        this.closeModal()
      } catch (error) {
        console.error('Failed to publish notification:', error)
        this.$emit('error', 'Failed to publish notification: ' + error.message)
      } finally {
        this.publishing = false
      }
    },
    
    async sendToAllUsers() {
      // Get all customers and providers
      const customersResponse = await adminAPI.getAllUsers(1)
      const providersResponse = await adminAPI.getAllUsers(2)
      
      const customers = customersResponse.data || []
      const providers = providersResponse.data || []
      
      // Send to all customers
      for (const customer of customers) {
        try {
          await adminAPI.sendNotificationToCustomer(customer.id, this.formData.message)
        } catch (error) {
          console.error(`Failed to send to customer ${customer.id}:`, error)
        }
      }
      
      // Send to all providers
      for (const provider of providers) {
        try {
          await adminAPI.sendNotificationToProvider(provider.id, this.formData.message)
        } catch (error) {
          console.error(`Failed to send to provider ${provider.id}:`, error)
        }
      }
    },
    
    async sendToSelectedUsers(userType) {
      const selectedUserIds = this.formData.selectedUsers
      
      for (const userId of selectedUserIds) {
        try {
          if (userType === 'customer') {
            await adminAPI.sendNotificationToCustomer(userId, this.formData.message)
          } else if (userType === 'provider') {
            await adminAPI.sendNotificationToProvider(userId, this.formData.message)
          }
        } catch (error) {
          console.error(`Failed to send to user ${userId}:`, error)
        }
      }
    },
    
    closeModal() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #6b7280;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #dc2626;
}

.radio-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.radio-item:hover {
  border-color: #4f46e5;
  background: #f8fafc;
}

.radio-item input[type="radio"] {
  margin: 0;
}

.radio-item input[type="radio"]:checked + span {
  color: #4f46e5;
  font-weight: 500;
}

/* 选择头部样式 */
.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.selection-header label {
  margin-bottom: 0;
}

.bulk-actions {
  display: flex;
  gap: 8px;
}

.bulk-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bulk-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.bulk-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.select-all-btn {
  border-color: #10b981;
  color: #10b981;
}

.select-all-btn:hover:not(:disabled) {
  background: #ecfdf5;
  border-color: #059669;
}

.clear-all-btn {
  border-color: #ef4444;
  color: #ef4444;
}

.clear-all-btn:hover:not(:disabled) {
  background: #fef2f2;
  border-color: #dc2626;
}

/* 选择信息样式 */
.selection-info {
  margin-bottom: 12px;
}

.selection-count {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

.user-selection {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  overflow: hidden;
}

.search-box {
  position: relative;
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.search-box input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.search-box svg {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
}

.user-list {
  max-height: 200px;
  overflow-y: auto;
}

.loading, .no-users {
  padding: 20px;
  text-align: center;
  color: #6b7280;
}

.user-items {
  padding: 8px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s ease;
}

.user-item:hover {
  background: #f3f4f6;
}

.user-item input[type="checkbox"] {
  margin: 0;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: #111827;
}

.user-email {
  font-size: 13px;
  color: #6b7280;
}

.user-role {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  margin-top: 2px;
  display: inline-block;
}

.user-role:nth-child(3) {
  background: #dbeafe;
  color: #1e40af;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.preview {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 500;
  color: #374151;
}

.preview-content {
  padding: 12px;
  background: white;
  white-space: pre-wrap;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn-cancel, .btn-publish {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-cancel {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-cancel:hover {
  background: #f3f4f6;
}

.btn-publish {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none;
  color: white;
}

.btn-publish:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  transform: translateY(-1px);
}

.btn-publish:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .radio-group {
    flex-direction: column;
  }
  
  .selection-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .bulk-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .bulk-btn {
    flex: 1;
    justify-content: center;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn-cancel, .btn-publish {
    width: 100%;
    justify-content: center;
  }
}
</style>
