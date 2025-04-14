<template>
  <div class="min-h-screen bg-gray-50 py-10">
    <div class="max-w-7xl mx-auto bg-white rounded-2xl shadow-xl p-10">
      <h1 class="text-4xl font-semibold text-gray-800 mb-12 text-center tracking-wide">Your Deliverables</h1>

      <div class="overflow-x-auto bg-white rounded-lg shadow-lg">
        <table class="min-w-full table-auto border-collapse">
          <thead class="bg-gray-800 text-white rounded-t-lg">
            <tr>
              <th class="px-6 py-4 text-left text-sm font-medium uppercase">Deliverable Name</th>
              <th class="px-6 py-4 text-left text-sm font-medium uppercase">Project</th>
              <th class="px-6 py-4 text-left text-sm font-medium uppercase">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="deliverable in deliverables"
              :key="deliverable.id"
              class="bg-white border-b transition-transform duration-300 transform hover:scale-105 hover:shadow-lg"
            >
              <td class="px-6 py-4 text-sm text-gray-800 font-semibold">{{ deliverable.deliverable_name }}</td>
              <td class="px-6 py-4 text-sm text-gray-600">{{ deliverable.project }}</td>
              <td class="px-6 py-4 text-sm">
                <span
                  :class="{
                    'text-green-500': deliverable.status === 'Completed',
                    'text-yellow-500': deliverable.status === 'In Progress',
                    'text-red-500': deliverable.status === 'Pending'
                  }"
                  class="font-medium"
                >
                  {{ deliverable.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const deliverables = ref([]);
const router = useRouter();

// Fetch deliverables
const fetchDeliverables = async () => {
  try {
    const res = await fetch('/api/method/project_management.api.get_pending_deliverables_for_vendor');
    const data = await res.json();
    deliverables.value = data.message || [];
  } catch (error) {
    console.error('Failed to fetch deliverables:', error);
  }
};

onMounted(() => {
  fetchDeliverables();
});
</script>

<style scoped>
/* General Layout */
body {
  font-family: 'Inter', sans-serif;
}

table {
  border-spacing: 0;
}

th, td {
  border: none;
  padding: 1rem;
}

th {
  background-color: #1A202C; /* Darker Gray for Header */
  color: white;
  text-transform: uppercase;
}

td {
  background-color: #FFFFFF;
}

/* Row Hover Effect */
tr:hover {
  background-color: #F7FAFC; /* Light Gray Background on Hover */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* Status Color Coding */
.text-green-500 {
  color: #38A169;
}

.text-yellow-500 {
  color: #D69E2E;
}

.text-red-500 {
  color: #E53E3E;
}

/* Button Styling */
button {
  transition: all 0.3s ease;
  padding: 0.75rem 2rem;
  font-weight: 600;
  text-transform: uppercase;
  border-radius: 0.5rem;
}

button:hover {
  cursor: pointer;
  background-color: #2D3748;
  transform: scale(1.05);
}

.bg-gray-800 {
  background-color: #2D3748;
}

button i {
  font-size: 1.2rem;
}

/* Responsive Table */
@media (max-width: 768px) {
  table {
    width: 100%;
    overflow-x: auto;
  }

  th, td {
    font-size: 0.875rem;
  }
}

/* Container Styling */
.bg-white {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

h1 {
  font-weight: 700;
  letter-spacing: 0.5px;
}
</style>
