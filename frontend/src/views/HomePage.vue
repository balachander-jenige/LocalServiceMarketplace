<template>
  <div class="home-page" :class="{ 'customer-theme': isCustomer }">
    <NavBar />
    
    <div class="main-content">
      <div class="tasks-section">
        <div class="section-header">
          <h2>{{ isCustomer ? 'My Tasks' : 'Available Tasks' }}</h2>
          <div class="header-actions">
            <div v-if="!isCustomer" class="sort-options">
              <select v-model="sortBy" @change="handleSort" class="sort-select">
                <option value="latest">Latest</option>
                <option value="price-high">Price: High to Low</option>
                <option value="price-low">Price: Low to High</option>
                <option value="deadline">Deadline</option>
              </select>
            </div>
            <button v-if="isCustomer" class="publish-btn" @click="publishTask">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Publish Task
            </button>
          </div>
        </div>
        
        <!-- Filter functionality - Only shown for Provider -->
        <div v-if="!isCustomer" class="filter-section">
          <div class="filter-header">
            <h3>Filter Options</h3>
            <button class="clear-filters-btn" @click="clearFilters" :disabled="!hasActiveFilters">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 6H5H21M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Clear Filters
            </button>
          </div>
          
          <div class="filter-form">
            <div class="filter-row">
              <div class="filter-group">
                <label>Location</label>
                <select v-model="filters.location" @change="applyFilters" class="filter-select">
                  <option value="">All Locations</option>
                  <option value="NORTH">North</option>
                  <option value="SOUTH">South</option>
                  <option value="EAST">East</option>
                  <option value="WEST">West</option>
                  <option value="MID">Central</option>
                </select>
              </div>
              
              <div class="filter-group">
                <label>Service Type</label>
                <select v-model="filters.service_type" @change="applyFilters" class="filter-select">
                  <option value="">All Types</option>
                  <option value="cleaning_repair">Cleaning & Repair</option>
                  <option value="it_technology">IT Technology</option>
                  <option value="education_training">Education & Training</option>
                  <option value="life_health">Life & Health</option>
                  <option value="design_consulting">Design & Consulting</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div class="filter-group">
                <label>Price Range</label>
                <div class="price-range">
                  <input 
                    type="number" 
                    v-model.number="filters.min_price" 
                    @input="applyFilters"
                    placeholder="Min Price"
                    class="price-input"
                    min="0"
                  />
                  <span class="price-separator">-</span>
                  <input 
                    type="number" 
                    v-model.number="filters.max_price" 
                    @input="applyFilters"
                    placeholder="Max Price"
                    class="price-input"
                    min="0"
                  />
                </div>
              </div>
            </div>
            
            <div class="filter-row">
              <div class="filter-group keyword-group">
                <label>Keyword Search</label>
                <div class="search-input-wrapper">
                  <input 
                    type="text" 
                    v-model="filters.keyword" 
                    @input="debouncedSearch"
                    placeholder="Search task titles or descriptions..."
                    class="search-input"
                  />
                  <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                    <path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
              
              <div class="filter-actions">
                <button class="apply-filters-btn" @click="applyFilters" :disabled="loading">
                  <svg v-if="loading" class="loading-spinner-small" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ loading ? 'Searching...' : 'Search' }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>Loading tasks...</p>
        </div>
        
        <div v-else-if="filteredTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 11H15M9 15H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H17C18.1046 3 19 3.89543 19 5V19C19 20.1046 18.1046 21 17 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>No Tasks</h3>
          <p>No tasks found matching your criteria. Please try adjusting your search conditions.</p>
        </div>
        
        <div v-else class="tasks-grid">
          <div v-for="task in paginatedTasks" :key="task.id" class="task-wrapper">
            <TaskCard 
              :task="task" 
              :clickable="!isCustomer"
              @card-click="handleTaskClick"
            />
            <div v-if="isCustomer" class="task-actions">
              <button class="action-btn delete-btn" @click="deleteTask(task)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 6H5H21M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Delete
              </button>
            </div>
          </div>
        </div>
        
        <Pagination
          :current-page="currentPage"
          :total-pages="totalPages"
          :total-items="filteredTasks.length"
          :items-per-page="itemsPerPage"
          @page-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import TaskCard from '@/components/TaskCard.vue'
