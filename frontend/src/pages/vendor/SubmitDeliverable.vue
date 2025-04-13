<template>
    <div class="min-h-screen bg-gray-50 p-6">
      <div class="max-w-3xl mx-auto bg-white rounded-2xl shadow-lg p-8 relative">
        <h1 class="text-3xl font-extrabold text-gray-800 mb-6 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
            <path d="M13 7H7v6h6V7z" />
            <path fill-rule="evenodd" d="M5 3a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V5a2 2 0 00-2-2H5zm0 2h10v10H5V5z" clip-rule="evenodd" />
          </svg>
          Submit a Deliverable
        </h1>
  
        <div class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Select Deliverable</label>
            <select
              v-model="selectedDeliverable"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option disabled value="">-- Choose Deliverable --</option>
              <option
                v-for="d in deliverables"
                :key="d.name"
                :value="d.name"
              >
                {{ d.deliverable_name }} ({{ d.project }})
              </option>
            </select>
          </div>
  
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Upload Document</label>
            <input
              type="file"
              class="block w-full text-sm text-gray-500
                     file:mr-4 file:py-2 file:px-4
                     file:rounded-lg file:border-0
                     file:text-sm file:font-semibold
                     file:bg-blue-50 file:text-blue-700
                     hover:file:bg-blue-100"
              @change="handleFileChange"
            />
          </div>
  
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="description"
              rows="5"
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Briefly describe your deliverable..."
            ></textarea>
          </div>
  
          <div class="text-right">
            <button
              @click="submitDeliverable"
              :disabled="!selectedDeliverable"
              class="bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 transition-all duration-200 text-white px-6 py-3 rounded-lg font-semibold shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              🚀 Submit Deliverable
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const deliverables = ref([]);
const selectedDeliverable = ref('');
const file = ref(null);
const description = ref('');

const fetchDeliverables = async () => {
  try {
    const res = await fetch('/api/method/project_management.api.get_pending_deliverables_for_vendor');
    const data = await res.json();
    deliverables.value = data.message || [];
  } catch (error) {
    console.error('Failed to fetch deliverables:', error);
  }
};

const handleFileChange = (e) => {
  file.value = e.target.files[0];
};

const submitDeliverable = async () => {
  const formData = new FormData();
  formData.append('deliverable', selectedDeliverable.value);
  formData.append('description', description.value);
  if (file.value) {
    formData.append('file', file.value);
  }

  try {
    const res = await fetch('/api/method/project_management.api.submit_deliverable', {
      method: 'POST',
      body: formData,
      headers: {
        'Connection': 'close'
      }
    });

    const data = await res.json();
console.log("Deliverables API response:", data);

if (data.message?.message === 'Deliverable submitted successfully') {
  alert('Deliverable submitted successfully!');
  router.push('/thank-you');
} else {
  alert('Something went wrong: ' + (data.message?.message || 'Unknown error'));
}

  } catch (err) {
    console.error(err);
    alert('Failed to submit deliverable. Please try again.');
  }
};

onMounted(() => {
  fetchDeliverables();
});
</script>

  