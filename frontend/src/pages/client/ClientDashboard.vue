<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <!-- Navigation Bar -->
    <nav class="bg-blue-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-3 flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <img src="../assets/logo.png" alt="Logo" class="h-8">
          <span class="text-xl font-semibold">Project Management</span>
        </div>
        
        <div class="hidden md:flex space-x-6">
          <router-link to="/client/dashboard" class="hover:text-blue-200">Dashboard</router-link>
          <router-link to="/client/projects" class="hover:text-blue-200">My Projects</router-link>
          <router-link to="/client/messages" class="hover:text-blue-200">Messages</router-link>
          <router-link to="/client/settings" class="hover:text-blue-200">Settings</router-link>
        </div>
        
        <div class="flex items-center space-x-4">
          <span class="hidden sm:inline">Welcome, {{ userName }}</span>
          <button @click="logout" class="bg-blue-700 hover:bg-blue-800 px-3 py-1 rounded">
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-grow container mx-auto px-4 py-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Client Dashboard</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Stats Cards -->
          <div class="bg-blue-50 p-4 rounded-lg border border-blue-100">
            <h3 class="text-lg font-medium text-blue-800">Active Projects</h3>
            <p class="text-3xl font-bold text-blue-600 mt-2">{{ activeProjects }}</p>
          </div>
          
          <div class="bg-green-50 p-4 rounded-lg border border-green-100">
            <h3 class="text-lg font-medium text-green-800">Completed Projects</h3>
            <p class="text-3xl font-bold text-green-600 mt-2">{{ completedProjects }}</p>
          </div>
          
          <div class="bg-purple-50 p-4 rounded-lg border border-purple-100">
            <h3 class="text-lg font-medium text-purple-800">Pending Tasks</h3>
            <p class="text-3xl font-bold text-purple-600 mt-2">{{ pendingTasks }}</p>
          </div>
        </div>
        
        <!-- Recent Projects Section -->
        <div class="mt-8">
          <h2 class="text-xl font-semibold text-gray-700 mb-4">Recent Projects</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="project in recentProjects" :key="project.id">
                  <td class="px-6 py-4 whitespace-nowrap">{{ project.name }}</td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusClass(project.status)}`">
                      {{ project.status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">{{ project.due_date }}</td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <button @click="viewProject(project.id)" class="text-blue-600 hover:text-blue-900 mr-3">View</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-6">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="mb-4 md:mb-0">
            <p>&copy; {{ currentYear }} Project Management System. All rights reserved.</p>
          </div>
          <div class="flex space-x-4">
            <a href="#" class="hover:text-blue-300">Terms of Service</a>
            <a href="#" class="hover:text-blue-300">Privacy Policy</a>
            <a href="#" class="hover:text-blue-300">Contact Us</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'ClientDashboard',
  setup() {
    const router = useRouter();
    
    // Sample data - replace with actual API calls
    const userName = ref('John Doe');
    const activeProjects = ref(3);
    const completedProjects = ref(5);
    const pendingTasks = ref(12);
    const currentYear = ref(new Date().getFullYear());
    
    const recentProjects = ref([
      { id: 1, name: 'Website Redesign', status: 'In Progress', due_date: '2023-12-15' },
      { id: 2, name: 'Mobile App Development', status: 'Pending', due_date: '2024-01-20' },
      { id: 3, name: 'Marketing Campaign', status: 'Completed', due_date: '2023-11-10' },
    ]);
    
    const getStatusClass = (status) => {
      switch(status) {
        case 'In Progress': return 'bg-yellow-100 text-yellow-800';
        case 'Pending': return 'bg-red-100 text-red-800';
        case 'Completed': return 'bg-green-100 text-green-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    };
    
    const viewProject = (projectId) => {
      router.push(`/client/projects/${projectId}`);
    };
    
    const logout = () => {
      // Implement logout logic
      router.push('/login');
    };
    
    // Fetch actual data when component mounts
    onMounted(() => {
      // fetchClientData();
    });
    
    return {
      userName,
      activeProjects,
      completedProjects,
      pendingTasks,
      currentYear,
      recentProjects,
      getStatusClass,
      viewProject,
      logout
    };
  }
};
</script>

<style scoped>
/* Add any custom styles here */
</style>