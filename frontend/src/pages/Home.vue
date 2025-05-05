<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <!-- Navbar -->
    <nav class="bg-blue-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-3 flex justify-between items-center">
        <div class="flex items-center space-x-2">
          <img src="/logo.png" alt="Logo" class="h-8">
          <span class="text-xl font-semibold">Project Management Portal</span>
        </div>

        <div class="hidden md:flex space-x-6">
          <router-link to="/client/dashboard" class="hover:text-blue-200">Client Dashboard</router-link>
          <router-link to="/vendor/dashboard" class="hover:text-blue-200">Vendor Dashboard</router-link>
          <router-link to="/app/user" class="hover:text-blue-200">Dashboard</router-link>
        </div>

        <div class="flex items-center space-x-4">
          <template v-if="isLoggedIn">
            <span class="hidden sm:inline">Welcome, {{ userName }}</span>
            <button @click="logout" class="bg-blue-700 hover:bg-blue-800 px-3 py-1 rounded transition-colors duration-200">
              Logout
            </button>
          </template>
          <template v-else>
            <router-link 
              to="/account/login" 
              class="bg-blue-700 hover:bg-blue-800 px-3 py-1 rounded transition-colors duration-200"
            >
              Login
            </router-link>
          </template>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-grow container mx-auto px-4 py-8">
      <!-- Metadata Section -->
      <div class="mb-8 bg-white rounded-xl shadow-md p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-6 border-b pb-2">Project Metadata</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="metadata-card bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
            <div class="metadata-icon bg-blue-100 text-blue-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h3 class="metadata-title">Total Projects</h3>
              <p class="metadata-value">24</p>
              <p class="metadata-change text-green-600">+2 from last week</p>
            </div>
          </div>
          
          <div class="metadata-card bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
            <div class="metadata-icon bg-green-100 text-green-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 class="metadata-title">Active Projects</h3>
              <p class="metadata-value">18</p>
              <p class="metadata-change text-green-600">75% active</p>
            </div>
          </div>
          
          <div class="metadata-card bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
            <div class="metadata-icon bg-yellow-100 text-yellow-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <h3 class="metadata-title">Total Tasks</h3>
              <p class="metadata-value">142</p>
              <p class="metadata-change text-green-600">86 completed</p>
            </div>
          </div>
          
          <div class="metadata-card bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
            <div class="metadata-icon bg-purple-100 text-purple-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div>
              <h3 class="metadata-title">Completion Rate</h3>
              <p class="metadata-value">61%</p>
              <p class="metadata-change text-green-600">+5% this month</p>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Enhanced Task Status Chart -->
        <div class="bg-white rounded-xl shadow-md p-6 lg:col-span-2">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-gray-800">Task Status Distribution</h2>
            <div class="flex space-x-2">
              <button class="px-3 py-1 text-sm bg-blue-100 text-blue-600 rounded-md">Weekly</button>
              <button class="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded-md">Monthly</button>
              <button class="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded-md">Yearly</button>
            </div>
          </div>
          <div class="h-80">
            <div class="flex h-full">
              <!-- Donut Chart -->
              <div class="w-1/2 flex items-center justify-center">
                <div class="relative w-64 h-64">
                  <!-- Chart background -->
                  <svg class="w-full h-full" viewBox="0 0 100 100">
                    <!-- Completed -->
                    <path d="M50 50 L50 0 A50 50 0 0 1 86.6 25 Z" fill="#10B981" />
                    <!-- In Progress -->
                    <path d="M50 50 L86.6 25 A50 50 0 0 1 86.6 75 Z" fill="#3B82F6" />
                    <!-- Pending -->
                    <path d="M50 50 L86.6 75 A50 50 0 0 1 50 100 Z" fill="#F59E0B" />
                    <!-- Overdue -->
                    <path d="M50 50 L50 100 A50 50 0 0 1 13.4 75 Z" fill="#EF4444" />
                    <!-- Center circle -->
                    <circle cx="50" cy="50" r="30" fill="white" />
                  </svg>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <div class="text-center">
                      <p class="text-3xl font-bold text-gray-800">142</p>
                      <p class="text-sm text-gray-500">Total Tasks</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Legend and Details -->
              <div class="w-1/2 flex flex-col justify-center pl-6">
                <div class="space-y-4">
                  <div class="flex items-center">
                    <div class="w-4 h-4 rounded-full bg-green-500 mr-3"></div>
                    <div class="flex-1">
                      <div class="flex justify-between">
                        <span class="text-gray-700 font-medium">Completed</span>
                        <span class="text-gray-700">61%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div class="bg-green-500 h-2 rounded-full" style="width: 61%"></div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex items-center">
                    <div class="w-4 h-4 rounded-full bg-blue-500 mr-3"></div>
                    <div class="flex-1">
                      <div class="flex justify-between">
                        <span class="text-gray-700 font-medium">In Progress</span>
                        <span class="text-gray-700">22%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div class="bg-blue-500 h-2 rounded-full" style="width: 22%"></div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex items-center">
                    <div class="w-4 h-4 rounded-full bg-yellow-500 mr-3"></div>
                    <div class="flex-1">
                      <div class="flex justify-between">
                        <span class="text-gray-700 font-medium">Pending</span>
                        <span class="text-gray-700">13%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div class="bg-yellow-500 h-2 rounded-full" style="width: 13%"></div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex items-center">
                    <div class="w-4 h-4 rounded-full bg-red-500 mr-3"></div>
                    <div class="flex-1">
                      <div class="flex justify-between">
                        <span class="text-gray-700 font-medium">Overdue</span>
                        <span class="text-gray-700">4%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div class="bg-red-500 h-2 rounded-full" style="width: 4%"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity with Enhanced UI -->
        <div class="bg-white rounded-xl shadow-md p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-gray-800">Recent Activity</h2>
            <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">View All</button>
          </div>
          <div class="space-y-4">
            <div class="activity-item">
              <div class="activity-avatar bg-blue-100 text-blue-600">JD</div>
              <div class="activity-content">
                <div class="activity-header">
                  <span class="activity-user">John Doe</span>
                  <span class="activity-time">2h ago</span>
                </div>
                <p class="activity-text">Completed task "Design Mockups"</p>
                <div class="activity-badge bg-blue-50 text-blue-600">Design</div>
              </div>
            </div>
            
            <div class="activity-item">
              <div class="activity-avatar bg-green-100 text-green-600">AS</div>
              <div class="activity-content">
                <div class="activity-header">
                  <span class="activity-user">Alice Smith</span>
                  <span class="activity-time">5h ago</span>
                </div>
                <p class="activity-text">Updated project "Website Redesign"</p>
                <div class="activity-badge bg-green-50 text-green-600">Development</div>
              </div>
            </div>
            
            <div class="activity-item">
              <div class="activity-avatar bg-purple-100 text-purple-600">RJ</div>
              <div class="activity-content">
                <div class="activity-header">
                  <span class="activity-user">Robert Johnson</span>
                  <span class="activity-time">1d ago</span>
                </div>
                <p class="activity-text">Commented on deliverable "API Docs"</p>
                <div class="activity-badge bg-purple-50 text-purple-600">Documentation</div>
              </div>
            </div>
            
            <div class="activity-item">
              <div class="activity-avatar bg-yellow-100 text-yellow-600">MB</div>
              <div class="activity-content">
                <div class="activity-header">
                  <span class="activity-user">Maria Brown</span>
                  <span class="activity-time">2d ago</span>
                </div>
                <p class="activity-text">Started task "Database Migration"</p>
                <div class="activity-badge bg-yellow-50 text-yellow-600">Database</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tasks by Project with Bar Chart -->
        <div class="bg-white rounded-xl shadow-md p-6 lg:col-span-3">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-gray-800">Tasks by Project</h2>
            <div class="flex space-x-2">
              <button class="px-3 py-1 text-sm bg-blue-100 text-blue-600 rounded-md">This Week</button>
              <button class="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded-md">This Month</button>
            </div>
          </div>
          <div class="h-80">
            <div class="flex h-full">
              <!-- Project Stats -->
              <div class="w-1/3 pr-6">
                <div class="space-y-6">
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm font-medium text-gray-700">Website Redesign</span>
                      <span class="text-sm text-gray-500">15/20</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-blue-600 h-2 rounded-full" style="width: 75%"></div>
                    </div>
                  </div>
                  
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm font-medium text-gray-700">Mobile App</span>
                      <span class="text-sm text-gray-500">18/20</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-green-600 h-2 rounded-full" style="width: 90%"></div>
                    </div>
                  </div>
                  
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm font-medium text-gray-700">API Development</span>
                      <span class="text-sm text-gray-500">9/20</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-yellow-600 h-2 rounded-full" style="width: 45%"></div>
                    </div>
                  </div>
                  
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm font-medium text-gray-700">Internal Tools</span>
                      <span class="text-sm text-gray-500">12/15</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-purple-600 h-2 rounded-full" style="width: 80%"></div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Bar Chart -->
              <div class="w-2/3">
                <div class="h-full w-full">
                  <div class="h-full flex flex-col">
                    <div class="flex-1 grid grid-cols-4 gap-4 items-end">
                      <!-- Website Redesign -->
                      <div class="flex flex-col items-center">
                        <div class="w-3/4 bg-blue-600 rounded-t-md" style="height: 75%"></div>
                        <span class="text-xs text-gray-500 mt-1">Web</span>
                      </div>
                      
                      <!-- Mobile App -->
                      <div class="flex flex-col items-center">
                        <div class="w-3/4 bg-green-600 rounded-t-md" style="height: 90%"></div>
                        <span class="text-xs text-gray-500 mt-1">Mobile</span>
                      </div>
                      
                      <!-- API Development -->
                      <div class="flex flex-col items-center">
                        <div class="w-3/4 bg-yellow-600 rounded-t-md" style="height: 45%"></div>
                        <span class="text-xs text-gray-500 mt-1">API</span>
                      </div>
                      
                      <!-- Internal Tools -->
                      <div class="flex flex-col items-center">
                        <div class="w-3/4 bg-purple-600 rounded-t-md" style="height: 80%"></div>
                        <span class="text-xs text-gray-500 mt-1">Tools</span>
                      </div>
                    </div>
                    
                    <div class="h-8 flex items-center justify-center border-t border-gray-200">
                      <span class="text-xs text-gray-500">Projects Completion Progress</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Team Performance -->
        <div class="bg-white rounded-xl shadow-md p-6 lg:col-span-2">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Team Performance</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Member</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tasks</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Completed</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="member in teamMembers" :key="member.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center" :class="member.avatarBg">
                        <span :class="member.avatarText">{{ member.initials }}</span>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{{ member.name }}</div>
                        <div class="text-sm text-gray-500">{{ member.role }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ member.tasks }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ member.completed }}</td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-24 mr-2">
                        <div class="w-full bg-gray-200 rounded-full h-2.5">
                          <div class="h-2.5 rounded-full" :class="member.performanceColor" :style="'width: ' + member.performance + '%'"></div>
                        </div>
                      </div>
                      <span class="text-sm text-gray-500">{{ member.performance }}%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Upcoming Deadlines -->
        <div class="bg-white rounded-xl shadow-md p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold text-gray-800">Upcoming Deadlines</h2>
            <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">View Calendar</button>
          </div>
          <div class="space-y-4">
            <div class="deadline-item border-l-4 border-blue-500">
              <div class="deadline-dot bg-blue-500"></div>
              <div>
                <h3 class="deadline-title">Finalize API Documentation</h3>
                <p class="deadline-project">Project: Website Redesign</p>
                <p class="deadline-date text-blue-600">Due: Tomorrow</p>
              </div>
            </div>
            
            <div class="deadline-item border-l-4 border-green-500">
              <div class="deadline-dot bg-green-500"></div>
              <div>
                <h3 class="deadline-title">Client Review Meeting</h3>
                <p class="deadline-project">Project: Mobile App</p>
                <p class="deadline-date text-green-600">Due: May 10</p>
              </div>
            </div>
            
            <div class="deadline-item border-l-4 border-yellow-500">
              <div class="deadline-dot bg-yellow-500"></div>
              <div>
                <h3 class="deadline-title">Database Migration</h3>
                <p class="deadline-project">Project: Internal Tools</p>
                <p class="deadline-date text-yellow-600">Due: May 15</p>
              </div>
            </div>
            
            <div class="deadline-item border-l-4 border-red-500">
              <div class="deadline-dot bg-red-500"></div>
              <div>
                <h3 class="deadline-title">Final Deployment</h3>
                <p class="deadline-project">Project: Website Redesign</p>
                <p class="deadline-date text-red-600">Due: May 20</p>
              </div>
            </div>
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
            <router-link to="/client/terms" class="hover:text-blue-300">Terms</router-link>
            <router-link to="/client/privacy" class="hover:text-blue-300">Privacy</router-link>
            <router-link to="/client/contact" class="hover:text-blue-300">Contact</router-link>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  data() {
    return {
      isLoggedIn: false, // This should be dynamically set based on auth state
      userName: 'John Doe',
      currentYear: new Date().getFullYear(),
      teamMembers: [
        {
          id: 1,
          initials: 'JD',
          name: 'John Doe',
          role: 'Developer',
          tasks: 24,
          completed: 18,
          performance: 85,
          performanceColor: 'bg-green-600',
          avatarBg: 'bg-blue-100',
          avatarText: 'text-blue-600'
        },
        {
          id: 2,
          initials: 'AS',
          name: 'Alice Smith',
          role: 'Designer',
          tasks: 18,
          completed: 15,
          performance: 78,
          performanceColor: 'bg-green-600',
          avatarBg: 'bg-purple-100',
          avatarText: 'text-purple-600'
        },
        {
          id: 3,
          initials: 'RJ',
          name: 'Robert Johnson',
          role: 'QA Engineer',
          tasks: 22,
          completed: 16,
          performance: 65,
          performanceColor: 'bg-yellow-600',
          avatarBg: 'bg-yellow-100',
          avatarText: 'text-yellow-600'
        }
      ]
    }
  },
  methods: {
    logout() {
      // Implement logout logic here
      this.isLoggedIn = false;
      // Redirect to same page after logout
      this.$router.go();
    },
    checkAuth() {
      // Implement your authentication check logic here
      // For demo purposes, we'll randomly set isLoggedIn
      this.isLoggedIn = Math.random() > 0.5;
    }
  },
  created() {
    this.checkAuth();
  }
}
</script>