import Pagination from '@/components/Pagination.vue'
import { providerAPI, customerAPI } from '@/api/auth.js'

export default {
  name: 'HomePage',
  components: {
    NavBar,
    TaskCard,
    Pagination
  },
  data() {
    return {
      loading: false,
      sortBy: 'latest',
      currentPage: 1,
      itemsPerPage: 9,
      tasks: [],
      // 筛选条件
      filters: {
        location: '',
        service_type: '',
        min_price: null,
        max_price: null,
        keyword: ''
      },
      // 防抖搜索定时器
      searchTimeout: null,
      // Default task data (for customer role)
      defaultTasks: [
        {
          id: 1,
          title: 'Website Development Project',
          description: 'Need to develop a responsive corporate website including homepage, product showcase, about us pages, requiring Vue.js framework.',
          service_type: 'it_technology',
          price: 15000,
          location: 'CENTRAL',
          address: 'Chaoyang District, Beijing',
          service_start_time: '2024-01-20T09:00:00Z',
          service_end_time: '2024-02-15T18:00:00Z',
          status: 'pending'
        },
        {
          id: 2,
          title: 'Brand Logo Design',
          description: 'Design a modern logo for an emerging tech company, requiring simplicity and elegance that fits the tech positioning.',
          service_type: 'design_consulting',
          price: 3000,
          location: 'EAST',
          address: 'Pudong New Area, Shanghai',
          service_start_time: '2024-01-15T09:00:00Z',
          service_end_time: '2024-01-30T18:00:00Z',
          status: 'pending'
        },
        {
          id: 3,
          title: 'Social Media Marketing Campaign',
          description: 'Responsible for daily operations and content creation on WeChat, Weibo, TikTok and other platforms to enhance brand awareness.',
          service_type: 'design_consulting',
          price: 8000,
          location: 'SOUTH',
          address: 'Tianhe District, Guangzhou',
          service_start_time: '2024-02-01T09:00:00Z',
          service_end_time: '2024-03-01T18:00:00Z',
          status: 'pending'
        },
        {
          id: 4,
          title: 'English Speaking Training',
          description: 'Provide one-on-one English speaking training for professionals to help improve business English communication skills.',
          service_type: 'education_training',
          price: 200,
          location: 'SOUTH',
          address: 'Nanshan District, Shenzhen',
          service_start_time: '2024-02-01T09:00:00Z',
          service_end_time: '2024-02-28T18:00:00Z',
          status: 'pending'
        },
        {
          id: 5,
          title: 'Home Cleaning Service',
          description: 'Weekly cleaning service for 3-bedroom apartment.',
          service_type: 'cleaning_repair',
          price: 800,
          location: 'NORTH',
          address: '456 Residential Avenue, North District',
          service_start_time: '2024-01-30T10:00:00Z',
          service_end_time: '2024-01-30T16:00:00Z',
          status: 'pending'
        },
        {
          id: 6,
          title: 'Mobile App Development',
          description: 'Develop a cross-platform mobile application for iOS and Android.',
          service_type: 'it_technology',
          price: 25000,
          location: 'WEST',
          address: '789 Tech Street, West District',
          service_start_time: '2024-02-10T09:00:00Z',
          service_end_time: '2024-04-10T18:00:00Z',
          status: 'pending'
        },
        {
          id: 7,
          title: 'Interior Design Consultation',
          description: 'Professional interior design for office space renovation.',
          service_type: 'design_consulting',
          price: 5000,
          location: 'CENTRAL',
          address: '123 Business Plaza, Central District',
          service_start_time: '2024-02-05T10:00:00Z',
          service_end_time: '2024-02-20T17:00:00Z',
          status: 'pending'
        },
        {
          id: 8,
          title: 'Data Analysis Project',
          description: 'Analyze customer data and provide insights for business decisions.',
          service_type: 'it_technology',
          price: 12000,
          location: 'EAST',
          address: '456 Data Center, East District',
          service_start_time: '2024-02-15T09:00:00Z',
          service_end_time: '2024-03-15T18:00:00Z',
          status: 'pending'
        },
        {
          id: 9,
          title: 'Photography Services',
          description: 'Professional photography for corporate events and product shoots.',
          service_type: 'design_consulting',
          price: 3000,
          location: 'SOUTH',
          address: '789 Creative Studio, South District',
          service_start_time: '2024-02-20T08:00:00Z',
          service_end_time: '2024-02-25T18:00:00Z',
          status: 'pending'
        }
      ]
    }
  },
  created() {
    this.loadTasks()
  },
  computed: {
    isCustomer() {
      // Prioritize logged-in user role information
      const currentUser = sessionStorage.getItem('currentUser')
      if (currentUser) {
        const user = JSON.parse(currentUser)
        return user.role === 'customer'
      }
      // If no logged-in user info, use route parameter
      return this.$route.query.role !== 'provider'
    },
    filteredTasks() {
      let filtered = this.tasks.filter(task => {
        // Filter based on user role and task status
        const matchesStatus = this.isCustomer ? 
          task.status === 'pending' : // Customer only sees approved but unassigned tasks
          task.status === 'pending'   // Provider also only sees unassigned tasks
        
        return matchesStatus
      })
      
      // Sort
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'price-high':
            return b.price - a.price
          case 'price-low':
            return a.price - b.price
          case 'deadline':
            return new Date(a.service_end_time) - new Date(b.service_end_time)
          case 'latest':
          default:
            return b.id - a.id
        }
      })
      
      return filtered
    },
    totalPages() {
      return Math.ceil(this.filteredTasks.length / this.itemsPerPage)
    },
    paginatedTasks() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredTasks.slice(start, end)
    },
    // 检查是否有活跃的筛选条件
    hasActiveFilters() {
      return this.filters.location || 
             this.filters.service_type || 
             this.filters.min_price !== null || 
             this.filters.max_price !== null || 
             this.filters.keyword.trim()
    }
  },
  methods: {
    async loadTasks() {
      this.loading = true
      try {
        if (this.isCustomer) {
          // Customer role gets historical orders from API, then filters unassigned orders
          const response = await customerAPI.getHistoryOrders()
          if (response.success && response.data) {
            // Filter orders with pending status (unassigned)
            this.tasks = response.data.filter(order => order.status === 'pending')
          } else {
            console.error('Failed to load customer orders:', response.message)
            this.tasks = []
          }
        } else {
          // Provider role gets available tasks from API with filters
          const response = await providerAPI.getAvailableOrders(this.filters)
          if (response.success && response.data) {
            this.tasks = response.data
          } else {
            console.error('Failed to load available orders:', response.message)
            this.tasks = []
          }
        }
      } catch (error) {
        console.error('Error loading tasks:', error)
        this.tasks = []
        alert('Failed to load tasks, please try again later')
      } finally {
        this.loading = false
      }
    },
    handleSort() {
      this.currentPage = 1
    },
    handlePageChange(page) {
      this.currentPage = page
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    publishTask() {
      // Get current user role
      const role = this.getCurrentRole()
      this.$router.push(`/publish-task?role=${role}`)
    },
    async deleteTask(task) {
      if (confirm(`Are you sure you want to cancel order "${task.title}"?`)) {
        try {
          const response = await customerAPI.cancelOrder(task.id)
          if (response.success) {
            alert('Order cancelled successfully')
            // Reload task list
            await this.loadTasks()
          } else {
            alert('Failed to cancel order: ' + (response.message || 'Unknown error'))
          }
        } catch (error) {
          console.error('Error canceling order:', error)
          alert('Failed to cancel order, please try again later')
        }
      }
    },
    getCurrentRole() {
      // Prioritize logged-in user role information
      const currentUser = sessionStorage.getItem('currentUser')
      if (currentUser) {
        const user = JSON.parse(currentUser)
        return user.role
      }
      // If no logged-in user info, use route parameter，默认为customer
      return this.$route.query.role || 'customer'
    },
    handleTaskClick(task) {
      // 跳转到订单详情页面，传递role参数
      this.$router.push({
        name: 'OrderDetail',
        params: { id: task.id },
        query: { role: this.isCustomer ? 'customer' : 'provider' }
      })
    },
    // 应用筛选条件
    async applyFilters() {
      if (this.isCustomer) return // Customer不需要筛选功能
      
      this.currentPage = 1 // 重置到第一页
      await this.loadTasks()
    },
    // 清除所有筛选条件
    async clearFilters() {
      this.filters = {
        location: '',
        service_type: '',
        min_price: null,
        max_price: null,
        keyword: ''
      }
      this.currentPage = 1
      await this.loadTasks()
    },
    // 防抖搜索
    debouncedSearch() {
      // 清除之前的定时器
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout)
      }
      
      // 设置新的定时器，500ms后执行搜索
      this.searchTimeout = setTimeout(() => {
        this.applyFilters()
      }, 500)
    }
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  min-height: calc(100vh - 60px);
}

