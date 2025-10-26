<template>
  <div v-if="isVisible" class="review-modal-overlay" @click="closeModal">
    <div class="review-modal" @click.stop>
      <div class="modal-header">
        <h3>Review Task</h3>
        <button class="close-btn" @click="closeModal">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <div class="modal-content">
        <!-- Task Information -->
        <div class="task-info">
          <h4>{{ task.title }}</h4>
          <p class="task-meta">
            <span class="price">S${{ task.price }}</span>
            <span class="location">{{ task.location }}</span>
          </p>
        </div>

        <!-- Star Rating -->
        <div class="rating-section">
          <label class="rating-label">Please rate this service:</label>
          <div class="star-rating">
            <button
              v-for="star in 5"
              :key="star"
              class="star-btn"
              :class="{ active: star <= rating, hover: star <= hoverRating }"
              @click="setRating(star)"
              @mouseenter="setHoverRating(star)"
              @mouseleave="setHoverRating(0)"
            >
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" 
                      stroke="currentColor" 
                      stroke-width="2" 
                      stroke-linecap="round" 
                      stroke-linejoin="round"
                      :fill="star <= rating ? 'currentColor' : 'none'"/>
              </svg>
            </button>
          </div>
          <p class="rating-text">{{ getRatingText(rating) }}</p>
        </div>

        <!-- Comment Section -->
        <div class="comment-section">
          <label class="comment-label">评价内容（可选）：</label>
          <textarea
            v-model="comment"
            class="comment-textarea"
            placeholder="请分享您对此次服务的体验和建议..."
            rows="4"
            maxlength="500"
          ></textarea>
          <div class="char-count">{{ comment.length }}/500</div>
        </div>

        <!-- Action Buttons -->
        <div class="modal-actions">
          <button class="cancel-btn" @click="closeModal">取消</button>
          <button 
            class="submit-btn" 
            :class="{ disabled: !rating }"
            :disabled="!rating || isSubmitting"
            @click="submitReview"
          >
            <span v-if="isSubmitting" class="loading-spinner"></span>
            {{ isSubmitting ? '提交中...' : '提交评价' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reviewAPI } from '@/api/auth.js'

export default {
  name: 'ReviewModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    task: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      rating: 0,
      hoverRating: 0,
      comment: '',
      isSubmitting: false
    }
  },
  computed: {
    isVisible() {
      return this.visible
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.resetForm()
        this.checkExistingReview()
      }
    }
  },
  methods: {
    setRating(rating) {
      this.rating = rating
    },
    setHoverRating(rating) {
      this.hoverRating = rating
    },
    getRatingText(rating) {
      const texts = {
        0: '请选择评分',
        1: '很差',
        2: '一般',
        3: '良好',
        4: '很好',
        5: '优秀'
      }
      return texts[rating] || ''
    },
    resetForm() {
      this.rating = 0
      this.hoverRating = 0
      this.comment = ''
      this.isSubmitting = false
    },
    async checkExistingReview() {
      try {
        const existingReview = await reviewAPI.getTaskReview(this.task.id)
        if (existingReview) {
          this.rating = existingReview.rating
          this.comment = existingReview.comment || ''
        }
      } catch (error) {
        // If no existing review found, continue to show blank form
        console.log('No existing review found')
      }
    },
    async submitReview() {
      if (!this.rating || this.isSubmitting) return

      this.isSubmitting = true
      try {
        // 使用新的API接口，传递order_id而不是task_id
        await reviewAPI.submitReview(this.task.id, {
          rating: this.rating,
          comment: this.comment
        })
        
        this.$emit('review-submitted', {
          taskId: this.task.id,
          rating: this.rating,
          comment: this.comment
        })
        
        this.closeModal()
        this.$emit('success', '评价提交成功！')
      } catch (error) {
        console.error('Failed to submit review:', error)
        this.$emit('error', '评价提交失败，请稍后重试')
      } finally {
        this.isSubmitting = false
      }
    },
    closeModal() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.review-modal-overlay {
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
  padding: 20px;
}

.review-modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #333;
}

.modal-content {
  padding: 24px;
}

.task-info {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #00b894;
}

.task-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.task-meta {
  display: flex;
  gap: 16px;
  margin: 0;
  color: #666;
  font-size: 14px;
}

.price {
  color: #00b894;
  font-weight: 600;
}

.rating-section {
  margin-bottom: 24px;
}

.rating-label {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.star-rating {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  color: #ddd;
}

.star-btn:hover {
  background: #f8f9fa;
}

.star-btn.active,
.star-btn.hover {
  color: #ffc107;
}

.star-btn svg {
  transition: all 0.2s ease;
}

.rating-text {
  font-size: 14px;
  color: #666;
  margin: 0;
  min-height: 20px;
}

.comment-section {
  margin-bottom: 24px;
}

.comment-label {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.comment-textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s ease;
}

.comment-textarea:focus {
  outline: none;
  border-color: #00b894;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn,
.submit-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
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

.submit-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
}

.submit-btn:hover:not(.disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
}

.submit-btn.disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .review-modal-overlay {
    padding: 10px;
  }
  
  .modal-header {
    padding: 16px 20px;
  }
  
  .modal-content {
    padding: 20px;
  }
  
  .star-rating {
    gap: 4px;
  }
  
  .star-btn svg {
    width: 28px;
    height: 28px;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .cancel-btn,
  .submit-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
