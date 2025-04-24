<template>
  <Navbar />
    <div class="max-w-4xl mx-auto mt-10 p-6 bg-white rounded-2xl shadow-lg">
      <div class="mb-6 flex items-center justify-between">
        <button @click="goBack" class="text-sm text-gray-600 hover:text-indigo-600 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Tasks
        </button>
  
        <span
          v-if="task"
          class="text-xs font-semibold px-3 py-1 rounded-full"
          :class="statusBadge(task.status)"
        >
          {{ task.status }}
        </span>
      </div>
  
      <div v-if="task" class="space-y-6">
        <div>
          <h2 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
            {{ getIcon(task.task_type) }} {{ task.name }}
          </h2>
          <p class="text-sm text-gray-500 mt-1">Assigned to: <strong>{{ task.assigned_to }}</strong></p>
        </div>
  
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-600">📅 <strong>Due:</strong> {{ task.end_date || '—' }}</p>
            <p class="text-sm text-gray-600">🔥 <strong>Priority:</strong> {{ task.priority || 'Normal' }}</p>
            <p class="text-sm text-gray-600">📝 <strong>Type:</strong> {{ task.task_type || 'General' }}</p>
          </div>
  
          <div>
            <div class="text-sm text-gray-600 mb-1"><strong>Progress</strong></div>
            <div class="w-full bg-gray-200 rounded-full h-5 relative overflow-hidden">
              <div
                class="h-5 text-white text-xs text-center leading-5 transition-all duration-500 ease-in-out"
                :style="{ width: `${task.progress_ || 0}%` }"
                :class="progressColor(task.progress_)"
              >
                {{ task.progress_ || 0 }}%
              </div>
            </div>
          </div>
        </div>
  
        <div>
          <h3 class="text-lg font-semibold text-gray-800 mb-1">🧾 Description</h3>
          <p class="text-sm text-gray-700 whitespace-pre-wrap">
            {{ task.description || 'No description provided.' }}
          </p>
        </div>
  
        <div>
          <h3 class="text-lg font-semibold text-gray-800 mb-1">💬 Comments</h3>
          <p class="text-sm text-gray-500">No comments yet.</p>
          <!-- Placeholder — can add a real comment system later -->
        </div>
      </div>
  
      <div v-else class="text-center py-10 text-gray-500">
        Loading task details...
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import Navbar from '@/components/Navbar.vue';  
  const route = useRoute();
  const router = useRouter();
  const taskName = decodeURIComponent(route.params.name);
  const task = ref(null);
  
  const fetchTask = async () => {
    try {
      const response = await fetch(`/api/method/project_management.api.get_single_task?task_name=${route.params.name}`);
      const result = await response.json();
      task.value = result.message || {}; 
    } catch (err) {
      console.error('Error loading task:', err);
    }
  };
  
  onMounted(() => {
    fetchTask();
  });
  
  const goBack = () => {
    router.push('/vendor/tasks');
  };
  
  const progressColor = (progress) => {
    const validProgress = Math.max(0, Math.min(100, progress || 0));
  
    return validProgress <= 25
      ? 'bg-red-500'
      : validProgress <= 50
      ? 'bg-yellow-500'
      : validProgress <= 75
      ? 'bg-blue-500'
      : 'bg-green-500';
  };
  
  const statusBadge = (status) => {
    return {
      'bg-green-100 text-green-700': status === 'Completed',
      'bg-yellow-100 text-yellow-700': status === 'In Progress',
      'bg-red-100 text-red-700': status === 'Overdue',
      'bg-gray-100 text-gray-700': !['Completed', 'In Progress', 'Overdue'].includes(status),
    };
  };
  
  const getIcon = (type) => {
    switch (type) {
      case 'Design':
        return '🎨';
      case 'Development':
        return '💻';
      case 'Bug':
        return '🛠️';
      case 'Delivery':
        return '📦';
      default:
        return '📝';
    }
  };
  </script>
  