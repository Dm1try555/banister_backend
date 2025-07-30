<template>
  <div class="profile-page">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-8">Profile Settings</h1>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Profile Photo Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold mb-4">Profile Photo</h2>
          
          <ProfilePhotoUploader
            :current-photo-url="user?.profile_photo_url"
            :is-required="isPhotoRequired"
            @photo-uploaded="handlePhotoUploaded"
            @photo-error="handlePhotoError"
          />
          
          <!-- Photo Requirements Info -->
          <div v-if="isPhotoRequired" class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p class="text-sm text-blue-800">
              <strong>Note:</strong> Profile photo is required for {{ user?.role }} accounts.
            </p>
          </div>
        </div>
        
        <!-- Profile Information Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold mb-4">Profile Information</h2>
          
          <form @submit.prevent="updateProfile" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                v-model="profileForm.email"
                type="email"
                disabled
                class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                First Name
              </label>
              <input
                v-model="profileForm.first_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Last Name
              </label>
              <input
                v-model="profileForm.last_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <input
                v-model="profileForm.phone"
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Role
              </label>
              <input
                :value="user?.role"
                type="text"
                disabled
                class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 capitalize"
              />
            </div>
            
            <button
              type="submit"
              :disabled="isUpdating"
              class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ isUpdating ? 'Updating...' : 'Update Profile' }}
            </button>
          </form>
        </div>
      </div>
      
      <!-- Status Messages -->
      <div v-if="message" class="mt-4 p-4 rounded-md" :class="messageClass">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Page metadata
definePageMeta({
  middleware: 'auth'
})

// Reactive data
const user = ref(null)
const isUpdating = ref(false)
const message = ref('')
const messageType = ref('success')

const profileForm = ref({
  email: '',
  first_name: '',
  last_name: '',
  phone: ''
})

// Computed properties
const isPhotoRequired = computed(() => {
  return user.value?.role === 'admin' || user.value?.role === 'provider'
})

const messageClass = computed(() => {
  return messageType.value === 'success' 
    ? 'bg-green-50 border border-green-200 text-green-800'
    : 'bg-red-50 border border-red-200 text-red-800'
})

// Methods
const fetchUserProfile = async () => {
  try {
    const response = await $fetch('/api/authentication/profile/', {
      headers: {
        'Authorization': `Bearer ${useCookie('access_token').value}`
      }
    })
    
    if (response.success) {
      user.value = response.data
      profileForm.value = {
        email: response.data.email,
        first_name: response.data.profile?.first_name || '',
        last_name: response.data.profile?.last_name || '',
        phone: response.data.phone || ''
      }
    }
  } catch (error) {
    console.error('Error fetching profile:', error)
    showMessage('Failed to load profile information', 'error')
  }
}

const updateProfile = async () => {
  isUpdating.value = true
  
  try {
    const response = await $fetch('/api/authentication/profile/', {
      method: 'PUT',
      body: {
        profile: {
          first_name: profileForm.value.first_name,
          last_name: profileForm.value.last_name
        },
        phone: profileForm.value.phone
      },
      headers: {
        'Authorization': `Bearer ${useCookie('access_token').value}`
      }
    })
    
    if (response.success) {
      showMessage('Profile updated successfully!', 'success')
      await fetchUserProfile() // Refresh data
    }
  } catch (error) {
    console.error('Error updating profile:', error)
    const errorMessage = error.data?.error?.error_message || 'Failed to update profile'
    showMessage(errorMessage, 'error')
  } finally {
    isUpdating.value = false
  }
}

const handlePhotoUploaded = (photoData) => {
  showMessage('Profile photo updated successfully!', 'success')
  // Update user data with new photo URL
  if (user.value) {
    user.value.profile_photo_url = photoData.photo_url
  }
}

const handlePhotoError = (error) => {
  showMessage(error, 'error')
}

const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  
  // Clear message after 5 seconds
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

// Lifecycle
onMounted(() => {
  fetchUserProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #f9fafb;
}
</style> 