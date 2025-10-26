<template>
  <div class="order-detail-page">
    <NavBar />
    
    <div class="main-content">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading order details...</p>
      </div>
      
      <div v-else-if="!order" class="error-state">
        <div class="error-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
            <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <h3>Order Not Found</h3>
        <p>Sorry, the order you are looking for does not exist or has been deleted</p>
        <router-link to="/?role=provider" class="back-btn">Return to Homepage</router-link>
      </div>
      
      <div v-else class="order-detail">
        <!-- Back button and breadcrumbs -->
        <div class="order-header">
          <div class="back-button" @click="goBack">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Back
          </div>
          
          <div class="breadcrumb">
            <router-link to="/?role=provider" class="breadcrumb-link">Find Tasks</router-link>
            <span class="breadcrumb-separator">></span>
            <span class="breadcrumb-current">Order Details</span>
          </div>
        </div>

        <!-- Order basic information -->
        <div class="order-basic-info">
          <h1 class="order-title">{{ order.title }}</h1>
          <div class="order-meta">
            <div class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 7H17V17H7V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 3V5M17 3V5M7 19V21M17 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="category">{{ getServiceTypeName(order.service_type) }}</span>
            </div>
            <div class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="location">{{ order.location }}</span>
            </div>
            <div v-if="order.address" class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="address">{{ order.address }}</span>
            </div>
            <div class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
              </svg>
              <span class="time">{{ formatDateTime(order.service_start_time) }} - {{ formatDateTime(order.service_end_time) }}</span>
            </div>
            <div class="meta-item price">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="12" y1="1" x2="12" y2="23" stroke="currentColor" stroke-width="2"/>
                <path d="M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="amount">S${{ order.price }}</span>
            </div>
          </div>
        </div>

        <!-- Separator -->
        <div class="divider"></div>

        <!-- Order detailed information -->
        <div class="order-details">
          <h3>Order Details</h3>
          <div class="detail-content">
            <p>{{ order.description }}</p>
          </div>
        </div>

        <!-- Accept order button for provider -->
        <div v-if="isProvider" class="action-buttons">
          <button 
            class="apply-btn" 
            :class="{ 'applying': applying, 'disabled': order.status !== 'pending' }"
            :disabled="applying || order.status !== 'pending'"
            @click="acceptOrder"
          >
            <div v-if="applying" class="loading-spinner-small"></div>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ applying ? 'Accepting...' : (order.status === 'pending' ? 'Accept Order' : 'Order Accepted') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import { providerAPI, customerAPI } from '@/api/auth.js'

export default {
  name: 'OrderDetail',
  components: {
    NavBar
  },
  data() {
    return {
      loading: true,
      order: null,
      applying: false
    }
  },
  computed: {
    isProvider() {
      // Check if user is provider role
      const currentUser = sessionStorage.getItem('currentUser')
      if (currentUser) {
        const user = JSON.parse(currentUser)
        return user.role === 'provider'
      }
      // If no logged-in user info, use route parameter
      return this.$route.query.role !== 'customer'
    }
  },
  created() {
    this.loadOrder()
  },
  methods: {
    async loadOrder() {
      const orderId = this.$route.params.id
      
      try {
        this.loading = true
        
        let response
        if (this.isProvider) {
          // Provider: try to get from available orders first
          response = await providerAPI.getAvailableOrders()
          if (response.success && response.data) {
            this.order = response.data.find(o => o.id == orderId) || null
          }
        } else {
          // Customer: get order detail directly
          response = await customerAPI.getOrderDetail(orderId)
          if (response.success && response.data) {
            this.order = response.data
          }
        }
        
        // If API didn't return data, use default data
        if (!this.order) {
          const defaultOrders = [
            {
              id: 1,
              title: '家庭清洁服务',
              description: '需要对100平米的房屋进行深度清洁',
              service_type: 'cleaning_repair',
              price: 200.0,
              location: 'NORTH',
              address: '123 Main Street, Apt 5',
              service_start_time: '2025-10-25T09:00:00',
              service_end_time: '2025-10-25T12:00:00',
              status: 'pending',
              payment_status: 'pending'
            }
          ]
          
          this.order = defaultOrders.find(o => o.id == orderId) || null
        }
        
      } catch (error) {
        console.error('Error loading order:', error)
        // Use default data as fallback
        const defaultOrders = [
          {
            id: 1,
            title: '家庭清洁服务',
            description: '需要对100平米的房屋进行深度清洁',
            service_type: 'cleaning_repair',
            price: 200.0,
            location: 'NORTH',
            address: '123 Main Street, Apt 5',
            service_start_time: '2025-10-25T09:00:00',
            service_end_time: '2025-10-25T12:00:00',
            status: 'pending',
            payment_status: 'pending'
          }
        ]
        
        this.order = defaultOrders.find(o => o.id == orderId) || null
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.go(-1)
    },
    async acceptOrder() {
      if (!this.order) return
      
      try {
        this.applying = true
        
        // Call accept order API
        const response = await providerAPI.acceptOrder(this.order.id)
        
        console.log('Accept order response:', response)
        
        if (response.success) {
          alert('Order accepted successfully!')
          
          // Update order status
          this.order.status = 'accepted'
          
          // Optionally redirect to homepage or my tasks page
          this.$router.push('/?role=provider')
        } else {
          alert(response.message || 'Failed to accept order, please try again later')
        }
        
      } catch (error) {
        console.error('Error accepting order:', error)
        
        // Handle different error types
        if (error.status === 400) {
          alert('This order has been accepted by another provider or cannot be accepted')
        } else if (error.status === 401) {
          alert('Please login first')
          this.$router.push('/login')
        } else if (error.status === 403) {
          alert('You do not have permission to accept this order')
        } else if (error.status === 404) {
          alert('Order does not exist or has been deleted')
        } else {
          alert('Failed to accept order, please try again later')
        }
      } finally {
        this.applying = false
      }
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
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return ''
      const date = new Date(dateTimeString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    formatDate(dateTimeString) {
      if (!dateTimeString) return ''
      const date = new Date(dateTimeString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.order-detail-page {
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
  border-top: 4px solid #74b9ff;
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
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

.order-detail {
  max-width: 100%;
}

.order-header {
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
  color: #74b9ff;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: #74b9ff;
  color: white;
  border-color: #74b9ff;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.breadcrumb-link {
  color: #74b9ff;
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

.order-basic-info {
  margin-bottom: 30px;
}

.order-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 20px 0;
  line-height: 1.3;
}

.order-meta {
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
  color: #74b9ff;
  flex-shrink: 0;
}

.category {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
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

.order-details {
  margin-bottom: 30px;
}

.order-details h3 {
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

.action-buttons {
  margin-top: 40px;
  text-align: center;
}

.apply-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.3);
}

.apply-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(116, 185, 255, 0.4);
}

.apply-btn:active {
  transform: translateY(0);
}

.apply-btn.applying {
  opacity: 0.7;
  cursor: not-allowed;
}

.apply-btn.disabled {
  background: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
  box-shadow: none;
}

.apply-btn.disabled:hover {
  transform: none;
  box-shadow: none;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@media (max-width: 768px) {
  .main-content {
    padding: 15px;
  }
  
  .order-title {
    font-size: 24px;
  }
  
  .order-meta {
    flex-direction: column;
    gap: 15px;
  }
  
  .order-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>