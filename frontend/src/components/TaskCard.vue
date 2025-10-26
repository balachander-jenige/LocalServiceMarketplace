<template>
  <div class="task-card" :class="{ 'clickable': isClickable }" @click="handleCardClick">
    <div class="task-header">
      <h3 class="task-title">{{ task.title }}</h3>
      <span class="task-service-type">{{ getServiceTypeName(task.service_type) }}</span>
    </div>
    
    <div class="task-content">
      <div class="task-info">
        <div class="info-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ task.location }}</span>
        </div>
        
        <div v-if="task.address" class="info-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ task.address }}</span>
        </div>
        
        <div v-if="task.service_start_time" class="info-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
            <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
            <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
            <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span>{{ formatDate(task.service_start_time) }}</span>
        </div>
      </div>
    </div>
    
    <div class="task-footer">
      <div class="task-price">
        <span class="price-amount">S${{ task.price }}</span>
      </div>
      <div class="task-status" :class="getStatusClass(task.status)">
        {{ getStatusName(task.status) }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskCard',
  props: {
    task: {
      type: Object,
      required: true
    },
    clickable: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    isClickable() {
      return this.clickable
    }
  },
  methods: {
    handleCardClick() {
      if (this.isClickable) {
        this.$emit('card-click', this.task)
      }
    },
    getServiceTypeName(serviceType) {
      const typeMap = {
        'it_technology': 'IT Technology',
        'design_consulting': 'Design Consulting',
        'education_training': 'Education Training',
        'cleaning_repair': 'Cleaning Repair',
        'other': 'Other'
      }
      return typeMap[serviceType] || serviceType
    },
    getStatusName(status) {
      const statusMap = {
        'pending': 'Pending',
        'accepted': '已接单',
        'in_progress': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return statusMap[status] || status
    },
    getStatusClass(status) {
      const classMap = {
        'pending': 'status-pending',
        'accepted': 'status-accepted',
        'in_progress': 'status-in-progress',
        'completed': 'status-completed',
        'cancelled': 'status-cancelled'
      }
      return classMap[status] || 'status-default'
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
        month: '2-digit',
        day: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.task-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 24px;
  transition: all 0.3s ease;
  position: relative;
  border: 1px solid #f0f0f0;
  height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.task-card.clickable {
  cursor: pointer;
}

.task-card.clickable:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border-color: #74b9ff;
}


.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.task-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
  line-height: 1.3;
  flex: 1;
  margin-right: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-service-type {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.task-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 13px;
}

.info-item svg {
  color: #74b9ff;
  flex-shrink: 0;
}

.time-info {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 13px;
  margin-bottom: 4px;
}

.time-item:last-child {
  margin-bottom: 0;
}

.time-item svg {
  color: #00b894;
  flex-shrink: 0;
}

.time-label {
  font-weight: 500;
  color: #888;
}

.time-value {
  color: #333;
  font-weight: 500;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.task-price {
  display: flex;
  align-items: center;
}

.price-amount {
  color: #00b894;
  font-size: 18px;
  font-weight: 700;
}

.task-status {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 600;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-accepted {
  background: #d1ecf1;
  color: #0c5460;
}

.status-in-progress {
  background: #d4edda;
  color: #155724;
}

.status-completed {
  background: #d1ecf1;
  color: #0c5460;
}

.status-cancelled {
  background: #f8d7da;
  color: #721c24;
}

.status-default {
  background: #e2e3e5;
  color: #383d41;
}

.info-item span {
  flex: 1;
  word-break: break-word;
}



@media (max-width: 768px) {
  .task-card {
    padding: 20px;
    height: 200px;
  }
  
  .task-title {
    font-size: 15px;
  }
  
  .task-service-type {
    font-size: 10px;
    padding: 4px 8px;
  }
  
  .price-amount {
    font-size: 16px;
  }
  
  .info-item {
    font-size: 12px;
  }
}
</style>
