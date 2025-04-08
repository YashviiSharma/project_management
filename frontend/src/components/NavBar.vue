<template>
    <nav class="bg-blue-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-3 flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <img src="../assets/logo.png" alt="Logo" class="h-8">
          <span class="text-xl font-semibold">Project Management Portal</span>
        </div>
        
        <div class="hidden md:flex space-x-6">
          <router-link to="/client/dashboard" class="hover:text-blue-200">Dashboard</router-link>
          <router-link to="/client/projects" class="hover:text-blue-200">My Projects</router-link>
          <router-link to="/client/deliverables" class="hover:text-blue-200">Deliverables</router-link>
          <router-link to="/client/team" class="hover:text-blue-200">Team Members</router-link>
        </div>
        
        <div class="flex items-center space-x-4">
          <span class="hidden sm:inline">Welcome, {{ userName }}</span>
          <button @click="logout" class="bg-blue-700 hover:bg-blue-800 px-3 py-1 rounded">
            Logout
          </button>
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
        session
      }
    },
    methods: {
      logout() {
        this.session.logout.submit().then(() => {
          this.$router.push('/account/login');
        });
      }
    }
  }
  </script>
  
  <style scoped>
  .router-link-active {
    @apply text-blue-300 font-medium;
  }
  </style>