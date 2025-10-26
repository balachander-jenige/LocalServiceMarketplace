<template>
  <div class="test-api-page">
    <div class="test-container">
      <h1>API Test Page</h1>
      
      <div class="test-section">
        <h2>Registration Test</h2>
        <form @submit.prevent="testRegister">
          <div class="form-group">
            <label>Username:</label>
            <input v-model="registerForm.username" type="text" placeholder="Enter username">
          </div>
          <div class="form-group">
            <label>Email:</label>
            <input v-model="registerForm.email" type="email" placeholder="Enter email">
          </div>
          <div class="form-group">
            <label>Password:</label>
            <input v-model="registerForm.password" type="password" placeholder="Enter password">
          </div>
          <div class="form-group">
            <label>Role:</label>
            <select v-model="registerForm.role_id">
              <option value="1">Customer</option>
              <option value="2">Provider</option>
            </select>
          </div>
          <button type="submit" :disabled="registerLoading">
            {{ registerLoading ? 'Registering...' : 'Test Registration' }}
          </button>
        </form>
        <div v-if="registerResult" class="result">
          <h3>Registration Result:</h3>
          <pre>{{ JSON.stringify(registerResult, null, 2) }}</pre>
        </div>
      </div>

      <div class="test-section">
        <h2>登录测试</h2>
        <form @submit.prevent="testLogin">
          <div class="form-group">
            <label>Email:</label>
            <input v-model="loginForm.email" type="email" placeholder="输入邮箱">
          </div>
          <div class="form-group">
            <label>Password:</label>
            <input v-model="loginForm.password" type="password" placeholder="输入密码">
          </div>
          <button type="submit" :disabled="loginLoading">
            {{ loginLoading ? '登录中...' : '测试登录' }}
          </button>
        </form>
        <div v-if="loginResult" class="result">
          <h3>登录结果:</h3>
          <pre>{{ JSON.stringify(loginResult, null, 2) }}</pre>
        </div>
      </div>

      <div class="test-section">
        <h2>用户角色检查</h2>
        <div class="role-check-controls">
          <button @click="checkUserRole" :disabled="roleCheckLoading">
            {{ roleCheckLoading ? '检查中...' : '检查当前用户角色' }}
          </button>
        </div>
        <div v-if="roleCheckResult" class="result">
          <h3>用户角色信息:</h3>
          <pre>{{ JSON.stringify(roleCheckResult, null, 2) }}</pre>
        </div>
      </div>

      <div class="test-section">
        <h2>Customer Profile API测试</h2>
        <div class="customer-test-controls">
          <button @click="testCustomerProfile" :disabled="customerLoading">
            {{ customerLoading ? '加载中...' : '获取Customer Profile' }}
          </button>
          <button @click="testUpdateCustomerProfile" :disabled="customerUpdateLoading">
            {{ customerUpdateLoading ? '更新中...' : '更新Customer Profile' }}
          </button>
        </div>
        <div v-if="customerResult" class="result">
          <h3>Customer Profile API结果:</h3>
          <pre>{{ JSON.stringify(customerResult, null, 2) }}</pre>
        </div>
        <div v-if="customerUpdateResult" class="result">
          <h3>Customer Profile 更新结果:</h3>
          <pre>{{ JSON.stringify(customerUpdateResult, null, 2) }}</pre>
        </div>
      </div>

      <div class="test-section">
        <h2>Provider Profile API测试</h2>
        <div class="provider-test-controls">
          <button @click="testProviderProfile" :disabled="providerLoading">
            {{ providerLoading ? '加载中...' : '获取Provider Profile' }}
          </button>
          <button @click="testUpdateProviderProfile" :disabled="providerUpdateLoading">
            {{ providerUpdateLoading ? '更新中...' : '更新Provider Profile' }}
          </button>
          <button @click="testGetAvailableOrders" :disabled="availableOrdersLoading">
            {{ availableOrdersLoading ? '加载中...' : '获取可接取订单' }}
          </button>
          <button @click="testGetHistoryOrders" :disabled="historyOrdersLoading">
            {{ historyOrdersLoading ? '加载中...' : '获取历史订单' }}
          </button>
        </div>
        <div v-if="providerResult" class="result">
          <h3>Provider Profile API结果:</h3>
          <pre>{{ JSON.stringify(providerResult, null, 2) }}</pre>
        </div>
        <div v-if="providerUpdateResult" class="result">
          <h3>Provider Profile 更新结果:</h3>
          <pre>{{ JSON.stringify(providerUpdateResult, null, 2) }}</pre>
        </div>
        <div v-if="availableOrdersResult" class="result">
          <h3>可接取订单结果:</h3>
          <pre>{{ JSON.stringify(availableOrdersResult, null, 2) }}</pre>
        </div>
        <div v-if="historyOrdersResult" class="result">
          <h3>历史订单结果:</h3>
          <pre>{{ JSON.stringify(historyOrdersResult, null, 2) }}</pre>
        </div>
      </div>

      <div class="test-section">
        <h2>管理员API测试</h2>
        <div class="admin-test-controls">
          <button @click="testGetAllUsers" :disabled="adminLoading">
            {{ adminLoading ? '加载中...' : '获取所有用户' }}
          </button>
          <button @click="testGetUsersByRole(1)" :disabled="adminLoading">
            {{ adminLoading ? '加载中...' : '获取客户用户' }}
          </button>
          <button @click="testGetUsersByRole(2)" :disabled="adminLoading">
            {{ adminLoading ? '加载中...' : '获取服务提供者' }}
          </button>
          <button @click="testGetUsersByRole(3)" :disabled="adminLoading">
            {{ adminLoading ? '加载中...' : '获取管理员' }}
          </button>
        </div>
        <div v-if="adminResult" class="result">
          <h3>管理员API结果:</h3>
          <pre>{{ JSON.stringify(adminResult, null, 2) }}</pre>
        </div>
      </div>

      <div class="test-section">
        <h2>API 连接状态</h2>
        <button @click="testConnection" :disabled="connectionLoading">
          {{ connectionLoading ? '测试中...' : '测试连接' }}
        </button>
        <div v-if="connectionResult" class="result">
          <h3>连接结果:</h3>
          <pre>{{ JSON.stringify(connectionResult, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI, adminAPI, customerAPI, providerAPI } from '@/api/auth.js'

export default {
  name: 'TestAPIPage',
  data() {
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        role_id: 1
      },
      loginForm: {
        email: '',
        password: ''
      },
      registerLoading: false,
      loginLoading: false,
      connectionLoading: false,
      adminLoading: false,
      customerLoading: false,
      customerUpdateLoading: false,
      providerLoading: false,
      providerUpdateLoading: false,
      availableOrdersLoading: false,
      historyOrdersLoading: false,
      roleCheckLoading: false,
      registerResult: null,
      loginResult: null,
      connectionResult: null,
      adminResult: null,
      customerResult: null,
      customerUpdateResult: null,
      providerResult: null,
      providerUpdateResult: null,
      availableOrdersResult: null,
      historyOrdersResult: null,
      roleCheckResult: null
    }
  },
  methods: {
    async testRegister() {
      this.registerLoading = true
      this.registerResult = null
      
      try {
        const result = await authAPI.register(this.registerForm)
        this.registerResult = result
      } catch (error) {
        this.registerResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.registerLoading = false
      }
    },
    
    async testLogin() {
      this.loginLoading = true
      this.loginResult = null
      
      try {
        const result = await authAPI.login(this.loginForm)
        this.loginResult = result
      } catch (error) {
        this.loginResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.loginLoading = false
      }
    },
    
    checkUserRole() {
      this.roleCheckLoading = true
      this.roleCheckResult = null
      
      try {
        const currentUser = sessionStorage.getItem('currentUser')
        const token = localStorage.getItem('access_token')
        
        this.roleCheckResult = {
          sessionStorage: currentUser ? JSON.parse(currentUser) : null,
          token: token ? 'Token exists' : 'No token',
          tokenLength: token ? token.length : 0,
          currentRoute: this.$route.query
        }
      } catch (error) {
        this.roleCheckResult = {
          error: error.message,
          sessionStorage: sessionStorage.getItem('currentUser')
        }
      } finally {
        this.roleCheckLoading = false
      }
    },
    
    async testCustomerProfile() {
      this.customerLoading = true
      this.customerResult = null
      
      try {
        const result = await customerAPI.getProfile()
        this.customerResult = result
      } catch (error) {
        this.customerResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.customerLoading = false
      }
    },
    
    async testUpdateCustomerProfile() {
      this.customerUpdateLoading = true
      this.customerUpdateResult = null
      
      try {
        const updateData = {
          location: 'SOUTH',
          address: '456 Test Street'
        }
        
        console.log('发送更新请求:', updateData)
        const result = await customerAPI.updateProfile(updateData)
        this.customerUpdateResult = result
      } catch (error) {
        console.error('更新失败:', error)
        this.customerUpdateResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.customerUpdateLoading = false
      }
    },
    
    async testProviderProfile() {
      this.providerLoading = true
      this.providerResult = null
      
      try {
        const result = await providerAPI.getProfile()
        this.providerResult = result
      } catch (error) {
        this.providerResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.providerLoading = false
      }
    },
    
    async testUpdateProviderProfile() {
      this.providerUpdateLoading = true
      this.providerUpdateResult = null
      
      try {
        const updateData = {
          skills: ['清洁', '维修', '搬运'],
          experience_years: 5,
          hourly_rate: 50.0,
          availability: '周一至周五 9:00-18:00'
        }
        
        console.log('发送Provider更新请求:', updateData)
        const result = await providerAPI.updateProfile(updateData)
        this.providerUpdateResult = result
      } catch (error) {
        console.error('Provider更新失败:', error)
        this.providerUpdateResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.providerUpdateLoading = false
      }
    },
    
    async testGetAvailableOrders() {
      this.availableOrdersLoading = true
      this.availableOrdersResult = null
      
      try {
        const result = await providerAPI.getAvailableOrders()
        this.availableOrdersResult = result
      } catch (error) {
        this.availableOrdersResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.availableOrdersLoading = false
      }
    },
    
    async testGetHistoryOrders() {
      this.historyOrdersLoading = true
      this.historyOrdersResult = null
      
      try {
        const result = await providerAPI.getHistoryOrders()
        this.historyOrdersResult = result
      } catch (error) {
        this.historyOrdersResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.historyOrdersLoading = false
      }
    },
    
    async testGetAllUsers() {
      this.adminLoading = true
      this.adminResult = null
      
      try {
        const result = await adminAPI.getAllUsers()
        this.adminResult = result
      } catch (error) {
        this.adminResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.adminLoading = false
      }
    },
    
    async testGetUsersByRole(roleId) {
      this.adminLoading = true
      this.adminResult = null
      
      try {
        const result = await adminAPI.getAllUsers(roleId)
        this.adminResult = result
      } catch (error) {
        this.adminResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.adminLoading = false
      }
    },
    
    async testConnection() {
      this.connectionLoading = true
      this.connectionResult = null
      
      try {
        const response = await fetch('https://localservicemarketplace.space/api/v1/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'test123'
          })
        })
        
        const data = await response.json()
        this.connectionResult = {
          status: response.status,
          statusText: response.statusText,
          data: data,
          success: response.ok
        }
      } catch (error) {
        this.connectionResult = {
          error: error.message,
          success: false
        }
      } finally {
        this.connectionLoading = false
      }
    }
  }
}
</script>

<style scoped>
.test-api-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.admin-test-controls,
.customer-test-controls,
.provider-test-controls,
.role-check-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.result {
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.result pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}
</style>
