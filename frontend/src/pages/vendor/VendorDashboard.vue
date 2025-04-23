<template>
  <Navbar />
  <div class="p-6 bg-gray-50 min-h-screen dark:bg-gray-900 transition-colors duration-300">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-extrabold text-gray-800 dark:text-white">Welcome, Vendor!</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <DashboardCard title="Assigned Tasks" :count="tasks.length" icon="🗂️" />
      <DashboardCard title="Submit a Deliverable⬇️" @click="goToSubmitPage" />
      <DashboardCard title="Submitted Deliverables" :count="pendingDeliverables.length" icon="📦" />
    </div>

    <div class="mt-6">
  <div class="bg-white p-4 rounded-lg shadow-md">
    <h2 class="font-bold text-lg mb-4">Your Tasks</h2>
    <div v-if="tasks.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="task in tasks"
        :key="task.name"
        class="p-4 border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition bg-white"
      >
        <div class="flex justify-between items-center mb-2">
          <h3 class="font-semibold text-md text-gray-800 truncate">{{ task.name }}</h3>
          <span
            class="text-xs font-medium px-2 py-1 rounded-full"
            :class="{
              'bg-green-100 text-green-700': task.status === 'Completed',
              'bg-yellow-100 text-yellow-700': task.status === 'In Progress',
              'bg-red-100 text-red-700': task.status === 'Overdue'
            }"
          >
            {{ task.status }}
          </span>
        </div>

        <div class="flex justify-between items-center text-sm text-gray-500 mb-3">
          <span>
            📅 <strong>Due:</strong> {{ task.end_date || '—' }}
          </span>
          <span v-if="task.priority">
             <strong>{{ task.priority }}</strong>
          </span>
        </div>

        <div class="flex items-center justify-between">
          <div class="w-16 h-16 relative">
            <svg class="w-full h-full">
              <circle
                class="text-gray-200"
                stroke-width="5"
                fill="transparent"
                r="25"
                cx="32"
                cy="32"
              />
              <circle
                class="text-blue-500"
                stroke-width="5"
                :stroke-dasharray="157"
                :stroke-dashoffset="157 - (157 * (task.progress_ || 0)) / 100"
                stroke-linecap="round"
                fill="transparent"
                r="25"
                cx="32"
                cy="32"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center text-xs font-bold text-blue-600">
              {{ task.progress_ || 0 }}%
            </div>
          </div>

          <div class="flex-1 ml-4 text-sm text-gray-600 space-y-1">
            <p><strong>Project:</strong> {{ task.project || '—' }}</p>
            <p><strong>Assigned By:</strong> {{ task.assigned_by || 'Project Manager' }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-6 text-gray-500">
      No tasks assigned. Enjoy your day! 🎉
    </div>
  </div>
</div>

    <!-- Pending Deliverables -->
    <section class="mt-10">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
        <h2 class="text-2xl font-bold text-gray-700 dark:text-white mb-4 flex items-center gap-2">
         Deliverables
        </h2>
        <div v-if="pendingDeliverables.length > 0" class="overflow-x-auto">
          <table class="min-w-full table-auto text-left text-sm">
            <thead class="bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
              <tr>
                <th class="px-4 py-2">Name</th>
                <th class="px-4 py-2">Project</th>
                <th class="px-4 py-2">Status</th>
                <th class="px-4 py-2">Due Date</th>
                <th class="px-4 py-2">Priority</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in pendingDeliverables"
                :key="item.name"
                class="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900"
              >
                <td class="px-4 py-2">{{ item.deliverable_name }}</td>
                <td class="px-4 py-2">{{ item.project }}</td>
                <td class="px-4 py-2">{{ item.status }}</td>
                <td class="px-4 py-2">{{ item.due_date }}</td>
                <td class="px-4 py-2">
                  <span
                    class="px-2 py-1 text-xs font-semibold rounded-full"
                    :class="{
                      'bg-red-100 text-red-800': item.priority === 'High',
                      'bg-yellow-100 text-yellow-800': item.priority === 'Medium',
                      'bg-green-100 text-green-800': item.priority === 'Low'
                    }"
                  >
                    {{ item.priority }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400">No pending deliverables.</div>
      </div>
    </section>
  </div>
  <Footer />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
import DashboardCard from '@/components/DashboardCard.vue';
import { useRouter } from 'vue-router';
const router = useRouter();
const tasks = ref([]);
const pendingDeliverables = ref([]);
const isDark = ref(false);

const goToSubmitPage = () => {
  router.push('/submit-deliverable');
};

onMounted(() => {
  fetchTasks();
  fetchPendingDeliverables();
});

// Fetch vendor tasks from API
const fetchTasks = async () => {
  try {
    const response = await fetch('/api/method/project_management.api.get_assigned_tasks_for_vendor');
    const result = await response.json();
    tasks.value = result.message || [];
  } catch (err) {
    console.error('Failed to load tasks:', err);
  }
};

// Fetch vendor's pending deliverables from API
const fetchPendingDeliverables = async () => {
  try {
    const response = await fetch('/api/method/project_management.api.get_pending_deliverables_for_vendor');
    const result = await response.json();
    pendingDeliverables.value = result.message || [];
  } catch (err) {
    console.error('Failed to load pending deliverables:', err);
  }
};
</script>

<style scoped>
body {
  transition: background-color 0.3s ease;
}
</style>
