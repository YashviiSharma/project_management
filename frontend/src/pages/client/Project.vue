<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Use the NavBar component -->
    <NavBar :userName="userName" />

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-gray-800">My Projects</h1>
        <button 
          @click="goToNewProject"
          class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
        >
          Propose New Project
        </button>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
        <p class="mt-3 text-gray-600">Loading projects...</p>
      </div>

      <div v-else-if="projects.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-600 mb-4">You don't have any projects yet.</p>
        <button 
          @click="goToNewProject"
          class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
        >
          Propose Your First Project
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="project in projects" 
          :key="project.name"
          class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition"
        >
          <div class="p-6">
            <div class="flex justify-between items-start">
              <div>
                <h2 class="text-xl font-bold text-gray-800 mb-1">{{ project.project_name }}</h2>
                <p class="text-sm text-gray-500">{{ project.project_type }}</p>
              </div>
              <span :class="`px-2 py-1 text-xs font-semibold rounded ${getStatusClass(project.status)}`">
                {{ project.status }}
              </span>
            </div>

            <div class="mt-4">
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>Start Date</span>
                <span>{{ formatDate(project.start_date) }}</span>
              </div>
              <div class="flex justify-between text-sm text-gray-600">
                <span>End Date</span>
                <span :class="`${isOverdue(project.end_date) ? 'text-red-600' : ''}`">
                  {{ formatDate(project.end_date) }}
                </span>
              </div>
            </div>

            <div class="mt-4">
              <p class="text-sm text-gray-600 mb-2">Progress</p>
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  :class="`h-2.5 rounded-full ${getProgressColor(project.progress)}`"
                  :style="`width: ${project.progress || 0}%`"
                ></div>
              </div>
              <div class="flex justify-between mt-1">
                <span class="text-xs text-gray-500">{{ project.progress || 0 }}% complete</span>
                <span class="text-xs text-gray-500">{{ getDaysRemaining(project.end_date) }}</span>
              </div>
            </div>

            <div class="mt-6 flex justify-between">
              <button 
                @click="viewProject(project.name)"
                class="text-blue-600 hover:text-blue-800 font-medium text-sm"
              >
                View Details
              </button>
              <button 
                @click="openProjectChat(project.name)"
                class="text-green-600 hover:text-green-800 font-medium text-sm"
                v-if="project.raven_channel"
              >
                Project Chat
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Use the Footer component -->
    <FooterComponent />
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import FooterComponent from '@/components/Footer.vue';

export default {
  name: 'ClientProjects',
  components: {
    NavBar,
    FooterComponent
  },
  data() {
    return {
      userName: '',
      projects: [],
      loading: true
    }
  },
  async mounted() {
    await this.getUserInfo();
    await this.fetchClientProjects();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    isOverdue(dateString) {
      if (!dateString) return false;
      return new Date(dateString) < new Date();
    },
    
    getStatusClass(status) {
      switch(status) {
        case 'In Progress': return 'bg-blue-100 text-blue-800';
        case 'Completed': return 'bg-green-100 text-green-800';
        case 'On Hold': return 'bg-yellow-100 text-yellow-800';
        case 'Cancelled': return 'bg-red-100 text-red-800';
        case 'Planned': return 'bg-purple-100 text-purple-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    },
    
    getProgressColor(progress) {
      progress = progress || 0;
      if (progress < 30) return 'bg-red-500';
      if (progress < 70) return 'bg-yellow-500';
      return 'bg-green-500';
    },
    
    getDaysRemaining(endDate) {
      if (!endDate) return '';
      const today = new Date();
      const end = new Date(endDate);
      const diffTime = end - today;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) return `${Math.abs(diffDays)} days overdue`;
      if (diffDays === 0) return 'Due today';
      return `${diffDays} days remaining`;
    },
    
    async getUserInfo() {
      try {
        const userResponse = await fetch('/api/method/frappe.auth.get_logged_user');
        if (!userResponse.ok) throw new Error('Failed to get user email');
        const userData = await userResponse.json();
        
        const profileResponse = await fetch(`/api/resource/User/${userData.message}`);
        if (!profileResponse.ok) throw new Error('Failed to get user profile');
        const profile = await profileResponse.json();
        
        this.userName = profile.data.full_name || userData.message;
      } catch (error) {
        console.error('Error fetching user info:', error);
      }
    },
    
    async fetchClientProjects() {
      try {
        this.loading = true;
        const response = await fetch('/api/method/project_management.api.get_client_projects');
        
        if (!response.ok) throw new Error('Failed to fetch projects');
        
        const data = await response.json();
        this.projects = data.message || [];
      } catch (error) {
        console.error('Error fetching projects:', error);
      } finally {
        this.loading = false;
      }
    },
    
    viewProject(projectId) {
      this.$router.push(`/client/projects/${projectId}`);
    },
    
    openProjectChat(projectId) {
      const project = this.projects.find(p => p.name === projectId);
      if (project?.raven_channel) {
        const workspace_name = project.raven_channel.split('-')[0];
        window.open(`/raven/${encodeURIComponent(workspace_name)}/${encodeURIComponent(project.raven_channel)}`, '_blank');
      }
    },
    
    goToNewProject() {
      this.$router.push('/client/projects/new');
    }
  }
}
</script>