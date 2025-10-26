<template>
  <AdminLayout 
    page-title="Task Management" 
    :breadcrumb="[{ name: 'Admin', path: '/admin' }, { name: 'Task Management' }]"
  >
    <AdminPage 
      title="Pending Review Tasks"
      description="Review user published tasks and decide whether to approve"
      :loading="loading"
      :error="error"
      @retry="loadTasks"
    >
      <template #headerActions>
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search order ID, customer ID or task title..."
            class="search-input"
          />
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="search-icon">
            <path d="M21 21L16.514 16.506L21 21ZM19 10.5C19 15.194 15.194 19 10.5 19C5.806 19 2 15.194 2 10.5C2 5.806 5.806 2 10.5 2C15.194 2 19 5.806 19 10.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </template>

      <AdminTable
        :data="filteredTasks"
        :columns="tableColumns"
        :loading="loading"
        :show-pagination="true"
        :page-size="10"
        empty-title="No Pending Review Tasks"
        empty-description="No tasks need review currently"
      >
        <template #cell-service_type="{ value }">
          {{ getServiceTypeName(value) }}
        </template>
        
        <template #cell-price="{ value }">
          ${{ value }}
        </template>
        
        <template #cell-created_at="{ value }">
          {{ formatDate(value) }}
        </template>
        
        <template #cell-actions="{ row }">
          <div class="action-buttons">
            <button @click="approveTask(row.id, row.title)" class="action-btn approve-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Approve
            </button>
            <button @click="rejectTask(row.id, row.title)" class="action-btn reject-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Reject
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
  name: 'TaskManagement',
  components: {
    AdminLayout,
    AdminPage,
    AdminTable
  },
  data() {
    return {
      tasks: [],
      loading: false,
      error: null,
      searchQuery: '',
      tableColumns: [
        { key: 'id', title: 'Order ID', sortable: true },
        { key: 'customer_id', title: 'Customer ID', sortable: true },
        { key: 'title', title: 'Task Title', sortable: true },
        { key: 'service_type', title: 'Service Type', sortable: true },
        { key: 'price', title: 'Price', sortable: true },
        { key: 'location', title: 'Location', sortable: true },
        { key: 'created_at', title: 'Created Time', sortable: true },
        { key: 'actions', title: 'Actions', sortable: false }
      ]
    }
  },
  computed: {
    filteredTasks() {
      if (!this.searchQuery) return this.tasks
      
      const query = this.searchQuery.toLowerCase()
      return this.tasks.filter(task => 
        task.id.toString().includes(query) ||
        task.customer_id.toString().includes(query) ||
        task.title.toLowerCase().includes(query)
      )
    }
  },
  async mounted() {
    await this.loadTasks()
  },
  methods: {
    async loadTasks() {
      this.loading = true
      this.error = null
      try {
        // Check if Token exists
        const token = localStorage.getItem('access_token')
        if (!token) {
          this.error = 'Not logged in or login expired, please login again'
          return
        }

        // Call real API to get pending review orders
        const response = await adminAPI.getPendingReviewOrders()
        
        if (response.success) {
          this.tasks = response.data
        } else {
          this.error = response.message || 'Failed to load pending review order data'
        }
      } catch (error) {
        // Check if Token expired
        if (error.message.includes('expired') || error.status === 401) {
          this.error = 'Login expired, please login again'
          // Clear local storage
          localStorage.removeItem('access_token')
          sessionStorage.removeItem('currentUser')
          // Delay redirect to let user see error message
          setTimeout(() => {
            this.$router.push('/login')
          }, 2000)
        } else {
          this.error = 'Failed to load pending review order data: ' + error.message
        }
        console.error('Failed to load pending review orders:', error)
      } finally {
        this.loading = false
      }
    },
    getServiceTypeName(serviceType) {
      const typeMap = {
        cleaning_repair: 'Cleaning Repair',
        it_technology: 'IT Technology',
        design_creative: 'Design Creative',
        marketing_sales: 'Marketing Sales',
        education_training: 'Education Training',
        consulting_legal: 'Consulting Legal',
        logistics_transport: 'Logistics Transport',
        other: 'Other'
      }
      return typeMap[serviceType] || serviceType
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
    async approveTask(orderId, orderTitle) {
      if (confirm(`Are you sure you want to approve order "${orderTitle}"?`)) {
        try {
          // Call real API to approve order
          const response = await adminAPI.approveOrder(orderId, true)
          
          if (response.success) {
            // Remove order from list
            this.tasks = this.tasks.filter(order => order.id !== orderId)
            alert('Order approved successfully')
          } else {
            alert('Failed to approve order: ' + (response.message || 'Unknown error'))
          }
        } catch (error) {
          // Check if Token expired
          if (error.message.includes('expired') || error.status === 401) {
            alert('Login expired, please login again')
            localStorage.removeItem('access_token')
            sessionStorage.removeItem('currentUser')
            this.$router.push('/login')
          } else {
            alert('Failed to approve order: ' + error.message)
          }
          console.error('Failed to approve order:', error)
        }
      }
    },
    async rejectTask(orderId, orderTitle) {
      const reason = prompt(`Please enter the reason for rejecting order "${orderTitle}":`)
      if (reason && reason.trim()) {
        try {
          // Call real API to reject order
          const response = await adminAPI.approveOrder(orderId, false, reason)
          
          if (response.success) {
            // Remove order from list
            this.tasks = this.tasks.filter(order => order.id !== orderId)
            alert('Order rejected')
          } else {
            alert('Failed to reject order: ' + (response.message || 'Unknown error'))
          }
        } catch (error) {
          // Check if Token expired
          if (error.message.includes('expired') || error.status === 401) {
            alert('Login expired, please login again')
            localStorage.removeItem('access_token')
            sessionStorage.removeItem('currentUser')
            this.$router.push('/login')
          } else {
            alert('Failed to reject order: ' + error.message)
          }
          console.error('Failed to reject order:', error)
        }
      }
    }
  }
}
</script>

<style scoped>
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
  width: 300px;
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

.approve-btn {
  background: #f0fdf4;
  color: #166534;
}

.approve-btn:hover {
  background: #dcfce7;
}

.reject-btn {
  background: #fef2f2;
  color: #dc2626;
}

.reject-btn:hover {
  background: #fee2e2;
}

/* Responsive Design */
@media (max-width: 768px) {
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
  .action-btn {
    padding: 4px 8px;
    font-size: 12px;
  }
}
</style>