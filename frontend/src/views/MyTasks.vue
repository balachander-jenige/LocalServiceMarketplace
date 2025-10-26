<template>
  <div class="my-tasks-page" :class="{ 'customer-theme': isCustomer }">
    <NavBar />
    
    <div class="main-content">
      <div class="page-header">
        <h1>My Tasks</h1>
        <p>{{ isCustomer ? 'Manage your published task progress' : 'Manage your ongoing and completed tasks' }}</p>
        <div v-if="loading" class="loading-indicator">
          <div class="spinner"></div>
          <span>Loading task data...</span>
        </div>
      </div>

      <!-- Pending Review Tasks (Customer only) -->
      <div v-if="isCustomer" class="section">
        <div class="section-header">
          <h2>Pending Review</h2>
          <span class="task-count">{{ pendingReviewTasks.length }} tasks</span>
        </div>
        
        <div v-if="pendingReviewTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12H15M9 16H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L19.7071 9.70711C19.8946 9.89464 20 10.149 20 10.4142V19C20 20.1046 19.1046 21 18 21H17Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>No Tasks Pending Review</h3>
          <p>All your published tasks have been reviewed</p>
          <router-link to="/publish-task" class="browse-btn">Publish New Task</router-link>
        </div>
        
        <div v-else class="task-list">
          <div v-for="task in pendingReviewTasks" :key="task.id" class="task-card pending-review">
            <div class="task-info">
              <h3 class="task-name">{{ task.title }}</h3>
              <div class="task-meta">
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <span>{{ formatDate(task.createdAt) }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.location }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.service_type }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2V22M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>S${{ task.price }}</span>
                </div>
                <div class="meta-item status">
                  <span :class="['status-badge', task.status]">{{ getStatusText(task.status) }}</span>
                </div>
              </div>
              <div v-if="task.description" class="task-description" @click="toggleTaskDescription(task.id)">
                <p :class="{ 'description-expanded': expandedTasks[task.id] }">
                  {{ task.description }}
                </p>
                <div v-if="needsExpansion(task.description)" class="expand-indicator">
                  <span v-if="!expandedTasks[task.id]">... Click to expand</span>
                  <span v-else>Click to collapse</span>
                </div>
              </div>
            </div>
            <div class="task-actions">
              <button class="action-btn cancel-btn" @click="cancelTask(task.id)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
                  <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
                </svg>
                Cancel Order
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Accepted Tasks (Provider only) -->
      <div v-if="!isCustomer" class="section">
        <div class="section-header">
          <h2>Accepted Tasks</h2>
          <span class="task-count">{{ acceptedTasks.length }} tasks</span>
        </div>
        
        <div v-if="acceptedTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>No Accepted Tasks</h3>
          <p>You haven't accepted any tasks yet</p>
          <router-link to="/" class="browse-btn">Browse Tasks</router-link>
        </div>
        
        <div v-else class="task-list">
          <div v-for="task in acceptedTasks" :key="task.id" class="task-card accepted">
            <div class="task-info">
              <h3 class="task-name">{{ task.title || task.name }}</h3>
              <div class="task-meta">
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <span>{{ formatDate(task.createdAt) || task.date }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.location }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.service_type || 'General Service' }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2V22M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>S${{ task.price || 'N/A' }}</span>
                </div>
                <div class="meta-item status">
                  <span :class="['status-badge', task.status]">{{ getStatusText(task.status) }}</span>
                </div>
              </div>
              <div v-if="task.description" class="task-description" @click="toggleTaskDescription(task.id)">
                <p :class="{ 'description-expanded': expandedTasks[task.id] }">
                  {{ task.description }}
                </p>
                <div v-if="needsExpansion(task.description)" class="expand-indicator">
                  <span v-if="!expandedTasks[task.id]">... Click to expand</span>
                  <span v-else>Click to collapse</span>
                </div>
              </div>
            </div>
            <div class="task-actions">
              <button class="action-btn start-btn" @click="startTask(task.id)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <polygon points="5,3 19,12 5,21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Start Task
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tasks in Progress -->
      <div class="section">
        <div class="section-header">
          <h2>Tasks in Progress</h2>
          <span class="task-count">{{ inProgressTasks.length }} tasks</span>
        </div>
        
        <div v-if="inProgressTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 11H15M9 15H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L19.7071 9.70711C19.8946 9.89464 20 10.149 20 10.4142V19C20 20.1046 19.1046 21 18 21H17Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>No Tasks in Progress</h3>
          <p>You currently have no tasks in progress</p>
          <router-link to="/" class="browse-btn">Browse Tasks</router-link>
        </div>
        
        <div v-else class="task-list">
          <div v-for="task in inProgressTasks" :key="task.id" class="task-card in-progress">
            <div class="task-info">
              <h3 class="task-name">{{ task.title || task.name }}</h3>
              <div class="task-meta">
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <span>{{ formatDate(task.createdAt) || task.date }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.location }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.service_type || 'General Service' }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2V22M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>S${{ task.price || 'N/A' }}</span>
                </div>
                <div class="meta-item status">
                  <span :class="['status-badge', task.status]">{{ getStatusText(task.status) }}</span>
                </div>
              </div>
              <div v-if="task.description" class="task-description" @click="toggleTaskDescription(task.id)">
                <p :class="{ 'description-expanded': expandedTasks[task.id] }">
                  {{ task.description }}
                </p>
                <div v-if="needsExpansion(task.description)" class="expand-indicator">
                  <span v-if="!expandedTasks[task.id]">... Click to expand</span>
                  <span v-else>Click to collapse</span>
                </div>
              </div>
            </div>
            <div class="task-actions">
              <!-- Provider Actions -->
              <template v-if="!isCustomer">
                <button class="action-btn complete-btn" @click="completeTask(task.id)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  I'm Done
                </button>
              </template>
              
              <!-- Customer Actions -->
              <template v-else>
                <button class="action-btn cancel-btn" @click="cancelTask(task.id)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
                    <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  Cancel Order
                </button>
                <button v-if="task.status === 'completed'" class="action-btn confirm-btn" @click="confirmComplete(task.id)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Confirm Completion
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Payment Tasks (Customer only) -->
      <div v-if="isCustomer" class="section">
        <div class="section-header">
          <h2>Pending Payment</h2>
          <span class="task-count">{{ pendingPaymentTasks.length }} tasks</span>
        </div>
        
        <div v-if="pendingPaymentTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2V22M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>No Pending Payment Tasks</h3>
          <p>You have no completed tasks waiting for payment</p>
        </div>
        
        <div v-else class="task-list">
          <div v-for="task in pendingPaymentTasks" :key="task.id" class="task-card pending-payment">
            <div class="task-info">
              <h3 class="task-name">{{ task.title || task.name }}</h3>
              <div class="task-meta">
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <span>{{ formatDate(task.createdAt) || task.date }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.location }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.service_type || 'General Service' }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2V22M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>S${{ task.price || 'N/A' }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>Completed: {{ task.completedAt }}</span>
                </div>
                <div class="meta-item status">
                  <span class="status-badge completed">Completed</span>
                </div>
              </div>
              <div v-if="task.description" class="task-description" @click="toggleTaskDescription(task.id)">
                <p :class="{ 'description-expanded': expandedTasks[task.id] }">
                  {{ task.description }}
                </p>
                <div v-if="needsExpansion(task.description)" class="expand-indicator">
                  <span v-if="!expandedTasks[task.id]">... Click to expand</span>
                  <span v-else>Click to collapse</span>
                </div>
              </div>
            </div>
            <div class="task-actions">
              <button class="action-btn payment-btn" @click="processPayment(task.id)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2V22M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Go to Payment
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Historical Tasks -->
      <div class="section">
        <div class="section-header">
          <h2>Historical Tasks</h2>
          <span class="task-count">{{ historyTasks.length }} tasks</span>
        </div>
        
        <div v-if="historyTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>No Historical Tasks</h3>
          <p>You haven't completed any tasks yet</p>
        </div>
        
        <div v-else class="task-list">
          <div v-for="task in historyTasks" :key="task.id" class="task-card history">
            <div class="task-info">
              <h3 class="task-name">{{ task.title || task.name }}</h3>
              <div class="task-meta">
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <span>{{ formatDate(task.createdAt) || task.date }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.location }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.service_type || 'General Service' }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2V22M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>S${{ task.price || 'N/A' }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.status === 'cancelled' ? 'Cancelled: ' : (task.status === 'paid' ? 'Paid: ' : 'Completed: ') }}{{ task.status === 'paid' ? task.paidAt : task.completedAt }}</span>
                </div>
              </div>
              <div v-if="task.description" class="task-description" @click="toggleTaskDescription(task.id)">
                <p :class="{ 'description-expanded': expandedTasks[task.id] }">
                  {{ task.description }}
                </p>
                <div v-if="needsExpansion(task.description)" class="expand-indicator">
                  <span v-if="!expandedTasks[task.id]">... Click to expand</span>
                  <span v-else>Click to collapse</span>
                </div>
              </div>
            </div>
            <div class="task-actions">
              <!-- Review buttons for customer role -->
              <template v-if="isCustomer">
                <button 
                  v-if="(task.status === 'paid' || task.payment_status === 'paid') && !task.hasReview" 
                  class="action-btn review-btn" 
                  @click="openReviewModal(task)"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Create Review
                </button>
                <div v-else-if="(task.status === 'paid' || task.payment_status === 'paid') && task.hasReview" class="review-status">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Reviewed
                </div>
              </template>
              
              <!-- Provider Actions -->
              <template v-else>
                <!-- No actions for provider in historical tasks -->
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Review Modal -->
      <ReviewModal 
        :visible="showReviewModal"
        :task="selectedTask"
        @close="closeReviewModal"
        @review-submitted="handleReviewSubmitted"
        @success="handleSuccess"
        @error="handleError"
      />
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import ReviewModal from '@/components/ReviewModal.vue'
import { providerAPI, customerAPI } from '@/api/auth.js'

