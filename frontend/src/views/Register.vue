<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <h1>Create Account</h1>
        <p>Please fill in the information to complete registration</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            type="text" 
            id="username" 
            v-model="form.username" 
            required
            placeholder="Please enter username"
            :class="{ 'error': errors.username }"
          >
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input 
            type="email" 
            id="email" 
            v-model="form.email" 
            required
            placeholder="Please enter email"
            :class="{ 'error': errors.email }"
          >
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password" 
            v-model="form.password" 
            required
            placeholder="Please enter password"
            :class="{ 'error': errors.password }"
          >
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input 
            type="password" 
            id="confirmPassword" 
            v-model="form.confirmPassword" 
            required
            placeholder="Please enter password again"
            :class="{ 'error': errors.confirmPassword }"
          >
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
        </div>

        <div class="form-group">
          <label for="role">Role</label>
          <select id="role" v-model="form.role" required :class="{ 'error': errors.role }">
            <option value="">Please select role</option>
            <option value="1">Customer</option>
            <option value="2">Service Provider</option>
          </select>
          <span v-if="errors.role" class="error-message">{{ errors.role }}</span>
        </div>

        <div class="role-description">
          <div v-if="form.role === '1'" class="role-info customer-info">
            <h4>Customer Role</h4>
            <p>As a customer, you can:</p>
            <ul>
              <li>Publish task requirements</li>
              <li>Manage your tasks</li>
              <li>View task progress</li>
              <li>Communicate with service providers</li>
            </ul>
          </div>
          <div v-else-if="form.role === '2'" class="role-info provider-info">
            <h4>Service Provider Role</h4>
            <p>As a service provider, you can:</p>
            <ul>
              <li>Browse and accept tasks</li>
              <li>Showcase your skills</li>
              <li>Manage accepted tasks</li>
              <li>Communicate with customers</li>
            </ul>
          </div>
        </div>

        <button type="submit" class="register-btn" :disabled="loading">
          <svg v-if="loading" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
          </svg>
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </form>

      <div class="register-footer">
        <p>Already have an account? <router-link to="/login" class="login-link">Login now</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '@/api/auth.js'

export default {
  name: 'RegisterPage',
  data() {
    return {
      loading: false,
      form: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: ''
      },
      errors: {}
    }
  },
  methods: {
    validateForm() {
      this.errors = {}
      
      if (!this.form.username.trim()) {
        this.errors.username = 'Please enter username'
      } else if (this.form.username.length < 3) {
        this.errors.username = 'Username must be at least 3 characters'
      }
      
      if (!this.form.email.trim()) {
        this.errors.email = 'Please enter email'
      } else if (!this.isValidEmail(this.form.email)) {
        this.errors.email = 'Please enter a valid email address'
      }
      
      if (!this.form.password.trim()) {
        this.errors.password = 'Please enter password'
      } else if (this.form.password.length < 6) {
        this.errors.password = 'Password must be at least 6 characters'
      }
      
      if (!this.form.confirmPassword.trim()) {
        this.errors.confirmPassword = 'Please confirm password'
      } else if (this.form.password !== this.form.confirmPassword) {
        this.errors.confirmPassword = 'Passwords do not match'
      }
      
      if (!this.form.role) {
        this.errors.role = 'Please select role'
      }
      
      return Object.keys(this.errors).length === 0
    },
    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },
    async handleRegister() {
      if (!this.validateForm()) {
        return
      }
      
      this.loading = true
      
      try {
        const response = await authAPI.register({
          username: this.form.username,
          email: this.form.email,
          password: this.form.password,
          role_id: parseInt(this.form.role)
        })
        
        if (response.success) {
          this.loading = false
          alert('Registration successful! Please login to your account')
          
          // Jump to login page
          this.$router.push('/login')
        } else {
          this.loading = false
          alert(response.message || 'Registration failed, please try again')
        }
      } catch (error) {
        this.loading = false
        console.error('Registration error:', error)
        alert('Registration failed: ' + error.message)
      }
    }
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 500px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 10px 0;
}

.register-header p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
.form-group select {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input.error,
.form-group select.error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 4px;
}

.role-description {
  margin: 20px 0;
}

.role-info {
  padding: 20px;
  border-radius: 8px;
  border: 2px solid #e1e5e9;
  background: #f8f9fa;
}

.role-info h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
}

.role-info p {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.role-info ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
  font-size: 14px;
}

.role-info li {
  margin-bottom: 5px;
}

.customer-info {
  border-color: #00b894;
  background: rgba(0, 184, 148, 0.05);
}

.customer-info h4 {
  color: #00b894;
}

.provider-info {
  border-color: #74b9ff;
  background: rgba(116, 185, 255, 0.05);
}

.provider-info h4 {
  color: #74b9ff;
}

.register-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.register-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.register-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.register-footer p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.login-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.login-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

@media (max-width: 480px) {
  .register-container {
    padding: 30px 20px;
  }
  
  .register-header h1 {
    font-size: 24px;
  }
}
</style>
