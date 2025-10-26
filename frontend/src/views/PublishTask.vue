<template>
  <div class="publish-task-page" :class="{ 'customer-theme': true }">
    <NavBar />
    
    <div class="main-content">
      <div class="page-header">
        <h1>{{ isEditMode ? 'Edit Task' : 'Publish Task' }}</h1>
        <p>{{ isEditMode ? 'Modify task information and update your requirements' : 'Fill in task information and publish your requirements' }}</p>
      </div>

      <div class="form-container">
        <form @submit.prevent="publishTask" class="task-form">
          <div class="form-section">
            <h3>Basic Information</h3>
            <div class="form-group">
              <label for="title">Task Title *</label>
              <input 
                type="text" 
                id="title" 
                v-model="form.title" 
                required
                placeholder="Please enter task title"
                maxlength="100"
              >
              <span class="char-count">{{ form.title.length }}/100</span>
            </div>
            
            <div class="form-group">
              <label for="description">Task Description</label>
              <textarea 
                id="description" 
                v-model="form.description" 
                placeholder="Please describe your task requirements in detail..."
                rows="4"
                maxlength="1000"
              ></textarea>
              <span class="char-count">{{ form.description.length }}/1000</span>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="service_type">Service Type *</label>
                <select id="service_type" v-model="form.service_type" required>
                  <option value="">Please select service type</option>
                  <option value="cleaning_repair">Cleaning & Repair</option>
                  <option value="it_technology">IT & Technology</option>
                  <option value="education_training">Education & Training</option>
                  <option value="life_health">Life & Health</option>
                  <option value="design_consulting">Design & Consulting</option>
                  <option value="other">Other Services</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="price">Order Amount *</label>
                <div class="price-input">
                  <span class="currency">S$</span>
                  <input 
                    type="number" 
                    id="price" 
                    v-model.number="form.price" 
                    required
                    placeholder="0"
                    min="0.01"
                    step="0.01"
                  >
                </div>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="location">Service Location *</label>
                <select id="location" v-model="form.location" required>
                  <option value="">Please select location</option>
                  <option value="NORTH">North</option>
                  <option value="SOUTH">South</option>
                  <option value="EAST">East</option>
                  <option value="WEST">West</option>
                  <option value="CENTRAL">Central</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="address">Detailed Address</label>
                <input 
                  type="text" 
                  id="address" 
                  v-model="form.address" 
                  placeholder="Please enter detailed address"
                  maxlength="200"
                >
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>Service Schedule</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="service_start_time">Service Start Time</label>
                <input 
                  type="datetime-local" 
                  id="service_start_time" 
                  v-model="form.service_start_time"
                >
              </div>
              
              <div class="form-group">
                <label for="service_end_time">Service End Time</label>
                <input 
                  type="datetime-local" 
                  id="service_end_time" 
                  v-model="form.service_end_time"
                >
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="goBack">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Cancel
            </button>
            <button type="submit" class="publish-btn" :disabled="publishing">
              <svg v-if="publishing" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
              </svg>
              {{ publishing ? (isEditMode ? 'Saving...' : 'Publishing...') : (isEditMode ? 'Save Changes' : 'Publish Task') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import { customerAPI } from '@/api/auth.js'

export default {
  name: 'PublishTask',
  components: {
    NavBar
  },
  data() {
    return {
      publishing: false,
      isEditMode: false,
      editingTaskId: null,
      form: {
        title: '',
        description: '',
        service_type: '',
        price: null,
        location: '',
        address: '',
        service_start_time: '',
        service_end_time: ''
      }
    }
  },
  created() {
    this.checkEditMode()
  },
  methods: {
    checkEditMode() {
      const query = this.$route.query
      if (query.edit === 'true' && query.id) {
        this.isEditMode = true
        this.editingTaskId = parseInt(query.id)
        this.loadTaskForEdit()
      }
    },
    loadTaskForEdit() {
      // Load task data from local storage
      const tasks = JSON.parse(localStorage.getItem('tasks') || '[]')
      const task = tasks.find(t => t.id === this.editingTaskId)
      
      if (task) {
        this.form = {
          title: task.title || '',
          description: task.description || '',
          service_type: task.service_type || '',
          price: task.price || null,
          location: task.location || '',
          address: task.address || '',
          service_start_time: task.service_start_time || '',
          service_end_time: task.service_end_time || ''
        }
      } else {
        alert('Task does not exist, returning to homepage')
        this.$router.push('/?role=customer')
      }
    },
    async publishTask() {
      // Validate form
      if (!this.validateForm()) {
        return
      }
      
      this.publishing = true
      
      try {
        // Prepare order data according to API specification
        const orderData = {
          title: this.form.title,
          description: this.form.description || undefined,
          service_type: this.form.service_type,
          price: this.form.price,
          location: this.form.location,
          address: this.form.address || undefined,
          service_start_time: this.form.service_start_time || undefined,
          service_end_time: this.form.service_end_time || undefined
        }
        
        // Call the API to publish order
        const response = await customerAPI.publishOrder(orderData)
        
        if (response.success) {
          alert(`Order "${this.form.title}" published successfully! Waiting for admin approval.`)
          // Return to homepage
          this.$router.push('/?role=customer')
        } else {
          alert('Publish failed: ' + (response.message || 'Unknown error'))
        }
      } catch (error) {
        console.error('Failed to publish order:', error)
        alert('Publish failed: ' + (error.message || 'Network error, please try again later'))
      } finally {
        this.publishing = false
      }
    },
    validateForm() {
      if (!this.form.title.trim()) {
        alert('Please enter task title')
        return false
      }
      if (!this.form.service_type) {
        alert('Please select service type')
        return false
      }
      if (!this.form.price || this.form.price <= 0) {
        alert('Please enter valid order amount (must be greater than 0)')
        return false
      }
      if (!this.form.location) {
        alert('Please select service location')
        return false
      }
      if (this.form.service_start_time && this.form.service_end_time) {
        if (new Date(this.form.service_end_time) <= new Date(this.form.service_start_time)) {
          alert('Service end time must be later than start time')
          return false
        }
      }
      return true
    },
    goBack() {
      this.$router.go(-1)
    }
  }
}
</script>

<style scoped>
.publish-task-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  max-width: 800px;
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
  font-size: 16px;
  color: #666;
  margin: 0;
}

.form-container {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.task-form {
  max-width: 100%;
}

.form-section {
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
}

.form-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 25px 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px 16px;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #74b9ff;
  box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.1);
}

.price-input {
  position: relative;
  display: flex;
  align-items: center;
}

.currency {
  position: absolute;
  left: 16px;
  color: #666;
  font-weight: 500;
  z-index: 1;
}

.price-input input {
  padding-left: 40px;
}

.char-count {
  font-size: 12px;
  color: #999;
  text-align: right;
}


.form-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid #f0f0f0;
}

.cancel-btn,
.publish-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #e9ecef;
}

.cancel-btn:hover {
  background: #e9ecef;
  color: #333;
}

.publish-btn {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
}

.publish-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

/* Customer theme colors */
.customer-theme .publish-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .publish-btn:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.customer-theme .form-group input:focus,
.customer-theme .form-group select:focus,
.customer-theme .form-group textarea:focus {
  border-color: #00b894;
  box-shadow: 0 0 0 3px rgba(0, 184, 148, 0.1);
}


.publish-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
  
  .form-container {
    padding: 20px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cancel-btn,
  .publish-btn {
    width: 100%;
    justify-content: center;
  }
  
}
</style>
