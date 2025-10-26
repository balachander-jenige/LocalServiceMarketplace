<template>
  <div class="admin-page">
    <!-- Page Header -->
    <div class="page-header" v-if="showHeader">
      <div class="header-left">
        <h2>{{ title }}</h2>
        <p class="page-description" v-if="description">{{ description }}</p>
      </div>
      <div class="header-right" v-if="$slots.headerActions">
        <slot name="headerActions"></slot>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>{{ loadingText || 'Loading...' }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3>Something went wrong</h3>
      <p>{{ error }}</p>
      <button v-if="showRetry" @click="$emit('retry')" class="retry-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M1 4V10H7M23 20V14H17M20.49 9A9 9 0 0 0 5.64 5.64L1 10M23 14L18.36 18.36A9 9 0 0 1 3.51 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Try Again
      </button>
    </div>

    <!-- Empty State -->
    <div v-else-if="showEmpty" class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h3>{{ emptyTitle || 'No Data Available' }}</h3>
      <p>{{ emptyDescription || 'There is no data to display at the moment.' }}</p>
      <slot name="emptyActions"></slot>
    </div>

    <!-- Main Content -->
    <div v-else class="page-content">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminPage',
  props: {
    title: {
      type: String,
      default: ''
    },
    description: {
      type: String,
      default: ''
    },
    showHeader: {
      type: Boolean,
      default: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    loadingText: {
      type: String,
      default: ''
    },
    error: {
      type: String,
      default: ''
    },
    showRetry: {
      type: Boolean,
      default: true
    },
    showEmpty: {
      type: Boolean,
      default: false
    },
    emptyTitle: {
      type: String,
      default: ''
    },
    emptyDescription: {
      type: String,
      default: ''
    }
  },
  emits: ['retry']
}
</script>

<style scoped>
.admin-page {
  width: 100%;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.page-description {
  margin: 0;
  color: #64748b;
  font-size: 14px;
  line-height: 1.5;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* Loading State */
.loading-state {
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
  border: 3px solid #e2e8f0;
  border-top: 3px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

/* Error State */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.error-icon {
  color: #ef4444;
  margin-bottom: 24px;
}

.error-state h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.error-state p {
  margin: 0 0 24px 0;
  color: #64748b;
  font-size: 14px;
  line-height: 1.5;
  max-width: 400px;
}

.retry-btn {
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

.retry-btn:hover {
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  color: #cbd5e1;
  margin-bottom: 24px;
}

.empty-state h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.empty-state p {
  margin: 0 0 24px 0;
  color: #64748b;
  font-size: 14px;
  line-height: 1.5;
  max-width: 400px;
}

/* Page Content */
.page-content {
  width: 100%;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: flex-start;
  }
  
  .loading-state,
  .error-state,
  .empty-state {
    padding: 60px 16px;
  }
}

@media (max-width: 480px) {
  .page-header {
    margin-bottom: 24px;
    padding-bottom: 20px;
  }
  
  .header-left h2 {
    font-size: 20px;
  }
  
  .loading-state,
  .error-state,
  .empty-state {
    padding: 40px 12px;
  }
  
  .error-state h3,
  .empty-state h3 {
    font-size: 18px;
  }
}
</style>

