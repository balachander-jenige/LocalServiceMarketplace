<template>
  <div class="provider-task-detail-page">
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
        <router-link to="/?role=provider" class="back-btn">Return to Homepage</router-link>
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
            <router-link to="/?role=provider" class="breadcrumb-link">Find Tasks</router-link>
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
            <div v-if="task.address" class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="address">{{ task.address }}</span>
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


        <!-- Accept task button -->
        <div class="action-buttons">
          <button 
            class="apply-btn" 
            :class="{ 'applying': applying, 'disabled': task.status !== 'pending' }"
            :disabled="applying || task.status !== 'pending'"
            @click="applyTask"
          >
            <div v-if="applying" class="loading-spinner-small"></div>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ applying ? 'Accepting...' : (task.status === 'pending' ? 'Accept Task' : 'Task Accepted') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import { providerAPI } from '@/api/auth.js'

export default {
  name: 'ProviderTaskDetail',
  components: {
    NavBar
  },
  data() {
    return {
      loading: true,
      task: null,
      applying: false
    }
  },
  created() {
    this.loadTask()
  },
  methods: {
    async loadTask() {
      const taskId = this.$route.params.id
      
      try {
        this.loading = true
        
        // Try to get task details from API
        const response = await providerAPI.getAvailableOrders()
        if (response.success && response.data) {
          this.task = response.data.find(t => t.id == taskId) || null
        }
        
        // 如果API没有返回数据，使用默认数据
        if (!this.task) {
          const defaultTasks = [
            {
              id: 1,
              title: 'Website Frontend Development Project',
              service_type: 'it_technology',
              location: 'CENTRAL',
              address: 'Chaoyang District, Beijing',
              service_start_time: '2024-01-15T09:00:00Z',
              service_end_time: '2024-01-20T18:00:00Z',
              price: 15000,
              description: 'Need to develop a responsive corporate website including homepage, product showcase, about us pages, requiring Vue.js framework. Project duration is expected to be 2 months, need to work closely with backend team.',
              requirements: [
                'Proficient in Vue.js framework',
                'Experience in responsive design',
                'Familiar with HTML5, CSS3, JavaScript',
                'Experience in corporate website development',
                'Able to deliver projects on time'
              ],
              customer_id: 'CUST_2024_001',
              customer_phone: '138-0000-1234',
              status: 'pending'
            },
            {
              id: 2,
              title: 'Brand Logo Design',
              service_type: 'design_consulting',
              location: 'EAST',
              address: 'Pudong New Area, Shanghai',
              service_start_time: '2024-01-15T09:00:00Z',
              service_end_time: '2024-01-30T18:00:00Z',
              price: 3000,
              description: 'Design a modern logo for an emerging tech company, requiring simplicity and elegance that fits the tech positioning.',
              requirements: [
                'Proficient in Adobe Illustrator',
                'Experience in brand design',
                'Creative thinking and design skills',
                'Able to deliver multiple design options'
              ],
              customer_id: 'CUST_2024_002',
              customer_phone: '138-0000-1235',
              status: 'pending'
            }
          ]
          
          this.task = defaultTasks.find(t => t.id == taskId) || null
        }
        
      } catch (error) {
        console.error('Error loading task:', error)
        // 使用默认数据作为fallback
        const defaultTasks = [
          {
            id: 1,
            title: 'Website Frontend Development Project',
            service_type: 'it_technology',
            location: 'CENTRAL',
            address: 'Chaoyang District, Beijing',
            service_start_time: '2024-01-15T09:00:00Z',
            service_end_time: '2024-01-20T18:00:00Z',
            price: 15000,
            description: 'Need to develop a responsive corporate website including homepage, product showcase, about us pages, requiring Vue.js framework. Project duration is expected to be 2 months, need to work closely with backend team.',
            requirements: [
              'Proficient in Vue.js framework',
              'Experience in responsive design',
              'Familiar with HTML5, CSS3, JavaScript',
              'Experience in corporate website development',
              'Able to deliver projects on time'
            ],
            customer_id: 'CUST_2024_001',
            customer_phone: '138-0000-1234',
            status: 'pending'
          }
        ]
        
        this.task = defaultTasks.find(t => t.id == taskId) || null
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.go(-1)
    },
    async applyTask() {
      if (!this.task) return
      
      try {
        this.applying = true
        
        // 调用接取任务的API
        const response = await providerAPI.acceptOrder(this.task.id)
        
        console.log('接取任务响应:', response)
        
        if (response.success) {
          alert('任务接取成功！')
          
          // 更新任务状态
          this.task.status = 'accepted'
          
          // 可以选择跳转回首页或我的任务页面
          this.$router.push('/?role=provider')
        } else {
          alert(response.message || '接取任务失败，请稍后重试')
        }
        
      } catch (error) {
        console.error('Error applying for task:', error)
        
        // 如果是网络错误或API错误，显示相应信息
        if (error.status === 400) {
          alert('该任务已被其他服务商接取或无法接取')
        } else if (error.status === 401) {
          alert('请先登录')
          this.$router.push('/login')
        } else if (error.status === 403) {
          alert('您没有权限接取此任务')
        } else if (error.status === 404) {
          alert('任务不存在或已被删除')
        } else {
          alert('接取任务失败，请稍后重试')
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
.provider-task-detail-page {
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

.task-details {
  margin-bottom: 30px;
}

.task-details h3 {
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
  
}
</style>
