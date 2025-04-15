<template>
  <nav class="bg-blue-600 text-white shadow-lg">
    <div class="container mx-auto px-4 py-3 flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <img src="/logo.png" alt="Logo" class="h-8">
        <span class="text-xl font-semibold">Project Management Portal</span>
      </div>
      
      <div class="hidden md:flex space-x-6">
        <router-link to="/client/dashboard" class="hover:text-blue-200">Dashboard</router-link>
        <router-link to="/client/projects" class="hover:text-blue-200">My Projects</router-link>
        <router-link to="/client/deliverables" class="hover:text-blue-200">Deliverables</router-link>
        <router-link to="/client/team" class="hover:text-blue-200">Team Members</router-link>
      </div>
      
      <div class="flex items-center space-x-4">
        <button 
          @click="openInviteModal" 
          class="bg-green-600 hover:bg-green-700 px-3 py-1 rounded"
        >
          Invite
        </button>
        <span class="hidden sm:inline">Welcome, {{ userName }}</span>
        <button @click="logout" class="bg-blue-700 hover:bg-blue-800 px-3 py-1 rounded">
          Logout
        </button>
      </div>
    </div>

    <!-- Invite Modal -->
    <div v-if="showInviteModal" class="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-md p-6 text-gray-800">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-semibold text-gray-700">Invite to Your Dashboard</h3>
          <button @click="closeInviteModal" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <p class="mb-4 text-gray-600">
          Invite someone to access your dashboard. They'll be able to see all projects, deliverables, and team members you have access to.
        </p>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
          <input 
            v-model="inviteEmail" 
            type="email" 
            placeholder="Enter email address" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-1">Role</label>
          <select 
            v-model="inviteRole" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="Guest">Guest (View only)</option>
            <option value="Client">Client (Same permissions as you)</option>
          </select>
        </div>
        
        <div class="flex justify-end space-x-3">
          <button 
            @click="closeInviteModal" 
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button 
            @click="sendInvitation" 
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Sending...
            </span>
            <span v-else>Send Invitation</span>
          </button>
        </div>
        
        <!-- Notification -->
        <div v-if="notification" :class="`mt-4 p-3 rounded-md ${notification.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`">
          {{ notification.message }}
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { session } from '@/data/session.js'

export default {
  name: 'NavBar',
  props: {
    userName: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      session,
      showInviteModal: false,
      inviteEmail: '',
      inviteRole: 'Guest',
      isLoading: false,
      notification: null
    }
  },
  methods: {
    logout() {
      this.session.logout.submit().then(() => {
        this.$router.push('/account/login');
      });
    },
    openInviteModal() {
      this.showInviteModal = true;
      this.inviteEmail = '';
      this.inviteRole = 'Guest';
      this.notification = null;
    },
    closeInviteModal() {
      this.showInviteModal = false;
    },
    async sendInvitation() {
      if (!this.inviteEmail) {
        this.notification = {
          type: 'error',
          message: 'Please enter an email address'
        };
        return;
      }
      
      this.isLoading = true;
      
      try {
        const response = await fetch('/api/method/project_management.api.invite_by_email', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            emails: this.inviteEmail,
            role: this.inviteRole
          })
        });
        
        const result = await response.json();
        
        if (result.message.status === 'success') {
          this.notification = {
            type: 'success',
            message: result.message.message
          };
          
          // Clear the form after successful invitation
          this.inviteEmail = '';
          
          // Close the modal after 2 seconds
          setTimeout(() => {
            this.closeInviteModal();
          }, 5000);
        } else {
          this.notification = {
            type: 'error',
            message: result.message.message || 'Failed to send invitation'
          };
        }
      } catch (error) {
        console.error('Error sending invitation:', error);
        this.notification = {
          type: 'error',
          message: 'An error occurred while sending the invitation'
        };
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.router-link-active {
  @apply text-blue-300 font-medium;
}
</style>