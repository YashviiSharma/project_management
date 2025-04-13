<template>
  <nav class="bg-blue-600 text-white py-4 px-6 flex justify-between items-center shadow-md">
    <h1 class="text-xl font-bold">Vendor Portal</h1>

    <ul class="flex space-x-6">
    <li><router-link to="/vendor/dashboard" class="hover:underline">Dashboard</router-link></li>
    <li><router-link to="/vendor/tasks" class="hover:underline">Tasks</router-link></li>
    <li><router-link to="/vendor/deliverables" class="hover:underline">Deliverables</router-link></li>
  </ul>

    <div class="flex items-center space-x-4">
      <span class="italic text-sm text-white">Hi, {{ userName }}</span>
      <button @click="logout" class="bg-red-500 px-4 py-2 rounded hover:bg-red-700">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const userName = ref('Loading...');

const getCurrentUser = async () => {
  try {
    // Step 1: Get the logged in user email
    const res = await fetch('/api/method/frappe.auth.get_logged_user');
    const data = await res.json();
    const email = data.message;

    // Step 2: Fetch full user details (optional)
    const userDetails = await fetch(`/api/resource/User/${email}`);
    const userInfo = await userDetails.json();

    userName.value = userInfo.data.full_name || email;
  } catch (err) {
    console.error('Failed to fetch user info:', err);
    userName.value = 'Guest';
  }
};

const logout = () => {
  fetch('/api/method/logout', { method: 'GET' }).then(() => {
    window.location.href = '/login'; 
  });
};

onMounted(() => {
  getCurrentUser();
});
</script>
