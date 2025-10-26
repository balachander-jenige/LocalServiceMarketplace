<template>
  <div class="profile-page" :class="{ 'customer-theme': $route.query.role === 'customer' }">
    <NavBar />
    
    <div class="main-content">
      <div class="page-header">
        <h1>Profile</h1>
        <p>Manage your personal information and account settings</p>
      </div>

      <div class="profile-container">
        <!-- Profile display -->
        <div v-if="!isEditing" class="profile-display">
          <!-- Personal Information Module -->
          <div class="profile-info-section">
              <div class="profile-card">
                <div class="user-info">
                  <h2 class="username">{{ userInfo.username }}</h2>
                  <div class="info-grid">
                    <div class="info-item">
                      <div class="info-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Username
                      </div>
                      <div class="info-value">{{ userInfo.username }}</div>
                    </div>
                    
                    <div class="info-item">
                      <div class="info-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Email Address
                      </div>
                      <div class="info-value">{{ userInfo.email }}</div>
                    </div>
                    
                    <div v-if="!isProvider" class="info-item">
                      <div class="info-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Location
                      </div>
                      <div class="info-value">{{ userInfo.location }}</div>
                    </div>
                    
                    <div v-if="!isProvider" class="info-item">
                      <div class="info-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M21 16V8C21 7.46957 20.7893 6.96086 20.4142 6.58579C20.0391 6.21071 19.5304 6 19 6H5C4.46957 6 3.96086 6.21071 3.58579 6.58579C3.21071 6.96086 3 7.46957 3 8V16C3 16.5304 3.21071 17.0391 3.58579 17.4142C3.96086 17.7893 4.46957 18 5 18H19C19.5304 18 20.0391 17.7893 20.4142 17.4142C20.7893 17.0391 21 16.5304 21 16Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          <polyline points="7,10 12,15 17,10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Address
                      </div>
                      <div class="info-value">{{ userInfo.address }}</div>
                    </div>
                    
                    <!-- Provider specific fields -->
                    <div v-if="isProvider" class="info-item">
                      <div class="info-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Skills
                      </div>
                      <div class="info-value">
                        <span v-for="(skill, index) in userInfo.skills" :key="index" class="skill-tag">
                          {{ skill }}
                        </span>
                      </div>
                    </div>
                    
                    <div v-if="isProvider" class="info-item">
                      <div class="info-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Experience Years
                      </div>
                      <div class="info-value">{{ userInfo.experience_years != null ? (userInfo.experience_years + ' years') : '' }}</div>
                    </div>
                    
                    <div v-if="isProvider" class="info-item">
                      <div class="info-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 1V23M17 5H9.5C8.57174 5 7.6815 5.36875 7.02513 6.02513C6.36875 6.6815 6 7.57174 6 8.5C6 9.42826 6.36875 10.3185 7.02513 10.9749C7.6815 11.6312 8.57174 12 9.5 12H14.5C15.4283 12 16.3185 12.3687 16.9749 13.0251C17.6312 13.6815 18 14.5717 18 15.5C18 16.4283 17.6312 17.3185 16.9749 17.9749C16.3185 18.6312 15.4283 19 14.5 19H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Hourly Rate
                      </div>
                      <div class="info-value">{{ userInfo.hourly_rate != null ? ('$' + userInfo.hourly_rate + '/hour') : '' }}</div>
                    </div>
                    
                    <div v-if="isProvider" class="info-item">
                      <div class="info-label">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                          <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Availability
                      </div>
                      <div class="info-value">{{ userInfo.availability || '' }}</div>
                    </div>
                  </div>
                </div>
            
                <!-- Personal Information Action Buttons -->
                <div class="action-buttons">
                  <button class="edit-btn" @click="startEdit">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13M18.5 2.5C18.8978 2.10218 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10218 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10218 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Edit Information
                  </button>
                  <button class="change-password-btn" @click="changePassword">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                      <circle cx="12" cy="16" r="1" stroke="currentColor" stroke-width="2"/>
                      <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Change Password
                  </button>
                </div>
              </div>
          </div>
          
          <!-- Rating and Review Module - Only shown for service providers, placed below personal info module -->
          <div v-if="isProvider" class="reviews-section">
                <div class="section-header">
                  <h3>My Ratings and Reviews</h3>
                </div>
                
                <!-- Rating Overview -->
                <div v-if="ratingInfo" class="rating-overview">
                  <div class="rating-card">
                    <div class="rating-score">
                      <div class="score-number">{{ ratingInfo.average_rating || 0 }}</div>
                      <div class="score-label">Average Rating</div>
                    </div>
                    <div class="rating-details">
                      <div class="total-reviews">
                        <span class="label">Total Reviews:</span>
                        <span class="value">{{ ratingInfo.total_reviews || 0 }}</span>
                      </div>
                      <div class="rating-stars">
                        <span v-for="star in 5" :key="star" class="star" :class="{ filled: star <= Math.round(ratingInfo.average_rating || 0) }">
                          ★
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Review List -->
                <div class="reviews-list">
                  <div class="reviews-header">
                    <h4>Customer Reviews</h4>
                    <button v-if="!showAllReviews && reviewsList.length > 3" @click="showAllReviews = true" class="show-more-btn">
                      View All ({{ reviewsList.length }})
                    </button>
                    <button v-if="showAllReviews" @click="showAllReviews = false" class="show-more-btn">
                      Collapse
                    </button>
                  </div>
                  
                  <div v-if="loadingReviews" class="loading-state">
                    <div class="loading-spinner"></div>
                    <p>Loading reviews...</p>
                  </div>
                  
                  <div v-else-if="reviewsList.length === 0" class="empty-state">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2L15.09 8.26L22 9L17 14.74L18.18 21.02L12 17.77L5.82 21.02L7 14.74L2 9L8.91 8.26L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <p>No reviews yet</p>
                  </div>
                  
                  <div v-else class="reviews-container">
                    <div 
                      v-for="(review, index) in displayReviews" 
                      :key="review.order_id" 
                      class="review-item"
                      :class="{ 'show': showAllReviews || index < 3 }"
                    >
                      <div class="review-header">
                        <div class="review-stars">
                          <span v-for="star in 5" :key="star" class="star" :class="{ filled: star <= review.stars }">
                            ★
                          </span>
                        </div>
                        <div class="review-date">{{ formatDate(review.created_at) }}</div>
                      </div>
                      <div class="review-content">
                        <p>{{ review.content || 'Customer did not leave review content' }}</p>
                      </div>
                    </div>
                  </div>
                </div>
          </div>
        </div>

        <!-- Edit mode -->
        <div v-else class="profile-edit">
          <div class="edit-card">
            <div class="edit-header">
              <h2>Edit Personal Information</h2>
              <button class="cancel-btn" @click="cancelEdit">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
                  <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="saveProfile" class="edit-form">
              <div class="form-group">
                <label for="username">Username</label>
                <input 
                  type="text" 
                  id="username" 
                  v-model="editForm.username" 
                  :disabled="true"
                  placeholder="Username cannot be changed"
                  class="disabled-input"
                >
              </div>
              
              <!-- Provider specific fields -->
              <div v-if="isProvider" class="form-group">
                <label for="skills">Skills</label>
                <div class="skills-input-container">
                  <input 
                    type="text" 
                    id="skills" 
                    v-model="newSkill" 
                    placeholder="Enter a skill and press Enter"
                    @keyup.enter="addSkill"
                    class="skill-input"
                  >
                  <button type="button" @click="addSkill" class="add-skill-btn">Add</button>
                </div>
                <div class="skills-display">
                  <span 
                    v-for="(skill, index) in editForm.skills" 
                    :key="index" 
                    class="skill-tag editable"
                  >
                    {{ skill }}
                    <button type="button" @click="removeSkill(index)" class="remove-skill">×</button>
                  </span>
                </div>
              </div>
              
              <div v-if="isProvider" class="form-group">
                <label for="experience_years">Experience Years</label>
                <input 
                  type="number" 
                  id="experience_years" 
                  v-model.number="editForm.experience_years" 
                  min="0"
                  max="50"
                  placeholder="Enter years of experience"
                >
              </div>
              
              <div v-if="isProvider" class="form-group">
                <label for="hourly_rate">Hourly Rate ($)</label>
                <input 
                  type="number" 
                  id="hourly_rate" 
                  v-model.number="editForm.hourly_rate" 
                  min="0"
                  step="0.01"
                  placeholder="Enter hourly rate"
                >
              </div>
              
              <div v-if="isProvider" class="form-group">
                <label for="availability">Availability</label>
                <textarea 
                  id="availability" 
                  v-model="editForm.availability" 
                  placeholder="Enter your availability (e.g., Monday to Friday 9:00-18:00)"
                  rows="3"
                ></textarea>
              </div>
              
              <!-- Customer specific fields -->
              <div v-if="!isProvider" class="form-group">
                <label for="email">Email Address</label>
                <input 
                  type="email" 
                  id="email" 
                  v-model="editForm.email" 
                  :disabled="true"
                  placeholder="Email cannot be changed"
                  class="disabled-input"
                >
              </div>
              
              <div v-if="!isProvider" class="form-group">
                <label for="location">Location</label>
                <select id="location" v-model="editForm.location" required>
                  <option value="">Please select location</option>
                  <option value="NORTH">North</option>
                  <option value="SOUTH">South</option>
                  <option value="EAST">East</option>
                  <option value="WEST">West</option>
                  <option value="CENTRAL">Central</option>
                </select>
              </div>
              
              <div v-if="!isProvider" class="form-group">
                <label for="address">Address</label>
                <textarea 
                  id="address" 
                  v-model="editForm.address" 
                  required
                  placeholder="Please enter detailed address"
                  rows="3"
                ></textarea>
              </div>
              
              <div class="form-actions">
                <button type="button" class="cancel-btn" @click="cancelEdit">Cancel</button>
                <button type="submit" class="save-btn" :disabled="saving">
                  <svg v-if="saving" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
                  </svg>
                  {{ saving ? 'Saving...' : 'Save' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Change password modal -->
        <div v-if="showPasswordModal" class="modal-overlay" @click="closePasswordModal">
          <div class="password-modal" @click.stop>
            <div class="modal-header">
              <h3>Change Password</h3>
              <button class="close-btn" @click="closePasswordModal">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="savePassword" class="password-form">
              <div class="form-group">
                <label for="currentPassword">Current Password</label>
                <input 
                  type="password" 
                  id="currentPassword" 
                  v-model="passwordForm.currentPassword" 
                  required
                  placeholder="Please enter current password"
                >
              </div>
              
              <div class="form-group">
                <label for="newPassword">New Password</label>
                <input 
                  type="password" 
                  id="newPassword" 
                  v-model="passwordForm.newPassword" 
                  required
                  placeholder="Please enter new password"
                  minlength="6"
                >
              </div>
              
              <div class="form-group">
                <label for="confirmPassword">Confirm New Password</label>
                <input 
                  type="password" 
                  id="confirmPassword" 
                  v-model="passwordForm.confirmPassword" 
                  required
                  placeholder="Please enter new password again"
                >
              </div>
              
              <div class="form-actions">
                <button type="button" class="cancel-btn" @click="closePasswordModal">Cancel</button>
                <button type="submit" class="save-btn" :disabled="savingPassword">
                  <svg v-if="savingPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
                  </svg>
                  {{ savingPassword ? 'Saving...' : 'Save' }}
                </button>
              </div>
            </form>
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
  name: 'ProfilePage',
  components: {
    NavBar
  },
  data() {
    return {
      isEditing: false,
      saving: false,
      showPasswordModal: false,
      savingPassword: false,
      userInfo: {
        user_id: null,
        username: '',
        email: '',
        location: '',
        address: '',
        budget_preference: 0,
        balance: 0,
        // Provider specific fields
        skills: [],
        experience_years: null,
        hourly_rate: null,
        availability: '',
        portfolio: [],
        total_earnings: 0,
        rating: 0,
        total_reviews: 0,
        created_at: '',
        updated_at: ''
      },
      editForm: {
        username: '',
        email: '',
        location: '',
        address: '',
        // Provider specific fields
        skills: [],
        experience_years: null,
        hourly_rate: null,
        availability: ''
      },
      newSkill: '',
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      // Rating and review related data
      ratingInfo: null,
      reviewsList: [],
      loadingReviews: false,
      showAllReviews: false
    }
  },
  computed: {
    isProvider() {
      const currentUser = sessionStorage.getItem('currentUser')
      if (currentUser) {
        const user = JSON.parse(currentUser)
        return user.role === 'provider' || this.$route.query.role === 'provider'
      }
      return false
    },
    displayReviews() {
      return this.showAllReviews ? this.reviewsList : this.reviewsList.slice(0, 3)
    }
  },
  async created() {
    await this.loadUserInfo()
    // If service provider, load rating and review data
    if (this.isProvider) {
      this.loadRatingAndReviews()
    }
  },
  methods: {
    async loadUserInfo() {
      try {
        const currentUser = sessionStorage.getItem('currentUser')
        if (currentUser) {
          const user = JSON.parse(currentUser)
          console.log('User role:', user.role, 'Route parameter:', this.$route.query.role)
          
          if (user.role === 'customer' || this.$route.query.role === 'customer') {
            // Call customer profile API
            try {
              const response = await customerAPI.getProfile()
              console.log('Customer profile API response:', response)
              if (response.success && response.data) {
                this.userInfo = {
                  user_id: response.data.user_id,
                  username: user.username || '',
                  email: user.email || '',
                  location: response.data.location || 'CENTRAL',
                  address: response.data.address || '',
                  budget_preference: response.data.budget_preference || 0,
                  balance: response.data.balance || 0,
                  skills: [],
                  experience_years: null,
                  hourly_rate: null,
                  availability: '',
                  portfolio: [],
                  total_earnings: 0,
                  rating: 0,
                  total_reviews: 0,
                  created_at: response.data.created_at || '',
                  updated_at: response.data.updated_at || ''
                }
              }
            } catch (error) {
              console.error('Failed to get customer profile:', error)
              // If getting fails, use sessionStorage info
              this.userInfo = {
                user_id: user.user_id || null,
                username: user.username || '',
                email: user.email || '',
                location: user.location || 'CENTRAL',
                address: user.address || '',
                budget_preference: 0,
                balance: 0,
                skills: [],
                experience_years: null,
                hourly_rate: null,
                availability: '',
                portfolio: [],
                total_earnings: 0,
                rating: 0,
                total_reviews: 0,
                created_at: '',
                updated_at: ''
              }
            }
          } else if (user.role === 'provider' || this.$route.query.role === 'provider') {
            // Call provider profile API
            try {
              const response = await providerAPI.getProfile()
              console.log('Provider profile API response:', response)
              if (response.success && response.data) {
                this.userInfo = {
                  user_id: response.data.user_id,
                  username: user.username || '',
                  email: user.email || '',
                  location: response.data.location || '',
                  address: response.data.address || '',
                  budget_preference: 0,
                  balance: 0,
                  skills: response.data.skills || [],
                  experience_years: (response.data.experience_years ?? null),
                  hourly_rate: (response.data.hourly_rate ?? null),
                  availability: response.data.availability || '',
                  portfolio: response.data.portfolio || [],
                  total_earnings: response.data.total_earnings || 0,
                  rating: response.data.rating || 0,
                  total_reviews: response.data.total_reviews || 0,
                  created_at: response.data.created_at || '',
                  updated_at: response.data.updated_at || ''
                }
              }
            } catch (error) {
              console.error('Failed to get provider profile:', error)
              // If getting fails, use sessionStorage info
              this.userInfo = {
                user_id: user.user_id || null,
                username: user.username || '',
                email: user.email || '',
                location: user.location || '',
                address: user.address || '',
                budget_preference: 0,
                balance: 0,
                skills: [],
                experience_years: null,
                hourly_rate: null,
                availability: '',
                portfolio: [],
                total_earnings: 0,
                rating: 0,
                total_reviews: 0,
                created_at: '',
                updated_at: ''
              }
            }
          } else {
            // Other roles, use sessionStorage info
            this.userInfo = {
              user_id: user.user_id || null,
              username: user.username || '',
              email: user.email || '',
              location: user.location || 'CENTRAL',
              address: user.address || '',
              budget_preference: 0,
              balance: 0,
              skills: [],
              experience_years: null,
              hourly_rate: null,
              availability: '',
              portfolio: [],
              total_earnings: 0,
              rating: 0,
              total_reviews: 0,
              created_at: '',
              updated_at: ''
            }
          }
        } else {
          // If no logged-in user info, use default values
          this.userInfo = {
            user_id: null,
            username: 'Guest User',
            email: 'guest@example.com',
            location: 'CENTRAL',
            address: 'No address provided',
            budget_preference: 0,
            balance: 0,
            skills: [],
            experience_years: null,
            hourly_rate: null,
            availability: '',
            portfolio: [],
            total_earnings: 0,
            rating: 0,
            total_reviews: 0,
            created_at: '',
            updated_at: ''
          }
        }
      } catch (error) {
        console.error('Failed to load user info:', error)
        // If API call fails, fallback to sessionStorage
        const currentUser = sessionStorage.getItem('currentUser')
        if (currentUser) {
          const user = JSON.parse(currentUser)
          this.userInfo = {
            user_id: user.user_id || null,
            username: user.username || '',
            email: user.email || '',
            location: user.location || 'CENTRAL',
            address: user.address || '',
            budget_preference: 0,
            balance: 0,
            skills: [],
            experience_years: null,
            hourly_rate: null,
            availability: '',
            portfolio: [],
            total_earnings: 0,
            rating: 0,
            total_reviews: 0,
            created_at: '',
            updated_at: ''
          }
        }
      }
    },
    startEdit() {
      if (this.isProvider) {
        // Provider specific edit form
        this.editForm = {
          username: this.userInfo.username,
          email: this.userInfo.email,
          location: '',
          address: '',
          // Provider specific fields
          skills: [...(this.userInfo.skills || [])],
          experience_years: this.userInfo.experience_years,
          hourly_rate: this.userInfo.hourly_rate,
          availability: this.userInfo.availability || ''
        }
      } else {
        // Customer edit form
        this.editForm = {
          username: this.userInfo.username,
          email: this.userInfo.email,
          location: this.userInfo.location,
          address: this.userInfo.address,
          // Provider specific fields
          skills: [],
          experience_years: null,
          hourly_rate: null,
          availability: ''
        }
      }
      this.isEditing = true
    },
    cancelEdit() {
      this.isEditing = false
      this.editForm = {
        username: '',
        email: '',
        location: '',
        address: '',
        // Provider specific fields
        skills: [],
        experience_years: null,
        hourly_rate: null,
        availability: ''
      }
      this.newSkill = ''
    },
    async saveProfile() {
      this.saving = true
      
      try {
        // Check if customer role
        const currentUser = sessionStorage.getItem('currentUser')
        if (currentUser) {
          const user = JSON.parse(currentUser)
          console.log('User info when saving:', user)
          console.log('User role:', user.role, 'Route parameter:', this.$route.query.role)
          
          if (user.role === 'customer' || this.$route.query.role === 'customer') {
            // Call customer updateProfile API
            const updateData = {
              location: this.editForm.location,
              address: this.editForm.address
            }
            
            console.log('Sending customer profile update request:', updateData)
            const response = await customerAPI.updateProfile(updateData)
            console.log('Customer profile update response:', response)
            
            if (response.success && response.data) {
              // Update local user info
              this.userInfo.location = response.data.location
              this.userInfo.address = response.data.address
              this.userInfo.updated_at = response.data.updated_at
              
              // Update sessionStorage
              user.location = response.data.location
              user.address = response.data.address
              sessionStorage.setItem('currentUser', JSON.stringify(user))
              
              alert('Customer profile updated successfully!')
            } else {
              alert('Update failed: ' + (response.message || 'Unknown error'))
            }
          } else if (user.role === 'provider' || this.$route.query.role === 'provider') {
            // Call provider updateProfile API
            const updateData = {
              skills: this.editForm.skills,
              experience_years: this.editForm.experience_years,
              hourly_rate: this.editForm.hourly_rate,
              availability: this.editForm.availability
            }
            
            console.log('Sending provider profile update request:', updateData)
            const response = await providerAPI.updateProfile(updateData)
            console.log('Provider profile update response:', response)
            
            if (response.success && response.data) {
              // Update local user info
              this.userInfo.skills = response.data.skills || []
              this.userInfo.experience_years = response.data.experience_years
              this.userInfo.hourly_rate = response.data.hourly_rate
              this.userInfo.availability = response.data.availability || ''
              this.userInfo.updated_at = response.data.updated_at
              
              alert('Provider profile updated successfully!')
            } else {
              alert('Update failed: ' + (response.message || 'Unknown error'))
            }
          } else {
            // Other roles, use local update
            this.userInfo.username = this.editForm.username
            this.userInfo.email = this.editForm.email
            this.userInfo.location = this.editForm.location
            this.userInfo.address = this.editForm.address
            
            // Update sessionStorage with new user information
            user.username = this.editForm.username
            user.email = this.editForm.email
            user.location = this.editForm.location
            user.address = this.editForm.address
            sessionStorage.setItem('currentUser', JSON.stringify(user))
            
            alert('Personal information saved successfully!')
          }
        }
      } catch (error) {
        console.error('Failed to save user info:', error)
        alert('Save failed: ' + (error.message || 'Unknown error'))
      } finally {
        this.saving = false
        this.isEditing = false
      }
    },
    changePassword() {
      this.passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      this.showPasswordModal = true
    },
    closePasswordModal() {
      this.showPasswordModal = false
      this.passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    },
    async savePassword() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        alert('The two new passwords entered do not match, please re-enter')
        return
      }
      
      if (this.passwordForm.newPassword.length < 6) {
        alert('New password must be at least 6 characters long')
        return
      }
      
      this.savingPassword = true
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      this.savingPassword = false
      this.closePasswordModal()
      
      alert('Password changed successfully!')
    },
    addSkill() {
      if (this.newSkill.trim() && !this.editForm.skills.includes(this.newSkill.trim())) {
        this.editForm.skills.push(this.newSkill.trim())
        this.newSkill = ''
      }
    },
    removeSkill(index) {
      this.editForm.skills.splice(index, 1)
    },
    
    // Load rating and review data
    async loadRatingAndReviews() {
      if (!this.isProvider) return
      
      try {
        this.loadingReviews = true
        
        // Load rating info and review list in parallel
        const [ratingResponse, reviewsResponse] = await Promise.all([
          providerAPI.getMyRating(),
          providerAPI.getMyReviews()
        ])
        
        // Process rating info
        if (ratingResponse.success && ratingResponse.data) {
          this.ratingInfo = ratingResponse.data
          console.log('Rating info loaded successfully:', this.ratingInfo)
        } else {
          console.warn('Failed to load rating info:', ratingResponse.message)
          this.ratingInfo = {
            average_rating: 0,
            total_reviews: 0
          }
        }
        
        // Process review list
        if (reviewsResponse.success && Array.isArray(reviewsResponse.data)) {
          this.reviewsList = reviewsResponse.data
          console.log('Review list loaded successfully:', this.reviewsList)
        } else {
          console.warn('Failed to load review list:', reviewsResponse.message)
          this.reviewsList = []
        }
        
      } catch (error) {
        console.error('Failed to load rating and review data:', error)
        this.ratingInfo = {
          average_rating: 0,
          total_reviews: 0
        }
        this.reviewsList = []
      } finally {
        this.loadingReviews = false
      }
    },
    
    // Format date
    formatDate(dateString) {
      if (!dateString) return ''
      
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        console.error('Date formatting failed:', error)
        return dateString
      }
    }
  }
}
</script>

