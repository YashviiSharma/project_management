<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Navigation Bar -->
    <NavBar :userName="userName" />

    <!-- Main Content -->
    <main class="flex-grow container mx-auto px-4 py-6">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-medium text-gray-700">Active Projects</h3>
          <p class="text-3xl font-bold text-blue-600 mt-2">{{ stats.active_projects || 0 }}</p>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-medium text-gray-700">Pending Deliverables</h3>
          <p class="text-3xl font-bold text-yellow-600 mt-2">{{ stats.pending_deliverables || 0 }}</p>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-medium text-gray-700">Completed Projects</h3>
          <p class="text-3xl font-bold text-green-600 mt-2">{{ stats.completed_projects || 0 }}</p>
        </div>
      </div>
      
      <!-- Recent Projects Section -->
      <div class="bg-white rounded-lg shadow p-6 mb-8">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold text-gray-700">Recent Projects</h2>
          <button 
            @click="goToNewProject"
            class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
          >
            Propose New Project
          </button>
        </div>
        
        <div v-if="loadingProjects" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          <p class="mt-2 text-gray-600">Loading projects...</p>
        </div>
        
        <div v-else-if="projects.length === 0" class="text-center py-8">
          <p class="text-gray-600">No projects found. You can propose a new project.</p>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="project in projects" :key="project.name" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="font-medium text-gray-900">{{ project.project_name }}</div>
                  <div class="text-sm text-gray-500">{{ project.project_type }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusClass(project.status)}`">
                    {{ project.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      :class="`h-2.5 rounded-full ${getProgressColor(project.progress)}`" 
                      :style="`width: ${project.progress || 0}%`"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-600">{{ project.progress || 0 }}%</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="`${isOverdue(project.end_date) ? 'text-red-600' : 'text-gray-600'}`">
                    {{ formatDate(project.end_date) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button 
                    @click.stop="viewProject(project.name)"
                    class="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    View
                  </button>
                  <button 
                    @click.stop="openProjectChat(project.name)"
                    class="text-green-600 hover:text-green-900"
                    v-if="project.raven_channel"
                  >
                    Chat
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Pending Deliverables Section -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-700 mb-4">Pending Deliverables</h2>
        
        <div v-if="loadingDeliverables" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          <p class="mt-2 text-gray-600">Loading deliverables...</p>
        </div>
        
        <div v-else-if="awaitingReviewDeliverables.length === 0" class="text-center py-8">
          <p class="text-gray-600">No pending deliverables requiring your review.</p>
        </div>
        
        <div v-else class="space-y-4">
          <div 
            v-for="deliverable in awaitingReviewDeliverables" 
            :key="deliverable.name"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
          >
            <div class="flex justify-between items-start">
              <div>
                <h3 class="font-medium text-lg text-gray-800">{{ deliverable.deliverable_name }}</h3>
                <p class="text-sm text-gray-600">Project: {{ getProjectName(deliverable.project) }}</p>
              </div>
              <span :class="`px-2 py-1 text-xs font-medium rounded ${getDeliverableStatusClass(deliverable.status)}`">
                {{ deliverable.status }}
              </span>
            </div>
            
            <div class="mt-3 flex items-center justify-between">
              <div>
                <span class="text-sm text-gray-600">Due: </span>
                <span :class="`text-sm ${isOverdue(deliverable.due_date) ? 'text-red-600' : 'text-gray-600'}`">
                  {{ formatDate(deliverable.due_date) }}
                </span>
              </div>
              
              <div class="space-x-2">
                <button 
                  @click="viewDeliverable(deliverable.name)"
                  class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  View
                </button>
                <button 
                  @click="downloadDeliverable(deliverable)"
                  class="text-green-600 hover:text-green-800 text-sm font-medium"
                  v-if="deliverable.document"
                >
                  Download
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <FooterComponent />
  </div>
</template>

<script>
import { session } from '@/data/session.js'
import NavBar from '@/components/NavBar.vue'
import FooterComponent from '@/components/Footer.vue'

export default {
  name: 'ClientDashboard',
  components: {
    NavBar,
    FooterComponent
  },
  data() {
    return {
      session,
      userName: '',
      userEmail: '',
      projects: [],
      deliverables: [],
      stats: {},
      loadingProjects: true,
      loadingDeliverables: true
    };
  },
  computed: {
    // Filtered deliverables for dashboard that only show "Awaiting Client Review" status
    awaitingReviewDeliverables() {
      return this.deliverables.filter(d => d.status === 'Awaiting Client Review');
    }
  },
  async mounted() {
    await this.getUserInfo();
    await this.fetchClientProjects();
    await this.fetchPendingDeliverables();
    await this.fetchDashboardStats();
  },
  methods: {
    // Format date for display
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const options = { year: 'numeric', month: 'short', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    // Check if date is overdue
    isOverdue(dateString) {
      if (!dateString) return false;
      return new Date(dateString) < new Date();
    },
    
    // Get project status class
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
    
    // Get deliverable status class
    getDeliverableStatusClass(status) {
      switch(status) {
        case 'In Progress': return 'bg-blue-100 text-blue-800';
        case 'Awaiting Client Review': return 'bg-purple-100 text-purple-800';
        case 'Required Changes': return 'bg-yellow-100 text-yellow-800';
        case 'Approved': return 'bg-green-100 text-green-800';
        case 'Rejected': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    },
    
    // Get progress bar color based on percentage
    getProgressColor(progress) {
      progress = progress || 0;
      if (progress < 30) return 'bg-red-500';
      if (progress < 70) return 'bg-yellow-500';
      return 'bg-green-500';
    },
    
    // Get project name from project reference
    getProjectName(projectId) {
      const project = this.projects.find(p => p.name === projectId);
      return project ? project.project_name : projectId;
    },
    
    // Navigation methods
    viewProject(projectId) {
      this.$router.push(`/client/projects/${projectId}`);
    },
    
    viewDeliverable(deliverableId) {
      this.$router.push(`/client/deliverables`);
    },
    
    openProjectChat(projectId) {
      const project = this.projects.find(p => p.name === projectId);
      if (project?.raven_channel) {
        const workspace_name = project.raven_channel.split('-')[0];
        window.open(`/raven/${encodeURIComponent(workspace_name)}/${encodeURIComponent(project.raven_channel)}`, '_blank');
      }
    },
    
    downloadDeliverable(deliverable) {
      if (deliverable.document) {
        window.open(deliverable.document, '_blank');
      }
    },
    
    goToNewProject() {
      window.location.replace(window.location.origin + '/propose-your-idea/new');
    },
    
    // Get user information
    async getUserInfo() {
      try {
        // Get logged in user email
        const userResponse = await fetch('/api/method/frappe.auth.get_logged_user');
        if (!userResponse.ok) throw new Error('Failed to get user email');
        const userData = await userResponse.json();
        this.userEmail = userData.message;
        
        // Get user full name
        const profileResponse = await fetch(`/api/resource/User/${userData.message}`);
        if (!profileResponse.ok) throw new Error('Failed to get user profile');
        const profile = await profileResponse.json();
        
        this.userName = profile.data.full_name || userData.message;
      } catch (error) {
        console.error('Error fetching user info:', error);
      }
    },
    
    // Fetch client projects - use a custom method instead of direct API call
    async fetchClientProjects() {
      try {
        this.loadingProjects = true;
        
        // Use a server-side method that has proper permissions
        const response = await fetch('/api/method/project_management.api.get_client_projects');
        
        if (!response.ok) throw new Error('Failed to fetch projects');
        
        const data = await response.json();
        this.projects = data.message || [];        
        
      } catch (error) {
        console.error('Error fetching projects:', error);
      } finally {
        this.loadingProjects = false;
      }
    },
    
    // Fetch pending deliverables
    async fetchPendingDeliverables() {
      try {
        this.loadingDeliverables = true;
        
        if (this.projects.length === 0) {
          this.deliverables = [];
          return;
        }
        
        const projectNames = this.projects.map(p => p.name);
        
        // Use a server-side method instead of direct API call
        const response = await fetch('/api/method/project_management.api.get_client_deliverables', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            projects: projectNames
          })
        });
        
        if (!response.ok) throw new Error('Failed to fetch deliverables');
        
        const data = await response.json();
        this.deliverables = data.message || [];
      } catch (error) {
        console.error('Error fetching deliverables:', error);
      } finally {
        this.loadingDeliverables = false;
      }
    },
    
    // Fetch dashboard statistics
    async fetchDashboardStats() {
      try {
        if (!this.userEmail) {
          return;
        }
        
        // Get project names first
        const projectNames = this.projects.map(p => p.name);
        
        if (projectNames.length === 0) {
          this.stats = {
            active_projects: 0,
            pending_deliverables: 0,
            completed_projects: 0
          };
          return;
        }
        
        // Use a server-side method instead of multiple API calls
        const response = await fetch('/api/method/project_management.api.get_client_dashboard_stats', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            projects: projectNames
          })
        });
        
        if (!response.ok) throw new Error('Failed to fetch dashboard stats');
        
        const data = await response.json();
        this.stats = data.message || {
          active_projects: 0,
          pending_deliverables: 0,
          completed_projects: 0
        };
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      }
    }
  }
};
</script>