export default {
  name: 'MyTasks',
  components: {
    NavBar,
    ReviewModal
  },
  data() {
    return {
      showReviewModal: false,
      selectedTask: null,
      loading: false,
      expandedTasks: {}, // Track task description expansion status
      pendingReviewTasks: [
        {
          id: 6,
          title: 'Website Development Project',
          description: 'Need a professional website for my business with modern design and responsive layout.',
          service_type: 'IT & Technology',
          price: 5000,
          location: 'CENTRAL',
          address: '123 Business Street, Central District',
          createdAt: '2024-01-25T10:30:00Z',
          status: 'pending_review'
        },
        {
          id: 7,
          title: 'Home Cleaning Service',
          description: 'Weekly cleaning service for 3-bedroom apartment.',
          service_type: 'Cleaning & Repair',
          price: 800,
          location: 'NORTH',
          address: '456 Residential Avenue, North District',
          createdAt: '2024-01-24T14:20:00Z',
          status: 'pending_review'
        }
      ],
      acceptedTasks: [
        {
          id: 2,
          title: 'Mobile App UI Design',
          name: 'Mobile App UI Design',
          description: 'Design modern and intuitive UI/UX for mobile application targeting young professionals.',
          service_type: 'Design & Creative',
          price: 5000,
          date: '2024-01-20',
          createdAt: '2024-01-20T14:30:00Z',
          location: 'Pudong New Area, Shanghai',
          status: 'accepted'
        },
        {
          id: 8,
          title: 'Logo Design Project',
          name: 'Logo Design Project',
          description: 'Create a modern and memorable logo design for a tech startup company.',
          service_type: 'Design & Creative',
          price: 2000,
          date: '2024-01-22',
          createdAt: '2024-01-22T11:00:00Z',
          location: 'Haidian District, Beijing',
          status: 'accepted'
        }
      ],
      inProgressTasks: [
        {
          id: 1,
          title: 'Website Frontend Development Project',
          name: 'Website Frontend Development Project',
          description: 'Develop a responsive frontend for e-commerce website using Vue.js and modern CSS frameworks.',
          service_type: 'IT & Technology',
          price: 8000,
          date: '2024-01-15',
          createdAt: '2024-01-15T09:00:00Z',
          location: 'Chaoyang District, Beijing',
          status: 'in_progress'
        },
        {
          id: 9,
          title: 'Mobile App Development',
          name: 'Mobile App Development',
          description: 'Develop a cross-platform mobile application using React Native.',
          service_type: 'IT & Technology',
          price: 15000,
          date: '2024-01-18',
          createdAt: '2024-01-18T14:00:00Z',
          location: 'Pudong New Area, Shanghai',
          status: 'in_progress'
        },
        {
          id: 10,
          title: 'UI/UX Design Project',
          name: 'UI/UX Design Project',
          description: 'Create modern UI/UX designs for a fintech application.',
          service_type: 'Design & Creative',
          price: 6000,
          date: '2024-01-20',
          createdAt: '2024-01-20T10:30:00Z',
          location: 'Haidian District, Beijing',
          status: 'in_progress'
        }
      ],
      pendingPaymentTasks: [
        {
          id: 11,
          title: 'Website Maintenance Project',
          name: 'Website Maintenance Project',
          description: 'Regular maintenance and updates for corporate website including security patches and content updates.',
          service_type: 'IT & Technology',
          price: 3000,
          date: '2024-01-25',
          createdAt: '2024-01-25T08:00:00Z',
          location: 'Xuhui District, Shanghai',
          completedAt: '2024-01-26 16:30',
          status: 'completed',
          payment_status: 'unpaid'
        },
        {
          id: 12,
          title: 'Mobile App UI Design',
          name: 'Mobile App UI Design',
          description: 'Design modern and intuitive UI/UX for mobile application targeting young professionals.',
          service_type: 'Design & Creative',
          price: 5000,
          date: '2024-01-20',
          createdAt: '2024-01-20T14:30:00Z',
          location: 'Pudong New Area, Shanghai',
          completedAt: '2024-01-22 18:00',
          status: 'completed',
          payment_status: 'unpaid'
        }
      ],
      historyTasks: [
        {
          id: 3,
          title: 'Corporate Website Redesign',
          name: 'Corporate Website Redesign',
          description: 'Complete redesign of corporate website with modern UI/UX and responsive design for better user experience.',
          service_type: 'IT & Technology',
          price: 12000,
          date: '2024-01-10',
          createdAt: '2024-01-10T10:00:00Z',
          location: 'Nanshan District, Shenzhen',
          completedAt: '2024-01-12 18:30',
          status: 'paid',
          paidAt: '2024-01-12 19:00',
          hasReview: false
        },
        {
          id: 4,
          title: 'E-commerce Platform Development',
          name: 'E-commerce Platform Development',
          description: 'Develop a full-stack e-commerce platform with payment integration and inventory management system.',
          service_type: 'IT & Technology',
          price: 25000,
          date: '2024-01-05',
          createdAt: '2024-01-05T09:30:00Z',
          location: 'Tianhe District, Guangzhou',
          completedAt: '2024-01-08 16:45',
          status: 'paid',
          paidAt: '2024-01-08 17:00',
          hasReview: true
        },
        {
          id: 5,
          title: 'Data Analysis Report',
          name: 'Data Analysis Report',
          description: 'Comprehensive data analysis and visualization report for business intelligence and decision making.',
          service_type: 'IT & Technology',
          price: 8000,
          date: '2024-01-01',
          createdAt: '2024-01-01T14:00:00Z',
          location: 'Xihu District, Hangzhou',
          completedAt: '2024-01-03 14:20',
          status: 'paid',
          paidAt: '2024-01-03 15:00',
          hasReview: false
        }
      ]
    }
  },
  computed: {
    isCustomer() {
      return this.$route.query.role === 'customer'
    }
  },
  async mounted() {
    // Load corresponding historical order data based on role
    if (this.isCustomer) {
      await this.loadCustomerOrders()
    } else {
      await this.loadProviderOrders()
    }
  },
  methods: {
    // Load Customer order data
    async loadCustomerOrders() {
      try {
        this.loading = true
        console.log('Starting to load Customer orders...')
        
        // Get current ongoing orders
        const currentResponse = await customerAPI.getCurrentOrders()
        console.log('Customer current orders response:', currentResponse)
        
        // Get historical orders
        const historyResponse = await customerAPI.getHistoryOrders()
        console.log('Customer historical orders response:', historyResponse)
        
        // Clear existing data
        this.pendingReviewTasks = []
        this.inProgressTasks = []
        this.pendingPaymentTasks = []
        this.historyTasks = []
        
        // Process current ongoing orders
        if (currentResponse.success && currentResponse.data) {
          currentResponse.data.forEach(order => {
            const taskData = this.transformOrderToTask(order)
            
            switch (order.status) {
              case 'pending_review':
              case 'pending':
                this.pendingReviewTasks.push(taskData)
                break
              case 'accepted':
              case 'in_progress':
                this.inProgressTasks.push(taskData)
                break
              case 'completed':
                // Check payment status
                if (order.payment_status === 'paid') {
                  this.historyTasks.push(taskData)
                } else {
                  this.pendingPaymentTasks.push(taskData)
                }
                break
              case 'cancelled':
              case 'paid':
                // Only put cancelled and paid orders into historical tasks
                this.historyTasks.push(taskData)
                break
              default:
                // Other status tasks are not put into historical tasks
                break
            }
          })
        }
        
        // Process historical orders
        if (historyResponse.success && historyResponse.data) {
          historyResponse.data.forEach(order => {
            const taskData = this.transformOrderToTask(order)
            
            switch (order.status) {
              case 'completed':
                // Check payment status
                if (order.payment_status === 'paid') {
                  this.historyTasks.push(taskData)
                } else {
                  this.pendingPaymentTasks.push(taskData)
                }
                break
              case 'cancelled':
              case 'paid':
                // Only put cancelled and paid orders into historical tasks
                this.historyTasks.push(taskData)
                break
              default:
                // Other status tasks are not put into historical tasks
                break
            }
          })
        }
        
        console.log('Customer task categorization completed:', {
          pendingReview: this.pendingReviewTasks.length,
          inProgress: this.inProgressTasks.length,
          pendingPayment: this.pendingPaymentTasks.length,
          history: this.historyTasks.length
        })
      } catch (error) {
        console.error('Failed to load Customer orders:', error)
        alert('Failed to load task data: ' + (error.message || 'Unknown error'))
      } finally {
        this.loading = false
      }
    },

    // Load Provider historical order data
    async loadProviderOrders() {
      try {
        this.loading = true
        console.log('Starting to load Provider historical orders...')
        
        const response = await providerAPI.getHistoryOrders()
        console.log('Provider historical orders response:', response)
        
        if (response.success && response.data) {
          // Clear existing data
          this.acceptedTasks = []
          this.inProgressTasks = []
          this.historyTasks = []
          
          // Categorize tasks based on order status
          response.data.forEach(order => {
            const taskData = this.transformOrderToTask(order)
            
            switch (order.status) {
              case 'accepted':
                this.acceptedTasks.push(taskData)
                break
              case 'in_progress':
                this.inProgressTasks.push(taskData)
                break
              case 'completed':
              case 'cancelled':
              case 'paid':
                this.historyTasks.push(taskData)
                break
              default:
                // Other status tasks are put into historical tasks
                this.historyTasks.push(taskData)
                break
            }
          })
          
          console.log('Task categorization completed:', {
            accepted: this.acceptedTasks.length,
            inProgress: this.inProgressTasks.length,
            history: this.historyTasks.length
          })
        } else {
          console.warn('API response format abnormal:', response)
        }
      } catch (error) {
        console.error('Failed to load Provider historical orders:', error)
        alert('Failed to load task data: ' + (error.message || 'Unknown error'))
      } finally {
        this.loading = false
      }
    },
    
    // Convert API order data to task format needed by component
    transformOrderToTask(order) {
      return {
        id: order.id,
        title: order.title,
        name: order.title,
        description: order.description,
        service_type: order.service_type,
        price: order.price,
        location: order.location,
        address: order.address,
        createdAt: order.created_at,
        updatedAt: order.updated_at,
        status: order.status,
        payment_status: order.payment_status,
        service_start_time: order.service_start_time,
        service_end_time: order.service_end_time,
        customer_id: order.customer_id,
        provider_id: order.provider_id,
        // Add some extra fields for compatibility with existing UI
        date: order.created_at ? new Date(order.created_at).toLocaleDateString() : '',
        completedAt: order.status === 'completed' || order.status === 'paid' ? 
          (order.service_end_time || order.updated_at) : null,
        paidAt: order.payment_status === 'paid' ? order.updated_at : null,
        // Check if there is review info, default to false if not
        hasReview: order.has_review || order.review_id || false
      }
    },
    
    getStatusText(status) {
      const statusMap = {
        'pending_review': 'Pending Review',
        'pending': 'Pending',
        'accepted': 'Accepted',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'paid': 'Paid'
      }
      return statusMap[status] || status || 'Unknown'
    },
    async cancelTask(taskId) {
      if (confirm('Are you sure you want to cancel this order?')) {
        try {
          if (this.isCustomer) {
            // Customer cancels order
            const response = await customerAPI.cancelOrder(taskId)
            console.log('Cancel order response:', response)
            
            if (response.success) {
              alert('Order cancelled successfully!')
              // Reload data
              await this.loadCustomerOrders()
            } else {
              alert('Failed to cancel order: ' + (response.message || 'Unknown error'))
            }
          } else {
            // Provider cancels order (keep original logic for now)
            console.log('Cancel task ID:', taskId)
            await this.loadProviderOrders()
            alert('Task cancelled!')
          }
        } catch (error) {
          console.error('Failed to cancel task:', error)
          alert('取消任务失败: ' + (error.message || '未知错误'))
        }
      }
    },
    async startTask(taskId) {
      if (confirm('确定要开始这个任务吗？')) {
        try {
          if (this.isCustomer) {
            // 客户角色暂时不支持开始任务
            alert('客户角色不支持开始任务操作')
            return
          } else {
            // 服务商开始任务 - 调用API更新订单状态为进行中
            const response = await providerAPI.updateOrderStatus(taskId, 'in_progress')
            console.log('开始任务响应:', response)
            
            if (response.success) {
              alert('任务已开始！')
              // Reload data
              await this.loadProviderOrders()
            } else {
              // 提取错误信息
              const errorMessage = response.message || response.error || response.detail || '未知错误'
              alert('开始任务失败: ' + errorMessage)
            }
          }
        } catch (error) {
          console.error('开始任务失败:', error)
          console.log('错误对象详情:', {
            message: error.message,
            data: error.data,
            status: error.status,
            type: typeof error.message
          })
          
          // 提取错误信息，处理各种可能的错误格式
          let errorMessage = '未知错误'
          
          // 检查error.message是否是对象
          if (error.message && typeof error.message === 'object') {
            errorMessage = JSON.stringify(error.message)
          } else if (error.message && typeof error.message === 'string') {
            errorMessage = error.message
          } else if (error.data) {
            if (typeof error.data === 'object') {
              errorMessage = error.data.message || error.data.error || error.data.detail || JSON.stringify(error.data)
            } else {
              errorMessage = error.data
            }
          } else if (typeof error === 'string') {
            errorMessage = error
          }
          
          console.log('提取的错误信息:', errorMessage)
          alert('开始任务失败: ' + errorMessage)
        }
      }
    },
    async completeTask(taskId) {
      if (confirm('确定要标记这个任务为已完成吗？')) {
        try {
          if (this.isCustomer) {
            // 客户角色不支持完成任务操作
            alert('客户角色不支持完成任务操作')
            return
          } else {
            // 服务商完成任务 - 调用API更新订单状态为已完成
            const response = await providerAPI.updateOrderStatus(taskId, 'completed')
            console.log('完成任务响应:', response)
            
            if (response.success) {
              alert('任务已完成！等待客户付款。')
              // Reload data
              await this.loadProviderOrders()
            } else {
              // 提取错误信息
              const errorMessage = response.message || response.error || response.detail || '未知错误'
              alert('完成任务失败: ' + errorMessage)
            }
          }
        } catch (error) {
          console.error('完成任务失败:', error)
          console.log('错误对象详情:', {
            message: error.message,
            data: error.data,
            status: error.status,
            type: typeof error.message
          })
          
          // 提取错误信息，处理各种可能的错误格式
          let errorMessage = '未知错误'
          
          // 检查error.message是否是对象
          if (error.message && typeof error.message === 'object') {
            errorMessage = JSON.stringify(error.message)
          } else if (error.message && typeof error.message === 'string') {
            errorMessage = error.message
          } else if (error.data) {
            if (typeof error.data === 'object') {
              errorMessage = error.data.message || error.data.error || error.data.detail || JSON.stringify(error.data)
            } else {
              errorMessage = error.data
            }
          } else if (typeof error === 'string') {
            errorMessage = error
          }
          
          console.log('提取的错误信息:', errorMessage)
          alert('完成任务失败: ' + errorMessage)
        }
      }
    },
    confirmComplete(taskId) {
      if (confirm('Are you sure you want to confirm task completion?')) {
        const task = this.inProgressTasks.find(t => t.id === taskId)
        if (task) {
          task.status = 'confirmed'
          task.confirmedAt = new Date().toLocaleString('en-US')
          
          // Move to historical tasks
          this.historyTasks.unshift({
            id: task.id,
            name: task.name,
            date: task.date,
            location: task.location,
            completedAt: task.confirmedAt
          })
          
          // Remove from in-progress tasks
          const taskIndex = this.inProgressTasks.findIndex(t => t.id === taskId)
          if (taskIndex !== -1) {
            this.inProgressTasks.splice(taskIndex, 1)
          }
          
          alert('Task completion confirmed!')
        }
      }
    },
    async processPayment(taskId) {
      if (confirm('确定要支付这个订单吗？')) {
        try {
          // 调用支付API
          const response = await customerAPI.payOrder(taskId)
          console.log('支付订单响应:', response)
          
          if (response.success) {
            alert('支付成功！订单已完成。')
            // 重新加载数据
            await this.loadCustomerOrders()
          } else {
            // 提取错误信息
            const errorMessage = response.message || response.error || response.detail || '未知错误'
            alert('支付失败: ' + errorMessage)
          }
        } catch (error) {
          console.error('支付失败:', error)
          console.log('错误对象详情:', {
            message: error.message,
            data: error.data,
            status: error.status,
            type: typeof error.message
          })
          
          // 提取错误信息，处理各种可能的错误格式
          let errorMessage = '未知错误'
          
          // 检查error.message是否是对象
          if (error.message && typeof error.message === 'object') {
            errorMessage = JSON.stringify(error.message)
          } else if (error.message && typeof error.message === 'string') {
            errorMessage = error.message
          } else if (error.data) {
            if (typeof error.data === 'object') {
              errorMessage = error.data.message || error.data.error || error.data.detail || JSON.stringify(error.data)
            } else {
              errorMessage = error.data
            }
          } else if (typeof error === 'string') {
            errorMessage = error
          }
          
          console.log('提取的错误信息:', errorMessage)
          alert('支付失败: ' + errorMessage)
        }
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    editTask(taskId) {
      // Navigate to edit task page
      this.$router.push(`/publish-task?edit=true&id=${taskId}`)
    },
    async deleteTask(taskId) {
      if (confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
        try {
          // TODO: 这里应该调用删除任务的API
          // await customerAPI.deleteOrder(taskId)
          console.log('删除任务ID:', taskId)
          
          // 临时处理：重新加载数据
          await this.loadCustomerOrders()
          alert('Task deleted successfully')
        } catch (error) {
          console.error('删除任务失败:', error)
          alert('删除任务失败: ' + (error.message || '未知错误'))
        }
      }
    },
    // Review related methods
    openReviewModal(task) {
      this.selectedTask = task
      this.showReviewModal = true
    },
    closeReviewModal() {
      this.showReviewModal = false
      this.selectedTask = null
    },
    handleReviewSubmitted(reviewData) {
      // Update task status, mark as reviewed
      const task = this.historyTasks.find(t => t.id === reviewData.taskId)
      if (task) {
        task.hasReview = true
        task.reviewRating = reviewData.rating
        task.reviewComment = reviewData.comment
      }
    },
    handleSuccess(message) {
      alert(message)
    },
    handleError(message) {
      alert(message)
    },
    
    // 切换任务描述的展开状态
    toggleTaskDescription(taskId) {
      this.expandedTasks[taskId] = !this.expandedTasks[taskId]
    },
    
    // 检查任务描述是否需要展开功能
    needsExpansion(description) {
      if (!description) return false
      // 简单的判断：如果描述超过100个字符，认为需要展开功能
      return description.length > 100
    }
  }
}
</script>

<style scoped>
.my-tasks-page {
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
  margin-bottom: 40px;
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
  font-size: 16px;
  color: #666;
  margin: 0;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
  padding: 15px;
  background: rgba(116, 185, 255, 0.1);
  border-radius: 8px;
  color: #74b9ff;
  font-size: 14px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e3f2fd;
  border-top: 2px solid #74b9ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
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
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.task-count {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
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
  font-size: 20px;
  color: #666;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #999;
  font-size: 14px;
  margin: 0 0 20px 0;
}

.browse-btn {
  display: inline-block;
  padding: 10px 20px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.browse-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.task-card:hover {
  border-color: #74b9ff;
  box-shadow: 0 2px 8px rgba(116, 185, 255, 0.1);
}

.task-card.history {
  background: #f8f9fa;
  opacity: 0.8;
}

.task-card.in-progress {
  background: #f8f9fa;
  border-left: 4px solid #74b9ff;
}

.task-card.pending-review {
  background: #f8f9fa;
  border-left: 4px solid #ffeaa7;
}

.task-card.accepted {
  background: #f8f9fa;
  border-left: 4px solid #00b894;
}

.task-card.pending-payment {
  background: #f8f9fa;
  border-left: 4px solid #fdcb6e;
}

.task-info {
  flex: 1;
}

.task-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 10px 0;
}

.task-description {
  margin-top: 10px;
  padding: 10px;
  background: rgba(116, 185, 255, 0.05);
  border-radius: 6px;
  border-left: 3px solid #74b9ff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.task-description:hover {
  background: rgba(116, 185, 255, 0.1);
}

.task-description p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: all 0.3s ease;
}

.task-description p.description-expanded {
  display: block;
  -webkit-line-clamp: unset;
  overflow: visible;
}

.expand-indicator {
  margin-top: 8px;
  text-align: center;
  font-size: 12px;
  color: #74b9ff;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s ease;
}

.expand-indicator:hover {
  color: #0984e3;
}

.expand-indicator span {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(116, 185, 255, 0.1);
  border-radius: 4px;
  border: 1px solid rgba(116, 185, 255, 0.3);
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 14px;
}

.meta-item svg {
  color: #74b9ff;
  flex-shrink: 0;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.pending_review {
  background: #fff3cd;
  color: #856404;
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

.status-badge.pending-review {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.status-badge.accepted {
  background: #d1ecf1;
  color: #0c5460;
}

.status-badge.paid {
  background: #d4edda;
  color: #155724;
}

.task-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.cancel-btn:hover {
  background: #f5c6cb;
  color: #721c24;
}

.complete-btn {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
}

.complete-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(116, 185, 255, 0.3);
}

.confirm-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
}

.confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
}

.edit-btn {
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #bbdefb;
}

.edit-btn:hover {
  background: #bbdefb;
  color: #1976d2;
}

.start-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
}

.start-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
}

.payment-btn {
  background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
  color: white;
}

.payment-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(253, 203, 110, 0.3);
}

.review-btn {
  background: linear-gradient(135deg, #ffc107 0%, #ff8f00 100%);
  color: white;
}

.review-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
}

.review-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #e8f5e8;
  color: #2e7d32;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
}

.review-status svg {
  color: #ffc107;
}

/* Customer theme colors */
.customer-theme .task-count {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .browse-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .browse-btn:hover {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.customer-theme .meta-item svg {
  color: #00b894;
}

.customer-theme .complete-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .complete-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
}

.task-status {
  display: flex;
  align-items: center;
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
  
  .section {
    padding: 20px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .task-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .task-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .task-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>