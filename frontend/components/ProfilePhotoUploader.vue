<template>
  <div class="profile-photo-uploader">
    <!-- Current Profile Photo Display -->
    <div class="current-photo" v-if="currentPhotoUrl">
      <img :src="currentPhotoUrl" alt="Current profile photo" class="profile-image" />
    </div>
    
    <!-- Upload Area -->
    <div class="upload-area" @click="triggerFileInput" @drop="handleDrop" @dragover.prevent>
      <div v-if="!previewImage" class="upload-placeholder">
        <div class="upload-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7,10 12,15 17,10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
        </div>
        <p class="upload-text">Click to upload or drag and drop</p>
        <p class="upload-hint">JPG, PNG, GIF up to 5MB</p>
      </div>
      
      <!-- Preview Image -->
      <div v-else class="preview-container">
        <img :src="previewImage" alt="Preview" class="preview-image" />
        <div class="preview-overlay">
          <button @click.stop="confirmUpload" class="confirm-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20,6 9,17 4,12" />
            </svg>
            Confirm
          </button>
          <button @click.stop="cancelUpload" class="cancel-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
            Cancel
          </button>
        </div>
      </div>
    </div>
    
    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      @change="handleFileSelect"
      class="hidden-input"
    />
    
    <!-- Loading State -->
    <div v-if="isUploading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Uploading photo...</p>
    </div>
    
    <!-- Error Message -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  currentPhotoUrl: {
    type: String,
    default: null
  },
  isRequired: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['photo-uploaded', 'photo-error'])

const fileInput = ref(null)
const previewImage = ref(null)
const selectedFile = ref(null)
const isUploading = ref(false)
const error = ref('')
const successMessage = ref('')

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndPreviewFile(file)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndPreviewFile(file)
  }
}

const validateAndPreviewFile = (file) => {
  // Reset states
  error.value = ''
  successMessage.value = ''
  
  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    error.value = 'Please select a valid image file (JPG, PNG, GIF)'
    return
  }
  
  // Validate file size (5MB)
  const maxSize = 5 * 1024 * 1024 // 5MB in bytes
  if (file.size > maxSize) {
    error.value = 'File size must not exceed 5MB'
    return
  }
  
  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    previewImage.value = e.target.result
    selectedFile.value = file
  }
  reader.readAsDataURL(file)
}

const confirmUpload = async () => {
  if (!selectedFile.value) return
  
  isUploading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('photo', selectedFile.value)
    
    const response = await $fetch('/api/file-storage/profile-photo/quick-change/', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${useCookie('access_token').value}`
      }
    })
    
    if (response.success) {
      successMessage.value = 'Profile photo updated successfully!'
      previewImage.value = null
      selectedFile.value = null
      emit('photo-uploaded', response.data)
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    }
  } catch (err) {
    console.error('Upload error:', err)
    error.value = err.data?.error?.error_message || 'Failed to upload photo. Please try again.'
    emit('photo-error', error.value)
  } finally {
    isUploading.value = false
  }
}

const cancelUpload = () => {
  previewImage.value = null
  selectedFile.value = null
  error.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

onMounted(() => {
  // Show warning if photo is required but not set
  if (props.isRequired && !props.currentPhotoUrl) {
    error.value = 'Profile photo is required for your role'
  }
})
</script>

<style scoped>
.profile-photo-uploader {
  position: relative;
  max-width: 300px;
  margin: 0 auto;
}

.current-photo {
  margin-bottom: 1rem;
  text-align: center;
}

.profile-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e5e7eb;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f9fafb;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.upload-icon {
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.upload-text {
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.upload-hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.preview-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.preview-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  border-radius: 8px;
}

.confirm-btn, .cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.confirm-btn {
  background: #10b981;
  color: white;
}

.confirm-btn:hover {
  background: #059669;
}

.cancel-btn {
  background: #ef4444;
  color: white;
}

.cancel-btn:hover {
  background: #dc2626;
}

.hidden-input {
  display: none;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 0.875rem;
}

.success-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  color: #16a34a;
  font-size: 0.875rem;
}
</style> 