<style scoped>
/* Navbar link active state */
.router-link-active {
  @apply text-blue-300 font-medium;
}

/* Metadata Card Styles */
.metadata-card {
  @apply rounded-xl p-4 flex items-center transition-all duration-300 hover:shadow-md;
}

.metadata-icon {
  @apply h-12 w-12 rounded-lg flex items-center justify-center mr-4;
}

.metadata-title {
  @apply text-sm text-gray-500 font-medium;
}

.metadata-value {
  @apply text-2xl font-bold text-gray-800 mt-1;
}

.metadata-change {
  @apply text-xs mt-1;
}

/* Activity Item Styles */
.activity-item {
  @apply flex p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200;
}

.activity-avatar {
  @apply h-10 w-10 rounded-full flex-shrink-0 flex items-center justify-center font-medium mr-3;
}

.activity-content {
  @apply flex-1;
}

.activity-header {
  @apply flex justify-between items-baseline;
}

.activity-user {
  @apply text-sm font-medium text-gray-900;
}

.activity-time {
  @apply text-xs text-gray-500;
}

.activity-text {
  @apply text-sm text-gray-600 mt-1;
}

.activity-badge {
  @apply inline-block px-2 py-1 rounded-full text-xs font-medium mt-2;
}

/* Deadline Item Styles */
.deadline-item {
  @apply pl-4 py-2 relative;
}

.deadline-dot {
  @apply absolute top-4 -left-2 h-3 w-3 rounded-full;
}

.deadline-title {
  @apply text-sm font-medium text-gray-900;
}

.deadline-project {
  @apply text-xs text-gray-500;
}

.deadline-date {
  @apply text-xs mt-1 font-medium;
}

/* Smooth transitions */
button, a {
  @apply transition-all duration-200;
}

/* Enhanced shadows */
.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* Smooth rounded corners */
.rounded-xl {
  border-radius: 0.75rem;
}
</style>