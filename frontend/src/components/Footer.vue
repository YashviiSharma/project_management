<template>
    <footer class="bg-gray-800 text-white py-6">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="mb-4 md:mb-0">
            <p>&copy; {{ currentYear }} Project Management System. All rights reserved.</p>
          </div>
          <div class="flex space-x-4">
            <router-link to="/client/terms" class="hover:text-blue-300">Terms</router-link>
            <router-link to="/client/privacy" class="hover:text-blue-300">Privacy</router-link>
            <router-link to="/client/contact" class="hover:text-blue-300">Contact</router-link>
          </div>
        </div>
      </div>
    </footer>
  </template>
  
  <script>
  export default {
    name: 'FooterComponent',
    data() {
      return {
        currentYear: new Date().getFullYear()
      }
    }
  }
  </script>