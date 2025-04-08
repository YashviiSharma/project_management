<template>
    <div class="min-h-screen bg-gray-50">
      <!-- Navigation Bar -->
      <nav-bar :userName="userName"></nav-bar>
  
      <!-- Main Content -->
      <main class="container mx-auto px-4 py-8">
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
          <p class="mt-3 text-gray-600">Loading project details...</p>
        </div>
  
        <div v-else-if="!project" class="text-center py-12 bg-white rounded-lg shadow">
          <p class="text-gray-600 mb-4">Project not found or you don't have access to this project.</p>
          <button 
            @click="goToProjects"
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
          >
            Back to Projects
          </button>
        </div>
  
        <div v-else>
          <!-- Project Header -->
          <div class="flex justify-between items-start mb-6">
            <div>
              <div class="flex items-center">
                <h1 class="text-2xl font-bold text-gray-800">{{ project.project_name }}</h1>
                <span 
                  :class="`ml-4 px-3 py-1 text-sm font-semibold rounded ${getStatusClass(project.status)}`"
                >
                  {{ project.status }}
                </span>
              </div>
              <p class="text-gray-600 mt-1">{{ project.project_type }}</p>
            </div>
            
            <div class="flex space-x-3">
              <button 
                v-if="project.raven_channel"
                @click="openProjectChat"
                class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded flex items-center"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
                Project Chat
              </button>
              <button 
                @click="goToProjects"
                class="border border-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-50"
              >
                Back to Projects
              </button>
            </div>
          </div>
  
          <!-- Project Overview -->
          <div class="bg-white rounded-lg shadow mb-6">
            <div class="p-6">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">Project Overview</h2>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <dl class="space-y-4">
                    <div>
                      <dt class="text-sm font-medium text-gray-500">Project ID</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ project.name }}</dd>
                    </div>
                    <div>
                      <dt class="text-sm font-medium text-gray-500">Start Date</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ formatDate(project.start_date) }}</dd>
                    </div>
                    <div>
                      <dt class="text-sm font-medium text-gray-500">End Date</dt>
                      <dd 
                        class="mt-1 text-sm" 
                        :class="isOverdue(project.end_date) ? 'text-red-600 font-medium' : 'text-gray-900'"
                      >
                        {{ formatDate(project.end_date) }}
                        <span v-if="getDaysRemaining(project.end_date)" class="ml-2 text-xs">
                          ({{ getDaysRemaining(project.end_date) }})
                        </span>
                      </dd>
                    </div>
                  </dl>
                </div>
                
                <div>
                  <dl class="space-y-4">
                    <div>
                      <dt class="text-sm font-medium text-gray-500">Progress</dt>
                      <dd class="mt-1">
                        <div class="w-full bg-gray-200 rounded-full h-2.5">
                          <div 
                            :class="`h-2.5 rounded-full ${getProgressColor(project.progress)}`"
                            :style="`width: ${project.progress || 0}%`"
                          ></div>
                        </div>
                        <span class="text-sm text-gray-600 mt-1 inline-block">{{ project.progress || 0 }}% complete</span>
                      </dd>
                    </div>
                    <div>
                      <dt class="text-sm font-medium text-gray-500">Priority</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ project.priority || 'Medium' }}</dd>
                    </div>
                    <div>
                      <dt class="text-sm font-medium text-gray-500">Department</dt>
                      <dd class="mt-1 text-sm text-gray-900">{{ project.department || 'N/A' }}</dd>
                    </div>
                  </dl>
                </div>
              </div>
              
              <div class="mt-6">
                <h3 class="text-sm font-medium text-gray-500">Description</h3>
                <div class="mt-1 text-sm text-gray-900 prose max-w-none">
                  <div v-if="project.description" v-html="project.description"></div>
                  <p v-else>No description available.</p>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Project Deliverables -->
          <div class="bg-white rounded-lg shadow mb-6">
            <div class="p-6">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">Project Deliverables</h2>
              
              <div v-if="loadingDeliverables" class="text-center py-6">
                <div class="inline-block animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
                <p class="mt-2 text-gray-600">Loading deliverables...</p>
              </div>
              
              <div v-else-if="deliverables.length === 0" class="py-6 text-center">
                <p class="text-gray-600">No deliverables have been created for this project yet.</p>
              </div>
              
              <div v-else class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deliverable</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="deliverable in deliverables" :key="deliverable.name" class="hover:bg-gray-50">
                      <td class="px-6 py-4">
                        <div class="font-medium text-gray-900">{{ deliverable.deliverable_name }}</div>
                        <div class="text-sm text-gray-500">{{ deliverable.description || 'No description' }}</div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span :class="`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getDeliverableStatusClass(deliverable.status)}`">
                          {{ deliverable.status }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span :class="`${isOverdue(deliverable.due_date) ? 'text-red-600' : 'text-gray-600'}`">
                          {{ formatDate(deliverable.due_date) }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                          v-if="deliverable.document"
                          @click="downloadDeliverable(deliverable)"
                          class="text-blue-600 hover:text-blue-900 mr-3"
                        >
                          Download
                        </button>
                        <button 
                          v-if="deliverable.status === 'Awaiting Client Review'"
                          @click="goToDeliverableReview(deliverable.name)"
                          class="text-green-600 hover:text-green-900"
                        >
                          Review
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
          <!-- Project Team -->
          <div class="bg-white rounded-lg shadow mb-6">
            <div class="p-6">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">Project Team</h2>
              
              <div v-if="loadingTeam" class="text-center py-6">
                <div class="inline-block animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
                <p class="mt-2 text-gray-600">Loading team...</p>
              </div>
              
              <div v-else-if="teamMembers.length === 0" class="py-6 text-center">
                <p class="text-gray-600">No team members are assigned to this project yet.</p>
              </div>
              
              <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                  v-for="member in teamMembers"
                  :key="member.name"
                  class="border border-gray-200 rounded-lg p-4 flex items-center space-x-3"
                >
                  <div class="flex-shrink-0">
                    <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">
                      {{ getInitials(member.full_name) }}
                    </div>
                  </div>
                  <div class="flex-1">
                    <h4 class="text-sm font-medium text-gray-900">{{ member.full_name }}</h4>
                    <p class="text-xs text-gray-500">{{ member.designation || member.email }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
  
      <!-- Footer -->
      <footer-component></footer-component>
    </div>
  </template>
  
  <script>
  import NavBar from '@/components/NavBar.vue';
  import FooterComponent from '@/components/Footer.vue';
  
  export default {
    name: 'ProjectDetail',
    components: {
      NavBar,
      FooterComponent
    },
    data() {
      return {
        projectId: null,
        project: null,
        userName: '',
        deliverables: [],
        teamMembers: [],
        loading: true,
        loadingDeliverables: false,
        loadingTeam: false
      };
    },
    async created() {
      this.projectId = this.$route.params.id;
    },
    async mounted() {
      await this.getUserInfo();
      await this.fetchProjectDetails();
      
      if (this.project) {
        await Promise.all([
          this.fetchProjectDeliverables(),
          this.fetchProjectTeam()
        ]);
      }
    },
    methods: {
      getInitials(name) {
        if (!name) return '?';
        return name.split(' ')
          .map(part => part.charAt(0))
          .join('')
          .substring(0, 2)
          .toUpperCase();
      },
      
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
      
      async fetchProjectDetails() {
        try {
          this.loading = true;
          
          // Use a custom method for better security
          const response = await fetch('/api/method/project_management.api.get_client_project_details', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              project: this.projectId
            })
          });
          
          if (!response.ok) throw new Error('Failed to fetch project details');
          
          const data = await response.json();
          this.project = data.message || null;
        } catch (error) {
          console.error('Error fetching project details:', error);
          this.project = null;
        } finally {
          this.loading = false;
        }
      },
      
      async fetchProjectDeliverables() {
        try {
          this.loadingDeliverables = true;
          
          const response = await fetch('/api/method/project_management.api.get_client_deliverables', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              projects: [this.projectId],
              include_all: true
            })
          });
          
          if (!response.ok) throw new Error('Failed to fetch deliverables');
          
          const data = await response.json();
          this.deliverables = data.message || [];
        } catch (error) {
          console.error('Error fetching project deliverables:', error);
        } finally {
          this.loadingDeliverables = false;
        }
      },
      
      async fetchProjectTeam() {
        try {
          this.loadingTeam = true;
          
          const response = await fetch('/api/method/project_management.api.get_project_team_members', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              projects: [this.projectId]
            })
          });
          
          if (!response.ok) throw new Error('Failed to fetch team members');
          
          const data = await response.json();
          
          // Filter members to only those on this project
          const projectMembers = data.message.project_members[this.projectId] || [];
          this.teamMembers = data.message.members.filter(member => projectMembers.includes(member.name)) || [];
        } catch (error) {
          console.error('Error fetching team members:', error);
        } finally {
          this.loadingTeam = false;
        }
      },
      
      downloadDeliverable(deliverable) {
        if (deliverable.document) {
          window.open(deliverable.document, '_blank');
        }
      },
      
      openProjectChat() {
        if (this.project?.raven_channel) {
          const workspace_name = this.project.raven_channel.split('-')[0];
          window.open(`/raven/${encodeURIComponent(workspace_name)}/${encodeURIComponent(this.project.raven_channel)}`, '_blank');
        }
      },
      
      goToProjects() {
        this.$router.push('/client/projects');
      },
      
      goToDeliverableReview(deliverableId) {
        this.$router.push('/client/deliverables');
      }
    }
  };
  </script>