<style scoped>
.profile-page {
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

.profile-container {
  position: relative;
}

/* Personal Information Module */
.profile-info-section {
  margin-bottom: 40px;
}

.profile-display {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.profile-card {
  margin-bottom: 30px;
}

/* Customer theme colors */
.customer-theme .info-label svg {
  color: #00b894;
}

.customer-theme .edit-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .edit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 184, 148, 0.4);
}

.customer-theme .change-password-btn {
  color: #00b894;
  border-color: #00b894;
}

.customer-theme .change-password-btn:hover {
  background: #00b894;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 184, 148, 0.3);
}

.customer-theme .form-group input:focus,
.customer-theme .form-group select:focus,
.customer-theme .form-group textarea:focus {
  border-color: #00b894;
  box-shadow: 0 0 0 3px rgba(0, 184, 148, 0.1);
}

.customer-theme .save-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .save-btn:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.username {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 25px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.info-label svg {
  color: #74b9ff;
  flex-shrink: 0;
}

.info-value {
  color: #333;
  font-size: 16px;
  font-weight: 500;
}

.skill-tag {
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 6px;
  margin-bottom: 4px;
}

.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #f0f0f0;
}

.edit-btn, .change-password-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 160px;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.edit-btn {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
}

.edit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(116, 185, 255, 0.4);
}

