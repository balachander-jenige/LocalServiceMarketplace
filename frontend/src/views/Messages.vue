<template>
  <div class="messages-page" :class="{ 'customer-theme': $route.query.role === 'customer' }">
    <NavBar />
    
    <div class="main-content">
      <div class="page-header">
        <h1>My Messages</h1>
        <p>View system notifications and important messages</p>
      </div>

      <!-- Message List -->
      <div class="messages-section">
        <div class="section-header">
          <h2>System Messages</h2>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
              </circle>
            </svg>
          </div>
          <h3>Loading Messages...</h3>
          <p>Please wait while we fetch your messages</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-state">
          <div class="error-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
              <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <h3>Error Loading Messages</h3>
          <p>{{ error }}</p>
          <button @click="loadMessages" class="retry-btn">Retry</button>
        </div>

        <!-- Empty State -->
        <div v-else-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>No Messages</h3>
          <p>You currently have no messages</p>
        </div>

        <div v-else>
          <!-- Message List -->
          <div class="message-list">
            <div v-for="message in paginatedMessages" :key="message.id" class="message-card">
              <div class="message-content">
                <p>{{ message.content }}</p>
              </div>
              <div class="message-time">
                {{ formatTime(message.createdAt) }}
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="pagination">
            <div class="pagination-info">
              Showing {{ messageRange.start }}-{{ messageRange.end }} of {{ messages.length }} messages
            </div>
            <div class="pagination-controls">
              <button 
                class="page-btn prev-btn" 
                :disabled="currentPage === 1"
                @click="goToPreviousPage"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Previous
              </button>
              
              <div class="page-numbers">
                <button 
                  v-for="page in getVisiblePages()" 
                  :key="page"
                  :class="['page-btn', 'page-number', { active: page === currentPage }]"
                  @click="goToPage(page)"
                >
                  {{ page }}
                </button>
              </div>
              
              <button 
                class="page-btn next-btn" 
                :disabled="currentPage === totalPages"
                @click="goToNextPage"
              >
                Next
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import { customerAPI, providerAPI } from '@/api/auth.js'

export default {
  name: 'MessagesPage',
  components: {
    NavBar
  },
  data() {
    return {
      messages: [],
      loading: false,
      error: null,
      currentUser: null,
      currentPage: 1,
      pageSize: 10
    }
  },
  created() {
    console.log('Messages component created, starting to load messages')
    this.checkLoginStatus()
    this.loadMessages()
  },
  computed: {
    // Calculate total pages
    totalPages() {
      return Math.ceil(this.messages.length / this.pageSize)
    },
    // 计算当前页显示的消息
    paginatedMessages() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.messages.slice(start, end)
    },
    // 计算显示的消息范围
    messageRange() {
      const start = (this.currentPage - 1) * this.pageSize + 1
      const end = Math.min(this.currentPage * this.pageSize, this.messages.length)
      return { start, end }
    }
  },
  watch: {
    // 监听路由变化，避免重复加载
    '$route'(to, from) {
      if (to.path !== from.path) {
        console.log('路由变化，重新加载消息')
        this.currentPage = 1
        this.loadMessages()
      }
    }
  },
  methods: {
    // 检查登录状态
    checkLoginStatus() {
      const user = sessionStorage.getItem('currentUser')
      if (user) {
        this.currentUser = JSON.parse(user)
      } else {
        // 如果没有登录，跳转到登录页
        this.$router.push('/login')
      }
    },

    // 获取用户角色
    getUserRole() {
      if (this.currentUser) {
        return this.currentUser.role
      }
      // 如果没有登录用户信息，则使用路由参数，默认为customer
      return this.$route.query.role || 'customer'
    },

    // 加载消息数据
    async loadMessages() {
      console.log('开始加载消息，当前消息数量:', this.messages.length)
      
      if (!this.currentUser) {
        console.log('用户未登录，跳过加载消息')
        return
      }

      this.loading = true
      this.error = null

      try {
        const userRole = this.getUserRole()
        let response

        if (userRole === 'customer') {
          response = await customerAPI.getInbox()
        } else if (userRole === 'provider') {
          response = await providerAPI.getInbox()
        } else {
          throw new Error('Invalid user role')
        }

        if (response.success && response.data) {
          // 转换API数据格式为组件需要的格式，使用数组索引确保唯一性
          const rawMessages = response.data.items.map((item, index) => ({
            id: `msg_${index}_${item.customer_id || item.provider_id}_${item.order_id}_${item.created_at}`,
            content: item.message,
            createdAt: new Date(item.created_at)
          }))
          
          // 去重：基于消息内容和时间戳去重
          const uniqueMessages = rawMessages.filter((message, index, array) => {
            return array.findIndex(m => 
              m.content === message.content && 
              m.createdAt.getTime() === message.createdAt.getTime()
            ) === index
          })
          
          this.messages = uniqueMessages
          
          // 调试信息：检查是否有重复的消息
          console.log('原始API数据:', response.data.items)
          console.log('转换后的消息:', rawMessages)
          console.log('去重后的消息:', uniqueMessages)
          console.log('消息数量:', uniqueMessages.length)
        } else {
          throw new Error(response.message || 'Failed to load messages')
        }
      } catch (error) {
        console.error('加载消息失败:', error)
        this.error = error.message || 'Failed to load messages'
        // 如果API调用失败，显示空状态
        this.messages = []
      } finally {
        this.loading = false
      }
    },

    // 分页方法
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },

    goToPreviousPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },

    goToNextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    },

    getVisiblePages() {
      const pages = []
      const maxVisible = 5
      let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2))
      let end = Math.min(this.totalPages, start + maxVisible - 1)
      
      if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1)
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    },

    formatTime(date) {
      const now = new Date()
      const messageDate = new Date(date)
      const diffTime = now - messageDate
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return messageDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      } else if (diffDays === 1) {
        return 'Yesterday ' + messageDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      } else if (diffDays < 7) {
        return diffDays + ' days ago'
      } else {
        return messageDate.toLocaleDateString('en-US')
      }
    }
  }
}
</script>

