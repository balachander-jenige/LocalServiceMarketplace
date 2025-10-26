<template>
  <AdminLayout page-title="Admin Dashboard" :breadcrumb="[{ name: 'Dashboard' }]">
    <AdminPage 
      :show-header="false"
      :show-empty="false"
    >
      <div class="dashboard-content">
        <div class="welcome-section">
          <div class="welcome-card">
            <div class="welcome-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2ZM12 18C14.21 18 16 16.21 16 14C16 11.79 14.21 10 12 10C9.79 10 8 11.79 8 14C8 16.21 9.79 18 12 18ZM12 20C8.69 20 6 17.31 6 14C6 10.69 8.69 8 12 8C15.31 8 18 10.69 18 14C18 17.31 15.31 20 12 20Z" fill="currentColor"/>
              </svg>
            </div>
            <h2 class="welcome-title">Welcome to Freelancer Admin Dashboard</h2>
            <p class="welcome-subtitle">Dear admin, have a great day!</p>
          </div>
        </div>
      </div>
    </AdminPage>
  </AdminLayout>
</template>

<script>
import AdminLayout from '@/components/AdminLayout.vue'
import AdminPage from '@/components/AdminPage.vue'

export default {
  name: 'AdminDashboard',
  components: {
    AdminLayout,
    AdminPage
  },
  data() {
    return {
      currentUser: null
    }
  },
  created() {
    this.checkLoginStatus()
  },
  methods: {
    checkLoginStatus() {
      const user = sessionStorage.getItem('currentUser')
      if (user) {
        this.currentUser = JSON.parse(user)
      }
    }
  }
}
</script>

<style scoped>
.dashboard-content {
  width: 100%;
}

.welcome-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.welcome-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 20px;
  padding: 48px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(20px);
  max-width: 500px;
  width: 100%;
}

.welcome-icon {
  color: #4f46e5;
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.welcome-icon svg {
  filter: drop-shadow(0 0 20px rgba(79, 70, 229, 0.3));
}

.welcome-title {
  margin: 0 0 16px 0;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  background: linear-gradient(135deg, #1e293b, #475569);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 16px;
  line-height: 1.6;
}

/* Responsive Design */
@media (max-width: 768px) {
  .welcome-card {
    padding: 32px 24px;
    margin: 0 16px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-subtitle {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .welcome-card {
    padding: 24px 20px;
  }
  
  .welcome-title {
    font-size: 20px;
  }
  
  .welcome-icon svg {
    width: 40px;
    height: 40px;
  }
}
</style>