.change-password-btn {
  background: white;
  color: #74b9ff;
  border: 2px solid #74b9ff;
}

.change-password-btn:hover {
  background: #74b9ff;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(116, 185, 255, 0.3);
}

.profile-edit {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.edit-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.cancel-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #f8f9fa;
  color: #666;
  border: 1px solid #e9ecef;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: #e9ecef;
  color: #333;
}

.edit-form {
  max-width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #74b9ff;
  box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.disabled-input {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.skills-input-container {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.skill-input {
  flex: 1;
}

.add-skill-btn {
  padding: 12px 16px;
  background: #74b9ff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-skill-btn:hover {
  background: #0984e3;
}

.skills-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag.editable {
  position: relative;
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.remove-skill {
  background: none;
  border: none;
  color: #1976d2;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.remove-skill:hover {
  background: #1976d2;
  color: white;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

.save-btn:disabled {
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.password-modal {
  background: white;
  border-radius: 12px;
  padding: 30px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f8f9fa;
  color: #666;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #e9ecef;
  color: #333;
}

.password-form {
  max-width: 100%;
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
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .action-buttons {
    flex-direction: column;
    width: 100%;
    gap: 15px;
  }
  
  .edit-btn, .change-password-btn {
    width: 100%;
    justify-content: center;
    min-width: auto;
    padding: 16px 24px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .password-modal {
    margin: 20px;
    width: calc(100% - 40px);
  }
}

/* Rating and Review Module Styles */
.reviews-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-top: 20px;
}

.section-header {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.section-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-header h3::before {
  content: '⭐';
  font-size: 18px;
}

/* Rating Overview */
.rating-overview {
  margin-bottom: 30px;
}

.rating-card {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.rating-score {
  text-align: center;
  min-width: 120px;
}

.score-number {
  font-size: 36px;
  font-weight: 700;
  color: #74b9ff;
  line-height: 1;
  margin-bottom: 5px;
}

.score-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.rating-details {
  flex: 1;
}

.total-reviews {
  margin-bottom: 10px;
  font-size: 16px;
}

.total-reviews .label {
  color: #666;
}

.total-reviews .value {
  color: #333;
  font-weight: 600;
}

.rating-stars {
  display: flex;
  gap: 2px;
}

.rating-stars .star {
  font-size: 20px;
  color: #ddd;
  transition: color 0.2s ease;
}

.rating-stars .star.filled {
  color: #ffc107;
}

/* Review List */
.reviews-list {
  margin-top: 20px;
}

.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.reviews-header h4 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.show-more-btn {
  background: none;
  border: 1px solid #74b9ff;
  color: #74b9ff;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.show-more-btn:hover {
  background: #74b9ff;
  color: white;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #74b9ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state svg {
  color: #ddd;
  margin-bottom: 15px;
}

.empty-state p {
  font-size: 16px;
  margin: 0;
}

/* Review Container */
.reviews-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-item {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(20px);
  animation: slideInUp 0.5s ease forwards;
}

.review-item:nth-child(1) { animation-delay: 0.1s; }
.review-item:nth-child(2) { animation-delay: 0.2s; }
.review-item:nth-child(3) { animation-delay: 0.3s; }
.review-item:nth-child(4) { animation-delay: 0.4s; }
.review-item:nth-child(5) { animation-delay: 0.5s; }

.review-item:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.review-stars {
  display: flex;
  gap: 2px;
}

.review-stars .star {
  font-size: 16px;
  color: #ddd;
  transition: color 0.2s ease;
}

.review-stars .star.filled {
  color: #ffc107;
}

.review-date {
  font-size: 14px;
  color: #666;
}

.review-content {
  margin-bottom: 15px;
}

.review-content p {
  color: #333;
  font-size: 16px;
  line-height: 1.6;
  margin: 0;
}


/* Animation */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .reviews-section {
    padding: 20px;
    margin-top: 20px;
  }
  
  .rating-card {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .rating-score {
    min-width: auto;
  }
  
  .reviews-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .show-more-btn {
    align-self: stretch;
  }
  
}
</style>