.tasks-section {
  padding: 0 20px 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-top: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sort-select {
  padding: 8px 12px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
}

.sort-select:focus {
  border-color: #74b9ff;
  box-shadow: 0 0 0 2px rgba(116, 185, 255, 0.1);
}

.publish-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.publish-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

/* Customer theme colors */
.customer-theme .publish-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .publish-btn:hover {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

/* 筛选功能样式 */
.filter-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid #e9ecef;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.clear-filters-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fff;
  color: #6c757d;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-filters-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #adb5bd;
  color: #495057;
}

.clear-filters-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.filter-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 15px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #495057;
}

.filter-select {
  padding: 10px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #495057;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
}

.filter-select:focus {
  border-color: #74b9ff;
  box-shadow: 0 0 0 2px rgba(116, 185, 255, 0.1);
}

.price-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #495057;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.price-input:focus {
  border-color: #74b9ff;
  box-shadow: 0 0 0 2px rgba(116, 185, 255, 0.1);
}

.price-separator {
  color: #6c757d;
  font-weight: 500;
}

.keyword-group {
  grid-column: span 2;
}

.search-input-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #495057;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: #74b9ff;
  box-shadow: 0 0 0 2px rgba(116, 185, 255, 0.1);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  pointer-events: none;
}

.filter-actions {
  display: flex;
  align-items: end;
}

.apply-filters-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
  justify-content: center;
}

.apply-filters-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

.apply-filters-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner-small {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.task-wrapper {
  position: relative;
}

.task-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.task-wrapper:hover .task-actions {
  opacity: 1;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}


.delete-btn {
  background: #ffebee;
  color: #d32f2f;
}

.delete-btn:hover {
  background: #ffcdd2;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 30px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  color: #74b9ff;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 20px;
  color: #666;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #999;
  font-size: 14px;
  margin: 0;
}

@media (max-width: 1200px) {
  .tasks-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .tasks-section {
    padding: 0 15px 15px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
    margin-bottom: 20px;
  }
  
  .section-header h2 {
    font-size: 20px;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .sort-select {
    width: 100%;
  }
  
  /* 筛选功能响应式设计 */
  .filter-section {
    padding: 15px;
    margin-bottom: 20px;
  }
  
  .filter-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .filter-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .keyword-group {
    grid-column: span 1;
  }
  
  .filter-actions {
    justify-content: stretch;
  }
  
  .apply-filters-btn {
    width: 100%;
  }
}
</style>
