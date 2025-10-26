<template>
  <div class="customer-task-detail-page">
    <NavBar />
    
    <div class="main-content">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading task details...</p>
      </div>
      
      <div v-else-if="!task" class="error-state">
        <div class="error-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
            <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <h3>Task Not Found</h3>
        <p>Sorry, the task you are looking for does not exist or has been deleted</p>
        <router-link to="/?role=customer" class="back-btn">Return to Homepage</router-link>
      </div>
      
      <div v-else class="task-detail">
        <!-- Back button and breadcrumbs -->
        <div class="task-header">
          <div class="back-button" @click="goBack">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Back
          </div>
          
          <div class="breadcrumb">
            <router-link to="/?role=customer" class="breadcrumb-link">My Tasks</router-link>
            <span class="breadcrumb-separator">></span>
            <span class="breadcrumb-current">Task Details</span>
          </div>
        </div>

        <!-- Task basic information -->
        <div class="task-basic-info">
          <h1 class="task-title">{{ task.title }}</h1>
          <div class="task-meta">
            <div class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 7H17V17H7V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 3V5M17 3V5M7 19V21M17 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="category">{{ getServiceTypeName(task.service_type) }}</span>
            </div>
            <div class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="location">{{ task.location }}</span>
            </div>
            <div class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="time">{{ formatDateTime(task.service_start_time) }} - {{ formatDateTime(task.service_end_time) }}</span>
            </div>
            <div class="meta-item price">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="12" y1="1" x2="12" y2="23" stroke="currentColor" stroke-width="2"/>
                <path d="M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="amount">S${{ task.price }}</span>
            </div>
          </div>
        </div>

        <!-- Separator -->
        <div class="divider"></div>

        <!-- Task detailed information -->
        <div class="task-details">
          <h3>Task Details</h3>
          <div class="detail-content">
            <p>{{ task.description }}</p>
          </div>
        </div>

        <!-- Address information -->
        <div class="task-requirements" v-if="task.address">
          <h3>Service Address</h3>
          <div class="detail-content">
            <p>{{ task.address }}</p>
          </div>
        </div>

        <!-- Separator -->
        <div class="divider"></div>

        <!-- Task status information -->
        <div class="task-status-info">
          <h3>Order Status</h3>
          <div class="status-content">
            <div class="status-item">
              <span class="status-label">Current Status:</span>
              <span :class="['status-badge', task.status]">{{ getStatusText(task.status) }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">发布时间:</span>
              <span class="status-value">{{ formatTime(task.created_at) }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">更新时间:</span>
              <span class="status-value">{{ formatTime(task.updated_at) }}</span>
            </div>
            <div v-if="task.payment_status" class="status-item">
              <span class="status-label">支付状态:</span>
              <span class="status-value">{{ getPaymentStatusText(task.payment_status) }}</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import { customerAPI } from '@/api/auth.js'

export default {
  name: 'CustomerTaskDetail',
  components: {
    NavBar
  },
  data() {
    return {
      loading: true,
      task: null
    }
  },
  created() {
    this.loadTask()
  },
  methods: {
    async loadTask() {
      const orderId = this.$route.params.id
      
      try {
        const response = await customerAPI.getOrderDetail(orderId)
        if (response.success && response.data) {
          this.task = response.data
        } else {
          console.error('Failed to load order detail:', response.message)
          this.task = null
        }
      } catch (error) {
        console.error('Error loading order detail:', error)
        this.task = null
        alert('加载订单详情失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    getStatusText(status) {
      const statusMap = {
        'pending': '待接单',
        'accepted': '已接单',
        'in_progress': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return statusMap[status] || '未知状态'
    },
    formatTime(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    formatDateTime(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getServiceTypeName(serviceType) {
      const typeMap = {
        'it_technology': 'IT技术',
        'design_consulting': '设计咨询',
        'education_training': '教育培训',
        'cleaning_repair': '清洁维修',
        'other': '其他'
      }
      return typeMap[serviceType] || serviceType
    },
    getPaymentStatusText(paymentStatus) {
      const statusMap = {
        'pending': '待支付',
        'paid': '已支付',
        'refunded': '已退款'
      }
      return statusMap[paymentStatus] || paymentStatus
    },
    goBack() {
      this.$router.go(-1)
    }
  }
}
</script>

<style scoped>
.customer-task-detail-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  min-height: calc(100vh - 60px);
  padding: 20px;
}

.loading-container, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #00b894;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  color: #e74c3c;
  margin-bottom: 20px;
}

.error-state h3 {
  font-size: 20px;
  color: #666;
  margin: 0 0 10px 0;
}

.error-state p {
  color: #999;
  font-size: 14px;
  margin: 0 0 20px 0;
}

.back-btn {
  display: inline-block;
  padding: 10px 20px;
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.task-detail {
  max-width: 100%;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f8f9fa;
  color: #00b894;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: #00b894;
  color: white;
  border-color: #00b894;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.breadcrumb-link {
  color: #00b894;
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  color: #ccc;
}

.breadcrumb-current {
  color: #999;
}

.task-basic-info {
  margin-bottom: 30px;
}

.task-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 20px 0;
  line-height: 1.3;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 16px;
}

.meta-item svg {
  color: #00b894;
  flex-shrink: 0;
}

.category {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.price .amount {
  color: #00b894;
  font-weight: 600;
  font-size: 18px;
}

.divider {
  height: 1px;
  background: #e9ecef;
  margin: 30px 0;
}

.task-details, .task-requirements, .task-status-info {
  margin-bottom: 30px;
}

.task-details h3, .task-requirements h3, .task-status-info h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 15px 0;
}

.detail-content p {
  color: #666;
  line-height: 1.6;
  font-size: 16px;
  margin: 0;
}

.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.requirements-list li {
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
  color: #666;
  line-height: 1.5;
  font-size: 16px;
}

.requirements-list li::before {
  content: '•';
  color: #00b894;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.status-label {
  color: #666;
  font-size: 14px;
  min-width: 80px;
}

.status-value {
  color: #333;
  font-weight: 500;
  font-size: 16px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.open {
  background: #d4edda;
  color: #155724;
}

.status-badge.in-progress {
  background: #d1ecf1;
  color: #0c5460;
}

.status-badge.completed {
  background: #d4edda;
  color: #155724;
}

.status-badge.cancelled {
  background: #f8d7da;
  color: #721c24;
}


@media (max-width: 768px) {
  .main-content {
    padding: 15px;
  }
  
  .task-title {
    font-size: 24px;
  }
  
  .task-meta {
    flex-direction: column;
    gap: 15px;
  }
  
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .status-content {
    gap: 10px;
  }
  
  .status-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .status-label {
    min-width: auto;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 15px;
  }
  
  .cancel-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