<style scoped>
.messages-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 40px 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 10px 0;
}

.page-header p {
  font-size: 18px;
  color: #666;
  margin: 0;
}


.messages-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.section-header h2 {
  font-size: 26px;
  font-weight: 600;
  color: #333;
  margin: 0;
}


.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  color: #74b9ff;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 22px;
  color: #666;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #999;
  font-size: 16px;
  margin: 0;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  color: #74b9ff;
  margin-bottom: 20px;
}

.loading-state h3 {
  font-size: 22px;
  color: #666;
  margin: 0 0 10px 0;
}

.loading-state p {
  color: #999;
  font-size: 16px;
  margin: 0;
}

.error-state {
  text-align: center;
  padding: 60px 20px;
}

.error-icon {
  color: #ff6b6b;
  margin-bottom: 20px;
}

.error-state h3 {
  font-size: 22px;
  color: #666;
  margin: 0 0 10px 0;
}

.error-state p {
  color: #999;
  font-size: 16px;
  margin: 0 0 20px 0;
}

.retry-btn {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  transition: all 0.3s ease;
}

.message-card:hover {
  border-color: #74b9ff;
  box-shadow: 0 2px 8px rgba(116, 185, 255, 0.1);
}

.message-content {
  margin-bottom: 10px;
}

.message-content p {
  color: #666;
  line-height: 1.6;
  margin: 0;
  font-size: 16px;
}

.message-time {
  color: #999;
  font-size: 14px;
  text-align: right;
}

/* Customer theme colors */
.customer-theme .message-card:hover {
  border-color: #00b894;
  box-shadow: 0 2px 8px rgba(0, 184, 148, 0.1);
}

.customer-theme .loading-spinner {
  color: #00b894;
}

.customer-theme .retry-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .retry-btn:hover {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

/* Pagination Styles */
.pagination {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-info {
  color: #666;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid #e9ecef;
  background: white;
  color: #666;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  border-color: #74b9ff;
  color: #74b9ff;
  background: #f8f9fa;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 5px;
}

.page-number {
  min-width: 36px;
  justify-content: center;
}

.page-number.active {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border-color: transparent;
}

.page-number.active:hover {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
}

/* Customer theme pagination */
.customer-theme .page-btn:hover:not(:disabled) {
  border-color: #00b894;
  color: #00b894;
}

.customer-theme .page-number.active {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .page-number.active:hover {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

@media (max-width: 768px) {
  .main-content {
    padding: 15px;
  }
  
  .page-header {
    padding: 30px 20px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .messages-section {
    padding: 20px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 15px;
    align-items: center;
  }
  
  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .page-numbers {
    order: 2;
  }
  
  .prev-btn {
    order: 1;
  }
  
  .next-btn {
    order: 3;
  }
}
</style>