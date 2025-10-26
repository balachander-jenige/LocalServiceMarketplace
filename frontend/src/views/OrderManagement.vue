<template>
  <AdminLayout 
    page-title="Order Management" 
    :breadcrumb="[{ name: 'Admin', path: '/admin' }, { name: 'Order Management' }]"
  >
    <AdminPage 
      title="Order List"
      description="Manage all platform order information"
      :loading="loading"
      :error="error"
      @retry="loadOrders"
    >
      <template #headerActions>
        <div class="filter-controls">
          <select v-model="statusFilter" @change="loadOrders" class="filter-select">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="accepted">Accepted</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
            <option value="paid">Paid</option>
          </select>
        </div>
      </template>

      <AdminTable
        :data="orders"
        :columns="tableColumns"
        :loading="loading"
        :show-pagination="true"
        :page-size="10"
        empty-title="No Orders"
        empty-description="No orders found matching the criteria"
      >
        <template #cell-status="{ value }">
          <span :class="getStatusClass(value)">{{ getStatusName(value) }}</span>
        </template>
        
        <template #cell-price="{ value }">
          ${{ value }}
        </template>
        
        <template #cell-created_at="{ value }">
          {{ formatDate(value) }}
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
  name: 'OrderManagement',
  components: {
    AdminLayout,
    AdminPage,
    AdminTable
  },
  data() {
    return {
      orders: [],
      loading: false,
      error: null,
      statusFilter: '',
      tableColumns: [
        { key: 'id', title: 'Order ID', sortable: true },
        { key: 'customer_id', title: 'Customer ID', sortable: true },
        { key: 'provider_id', title: 'Provider ID', sortable: true },
        { key: 'title', title: 'Task Title', sortable: true },
        { key: 'status', title: 'Status', sortable: true },
        { key: 'price', title: 'Price', sortable: true },
        { key: 'created_at', title: 'Created Time', sortable: true }
      ]
    }
  },
  async mounted() {
    await this.loadOrders()
  },
  methods: {
    async loadOrders() {
      this.loading = true
      this.error = null
      try {
        // Check if Token exists
        const token = localStorage.getItem('access_token')
        if (!token) {
          this.error = 'Not logged in or login expired, please login again'
          return
        }

        // Call real API to get all orders
        const response = await adminAPI.getAllOrders(this.statusFilter || null)
        
        if (response.success) {
          this.orders = response.data
        } else {
          this.error = response.message || 'Failed to load orders data'
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
          this.error = 'Failed to load orders: ' + error.message
        }
        console.error('Failed to load orders:', error)
      } finally {
        this.loading = false
      }
    },
    getStatusName(status) {
      const statusMap = {
        pending: 'Pending',
        accepted: 'Accepted',
        in_progress: 'In Progress',
        completed: 'Completed',
        cancelled: 'Cancelled',
        paid: 'Paid'
      }
      return statusMap[status] || status
    },
    getStatusClass(status) {
      const classMap = {
        pending: 'status-pending',
        accepted: 'status-accepted',
        in_progress: 'status-progress',
        completed: 'status-completed',
        cancelled: 'status-cancelled',
        paid: 'status-paid'
      }
      return classMap[status] || 'status-unknown'
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

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  color: #374151;
  min-width: 120px;
}

.filter-select:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* Status badges */
.status-pending {
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-accepted {
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-progress {
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-completed {
  background: #dcfce7;
  color: #166534;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-cancelled {
  background: #fee2e2;
  color: #dc2626;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-paid {
  background: #dcfce7;
  color: #166534;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-unknown {
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
  
  .filter-select {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .filter-select {
    min-width: 100px;
  }
}
</style>