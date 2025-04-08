<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation Bar -->
    <nav-bar :userName="userName"></nav-bar>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-800 mb-6">Project Team Members</h1>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
        <p class="mt-3 text-gray-600">Loading team members...</p>
      </div>

      <div v-else-if="teamMembers.length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-600">No team members assigned to your projects yet.</p>
      </div>

      <div v-else>
        <!-- Filter by project dropdown -->
        <div class="mb-6 flex justify-between items-center">
          <div class="max-w-xs">
            <label for="projectFilter" class="block text-sm font-medium text-gray-700 mb-1">Filter by Project</label>
            <select 
              id="projectFilter"
              v-model="selectedProject"
              class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Projects</option>
              <option v-for="project in projects" :key="project.name" :value="project.name">
                {{ project.project_name }}
              </option>
            </select>
          </div>
          
          <div>
            <span class="text-gray-700">{{ filteredTeamMembers.length }} members found</span>
          </div>
        </div>

        <!-- Team Members Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="member in filteredTeamMembers" 
            :key="member.name"
            class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition"
          >
            <div class="p-6">
              <div class="flex items-start justify-between">
                <div class="flex items-start space-x-4">
                  <div class="flex-shrink-0">
                    <div class="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xl">
                      {{ getInitials(member.full_name) }}
                    </div>
                  </div>
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-gray-800">{{ member.full_name }}</h3>
                    <p class="text-sm text-gray-600" v-if="member.designation">{{ member.designation }}</p>
                    <p class="text-sm text-gray-500" v-if="member.department">{{ member.department }}</p>
                  </div>
                </div>
                <div>
                  <button 
                    @click="openRavenChat(member.name)" 
                    class="px-3 py-1 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition"
                  >
                    Chat
                  </button>
                </div>
              </div>

              <div class="mt-4 space-y-2">
                <div class="flex items-center text-sm">
                  <svg class="h-4 w-4 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <a :href="`mailto:${member.email}`" class="text-blue-600 hover:underline truncate">{{ member.email }}</a>
                </div>
                <div class="flex items-center text-sm" v-if="member.mobile_no">
                  <svg class="h-4 w-4 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <span>{{ member.mobile_no }}</span>
                </div>
              </div>

              <div class="mt-4">
                <p class="text-sm font-medium text-gray-700 mb-2">Project Assignments:</p>
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="(projectId, index) in getMemberProjects(member.name)" 
                    :key="index"
                    class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full"
                  >
                    {{ getProjectName(projectId) }}
                  </span>
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
  name: 'TeamMembers',
  components: {
    NavBar,
    FooterComponent
  },
  data() {
    return {
      userName: '',
      projects: [],
      teamMembers: [],
      projectMembers: {}, // Map of project ID to array of member IDs
      loading: true,
      selectedProject: ''
    };
  },
  computed: {
    filteredTeamMembers() {
      if (!this.selectedProject) {
        return this.teamMembers;
      }
      
      const memberIds = this.projectMembers[this.selectedProject] || [];
      return this.teamMembers.filter(member => memberIds.includes(member.name));
    }
  },
  async mounted() {
    await this.getUserInfo();
    await this.fetchClientProjects();
    await this.fetchTeamMembers();
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
    
    openRavenChat(memberId) {
      // Redirect to Raven one-to-one chat with the selected member
      window.location.href = `/raven/Project?member=${memberId}`;
    },
    
    getMemberProjects(memberId) {
      const projectIds = [];
      
      for (const [projectId, members] of Object.entries(this.projectMembers)) {
        if (members.includes(memberId)) {
          projectIds.push(projectId);
        }
      }
      
      return projectIds;
    },
    
    getProjectName(projectId) {
      const project = this.projects.find(p => p.name === projectId);
      return project ? project.project_name : projectId;
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
        const response = await fetch('/api/method/project_management.api.get_client_projects');
        
        if (!response.ok) throw new Error('Failed to fetch projects');
        
        const data = await response.json();
        this.projects = data.message || [];
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    },
    
    async fetchTeamMembers() {
      try {
        this.loading = true;
        
        if (this.projects.length === 0) {
          this.teamMembers = [];
          this.projectMembers = {};
          return;
        }
        
        const projectNames = this.projects.map(p => p.name);
        
        const response = await fetch('/api/method/project_management.api.get_project_team_members', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            projects: projectNames
          })
        });
        
        if (!response.ok) throw new Error('Failed to fetch team members');
        
        const data = await response.json();
        
        this.teamMembers = data.message.members || [];
        this.projectMembers = data.message.project_members || {};
      } catch (error) {
        console.error('Error fetching team members:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>