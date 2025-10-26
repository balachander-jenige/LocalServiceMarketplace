<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>Welcome Back</h1>
        <p>Please log in to your account</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
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

        <button type="submit" class="login-btn" :disabled="loading">
          <svg v-if="loading" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
          </svg>
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <div class="login-footer">
        <p>Don't have an account? <router-link to="/register" class="register-link">Register now</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI, tokenManager } from '@/api/auth.js'

export default {
  name: 'LoginPage',
  data() {
    return {
      loading: false,
      form: {
        email: '',
        password: ''
      },
      errors: {}
    }
  },
  methods: {
    validateForm() {
      this.errors = {}
      
      if (!this.form.email.trim()) {
        this.errors.email = 'Please enter email'
      } else if (!this.isValidEmail(this.form.email)) {
        this.errors.email = 'Please enter a valid email address'
      }
      
      if (!this.form.password.trim()) {
        this.errors.password = 'Please enter password'
      }
      
      return Object.keys(this.errors).length === 0
    },
    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },
    async handleLogin() {
      if (!this.validateForm()) {
        return
      }
      
      this.loading = true
      
      try {
        const response = await authAPI.login({
          email: this.form.email,
          password: this.form.password
        })
        
        if (response.success) {
          // Save token
          tokenManager.setToken(response.data.access_token)
          
          // Get user details
          try {
            const userResponse = await authAPI.getCurrentUser()
            if (userResponse.success) {
              const userData = userResponse.data
              // Save user info to sessionStorage, including role info
              sessionStorage.setItem('currentUser', JSON.stringify({
                email: this.form.email,
                token: response.data.access_token,
                role: userData.role_id === 1 ? 'customer' : (userData.role_id === 2 ? 'provider' : 'admin'),
                username: userData.username,
                role_id: userData.role_id
              }))
              
              this.loading = false
              alert('Login successful!')
              
              // Jump to corresponding page based on role
              if (userData.role_id === 3) {
                // Admin users jump directly to admin dashboard
                this.$router.push('/admin')
              } else {
                let role = userData.role_id === 1 ? 'customer' : 'provider'
                this.$router.push(`/?role=${role}`)
              }
            } else {
              throw new Error('Failed to get user information')
            }
          } catch (userError) {
            console.error('Failed to get user info:', userError)
            // If getting user info fails, still save basic info
            sessionStorage.setItem('currentUser', JSON.stringify({
              email: this.form.email,
              token: response.data.access_token,
              role: 'customer' // Default to customer
            }))
            
            this.loading = false
            alert('Login successful!')
            this.$router.push('/?role=customer')
          }
        } else {
          this.loading = false
          alert(response.message || 'Login failed, please check email and password')
        }
      } catch (error) {
        this.loading = false
        console.error('Login error:', error)
        alert('Login failed: ' + error.message)
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 10px 0;
}

.login-header p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.login-form {
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

.login-btn {
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

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.login-btn:disabled {
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

.login-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.login-footer p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.register-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.register-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-container {
    padding: 30px 20px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}
</style>
