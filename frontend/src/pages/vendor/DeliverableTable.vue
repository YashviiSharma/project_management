<template>
    <div class="min-h-screen bg-gray-100 p-6">
      <div class="max-w-6xl mx-auto bg-white rounded-2xl shadow-lg p-8">
        <h1 class="text-4xl font-extrabold text-gray-800 mb-6">Deliverables</h1>
  
        <div class="overflow-x-auto bg-white rounded-lg shadow-lg">
          <table class="min-w-full table-auto border-collapse">
            <thead class="bg-blue-600 text-white">
              <tr>
                <th class="px-6 py-3 text-left text-sm font-medium uppercase">Deliverable Name</th>
                <th class="px-6 py-3 text-left text-sm font-medium uppercase">Project</th>
                <th class="px-6 py-3 text-left text-sm font-medium uppercase">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="deliverable in deliverables"
                :key="deliverable.id"
                class="hover:bg-gray-100 transition-all duration-200"
              >
                <td class="px-6 py-4 border-b text-sm">{{ deliverable.deliverable_name }}</td>
                <td class="px-6 py-4 border-b text-sm">{{ deliverable.project }}</td>
                <td class="px-6 py-4 border-b text-sm">
                  <span>
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
  table {
    border-spacing: 0;
  }
  
  th, td {
    border: 1px solid #e2e8f0; 
  }
  
  th {
    background-color: #1d4ed8; 
    color: white;
  }
  
  tr:hover {
    background-color: #f1f5f9;
  }
  
  button {
    transition: all 0.3s ease;
  }
  
  button:hover {
    transform: scale(1.1);
    cursor: pointer;
  }
  
  button i {
    font-size: 1.2rem;
  }
  
  .bg-white {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  </style>
  