<template>
  <AdminLayout 
    page-title="Notification Management" 
    :breadcrumb="[{ name: 'Admin', path: '/admin' }, { name: 'Notification Management' }]"
  >
    <AdminPage 
      title="Notification Management"
      description="Manage system announcements and platform notifications"
      :loading="loading"
      :error="error"
      @retry="loadNotifications"
    >
      <template #headerActions>
        <button class="publish-btn" @click="showPublishModal = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 13H13V19H11V13H5V11H11V5H13V11H19V13Z" fill="currentColor"/>
          </svg>
          Publish System Announcement
        </button>
      </template>

      <AdminTable
        :data="notifications"
        :columns="tableColumns"
        :loading="loading"
        :show-pagination="true"
        :page-size="10"
        empty-title="No Notifications"
        empty-description="No system announcements have been published yet"
      >
        <template #cell-created_at="{ value }">
          {{ formatDate(value) }}
        </template>
        
        <template #cell-content="{ value }">
          <div class="content-preview">
            {{ value.length > 100 ? value.substring(0, 100) + '...' : value }}
          </div>
        </template>
      </AdminTable>
    </AdminPage>

    <!-- Publish Notification Modal -->
    <PublishNotificationModal
      :show="showPublishModal"
      @close="showPublishModal = false"
      @success="onNotificationPublished"
      @error="onNotificationError"
    />

    <!-- Success Message -->
    <div v-if="showSuccessMessage" class="success-message">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      {{ successMessage }}
    </div>

    <!-- Error Message -->
    <div v-if="showErrorMessage" class="error-message">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      {{ errorMessage }}
    </div>
  </AdminLayout>
</template>

<script>
import AdminLayout from '@/components/AdminLayout.vue'
import AdminPage from '@/components/AdminPage.vue'
import AdminTable from '@/components/AdminTable.vue'
import PublishNotificationModal from '@/components/PublishNotificationModal.vue'

export default {
  name: 'NotificationManagement',
  components: {
    AdminLayout,
    AdminPage,
    AdminTable,
    PublishNotificationModal
  },
  data() {
    return {
      notifications: [],
      loading: false,
      error: null,
      showPublishModal: false,
      showSuccessMessage: false,
      showErrorMessage: false,
      successMessage: '',
      errorMessage: '',
      tableColumns: [
        { key: 'id', title: 'ID', sortable: true },
        { key: 'title', title: 'Title', sortable: true },
        { key: 'content', title: 'Content', sortable: true },
        { key: 'created_at', title: 'Published At', sortable: true }
      ]
    }
  },
  async mounted() {
    await this.loadNotifications()
  },
  methods: {
    async loadNotifications() {
      this.loading = true
      this.error = null
      try {
        // Mock data for now - replace with real API call
        this.notifications = [
          {
            id: 1,
            title: 'Platform Maintenance Notice',
            content: 'The platform will undergo maintenance tonight from 10:00-12:00, during which services may be affected.',
            created_at: '2024-01-15T10:30:00Z'
          },
          {
            id: 2,
            title: 'New Feature Release',
            content: 'We are excited to announce the release of our new task tracking feature!',
            created_at: '2024-01-14T14:20:00Z'
          }
        ]
      } catch (error) {
        this.error = 'Failed to load notifications: ' + error.message
        console.error('Failed to load notifications:', error)
      } finally {
        this.loading = false
      }
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
    onNotificationPublished(message) {
      this.successMessage = message
      this.showSuccessMessage = true
      this.showErrorMessage = false
      
      // Auto-hide success message after 3 seconds
      setTimeout(() => {
        this.showSuccessMessage = false
      }, 3000)
      
      // Reload notification list
      this.loadNotifications()
    },
    onNotificationError(message) {
      this.errorMessage = message
      this.showErrorMessage = true
      this.showSuccessMessage = false
      
      // Auto-hide error message after 5 seconds
      setTimeout(() => {
        this.showErrorMessage = false
      }, 5000)
    }
  }
}
</script>

<style scoped>
.publish-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
}

.publish-btn:hover {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
}

.content-preview {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.success-message, .error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 8px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  animation: slideIn 0.3s ease-out;
}

.success-message {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .publish-btn {
    padding: 8px 16px;
    font-size: 13px;
  }
  
  .content-preview {
    max-width: 200px;
  }
  
  .success-message, .error-message {
    top: 10px;
    right: 10px;
    left: 10px;
    padding: 12px 16px;
  }
}

@media (max-width: 480px) {
  .publish-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
  
  .content-preview {
    max-width: 150px;
  }
}
</style>