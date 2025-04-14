<template>
  <Navbar />
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Vendor Dashboard</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <DashboardCard title="Assigned Tasks" :count="tasks.length" icon="✅" />
      <DashboardCard title="Your Deliverables" :count="pendingDeliverables.length" icon="📤" />
      <DashboardCard
  title="Submit a Deliverable"
  icon="📤"
  @click="goToSubmitPage"
/>
    </div>

    <div class="mt-6">
      <div class="bg-white p-4 rounded-lg shadow-md">
        <h2 class="font-bold text-lg mb-4">Assigned Tasks</h2>
        <table class="w-full table-auto text-left border border-gray-200 rounded-lg">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-4 py-2 font-semibold text-sm">Task</th>
              <th class="px-4 py-2 font-semibold text-sm">Status</th>
              <th class="px-4 py-2 font-semibold text-sm">Due Date</th>
              <th class="px-4 py-2 font-semibold text-sm">Progress</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="task in tasks"
              :key="task.name"
              class="border-t hover:bg-gray-50 transition"
            >
              <td class="px-4 py-2">{{ task.name }}</td>
              <td class="px-4 py-2">{{ task.status }}</td>
              <td class="px-4 py-2">{{ task.due_date || '—' }}</td>
              <td class="px-4 py-2">
                <div class="w-full bg-gray-200 rounded-full h-4">
                  <div
                    class="h-4 rounded-full text-xs text-white text-center transition-all duration-300"
                    :class="{
                      'bg-red-500': (task.progress_ || 0) <= 25,
                      'bg-yellow-500': (task.progress_ || 0) > 25 && task.progress_ <= 50,
                      'bg-blue-500': (task.progress_ || 0) > 50 && task.progress_ <= 75,
                      'bg-green-500': (task.progress_ || 0) > 75
                    }"
                    :style="{ width: `${task.progress_ || 0}%` }"
                  >
                    {{ task.progress_ || 0 }}%
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="tasks.length === 0">
              <td colspan="4" class="text-center py-4 text-gray-500">No tasks assigned.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="mt-6">
      <div class="bg-white p-4 rounded-lg shadow-md">
        <h2 class="font-bold text-lg mb-4">Pending Deliverables</h2>
        <table class="w-full table-auto text-left border border-gray-200 rounded-lg">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-4 py-2 font-semibold text-sm">Name</th>
              <th class="px-4 py-2 font-semibold text-sm">Project</th>
              <th class="px-4 py-2 font-semibold text-sm">Status</th>
              <th class="px-4 py-2 font-semibold text-sm">Due Date</th>
              <th class="px-4 py-2 font-semibold text-sm">Priority</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in pendingDeliverables"
              :key="item.name"
              class="border-t hover:bg-gray-50 transition"
            >
              <td class="px-4 py-2">{{ item.deliverable_name }}</td>
              <td class="px-4 py-2">{{ item.project }}</td>
              <td class="px-4 py-2">{{ item.status }}</td>
              <td class="px-4 py-2">{{ item.due_date }}</td>
              <td class="px-4 py-2">{{ item.priority }}</td>
            </tr>
            <tr v-if="pendingDeliverables.length === 0">
              <td colspan="5" class="text-center py-4 text-gray-500">No pending deliverables.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
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


const goToSubmitPage = () => {
  router.push('/submit-deliverable');
};

const tasks = ref([]);
const pendingDeliverables = ref([]);
const payments = ref([]); // You can fill this in with actual data later

const fetchTasks = async () => {
  try {
    const response = await fetch('/api/method/project_management.api.get_assigned_tasks_for_vendor');
    const result = await response.json();
    console.log('Tasks API response:', result);
    tasks.value = result.message || [];
  } catch (err) {
    console.error('Failed to load tasks:', err);
  }
};

const fetchPendingDeliverables = async () => {
  try {
    const response = await fetch('/api/method/project_management.api.get_pending_deliverables_for_vendor');
    const result = await response.json();
    console.log('Deliverables API response:', result);
    pendingDeliverables.value = result.message || [];
  } catch (err) {
    console.error('Failed to load pending deliverables:', err);
  }
};

onMounted(() => {
  fetchTasks();
  fetchPendingDeliverables();
});
</script>
