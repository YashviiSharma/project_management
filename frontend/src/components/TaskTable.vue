<template>
  <div class="mt-6">
    <div class="bg-white p-6 rounded-2xl shadow-lg">
      <h2 class="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2a4 4 0 014-4h6M9 17H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v10a2 2 0 01-2 2z" />
        </svg>
        Assigned Tasks
      </h2>

      <div v-if="tasks.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <div
          v-for="task in tasks"
          :key="task.name"
          class="border border-gray-200 rounded-2xl p-5 bg-gradient-to-tr from-white to-gray-50 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 relative"
        >
          <!-- Assignee Initials or Icon -->
          <div class="absolute -top-4 -right-4 bg-indigo-500 text-white text-xs font-bold rounded-full w-8 h-8 flex items-center justify-center shadow-lg">
            {{ task.assigned_to?.[0]?.toUpperCase() || 'A' }}
          </div>

          <!-- Task name with type icon + tooltip -->
          <div class="flex items-start justify-between mb-2">
            <h3 class="text-lg font-semibold text-gray-800 w-3/4 truncate" :title="task.name">
              {{ getIcon(task.task_type) }} {{ task.name }}
            </h3>
            <span
              class="text-xs font-semibold px-2 py-1 rounded-full whitespace-nowrap"
              :class="statusBadge(task.status)"
            >
              {{ task.status }}
            </span>
          </div>

          <!-- Priority and Due Badge -->
          <div class="flex justify-between items-center text-sm text-gray-600 mb-3">
            <span class="flex items-center gap-1">
              <span :class="priorityBadge(task.priority)">
                {{ priorityIcon(task.priority) }}
                {{ task.priority || 'Normal' }}
              </span>
            </span>
            <span :class="dateBadge(task.due_date)">
              {{ dateLabel(task.due_date) }}
            </span>
          </div>

          <!-- Progress Bar -->
          <div class="w-full bg-gray-200 rounded-full h-4 overflow-hidden mb-2">
            <div
              class="h-4 rounded-full text-[10px] text-white text-center leading-4 transition-all duration-700 ease-in-out"
              :style="{ width: `${task.progress_ || 0}%` }"
              :class="progressColor(task.progress_)"
            >
              {{ task.progress_ || 0 }}%
            </div>
          </div>

          <!-- View Button -->
          <div class="flex justify-end mt-3">
            <button
  @click="goToTask(task.name)"
  class="text-xs text-indigo-600 hover:underline"
>
  View Details
</button>          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center text-gray-500 py-10">
        <p class="text-lg">🎉 No tasks assigned right now.</p>
        <p class="text-sm">You're all caught up!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const goToTask = (taskName) => {
  router.push(`/vendor/task-detail/${taskName}`);
};
const tasks = ref([]);

const fetchTasks = async () => {
  try {
    const response = await fetch('/api/method/project_management.api.get_assigned_tasks_for_vendor');
    const result = await response.json();
    tasks.value = result.message || [];
  } catch (err) {
    console.error('Failed to load tasks:', err);
  }
};

onMounted(() => {
  fetchTasks();
});

// Status Badge
const statusBadge = (status) => {
  return {
    'bg-green-100 text-green-700': status === 'Completed',
    'bg-yellow-100 text-yellow-700': status === 'In Progress',
    'bg-red-100 text-red-700': status === 'Overdue',
    'bg-gray-100 text-gray-700': !['Completed', 'In Progress', 'Overdue'].includes(status)
  };
};

// Priority Pill
const priorityBadge = (priority) => {
  return `text-xs px-2 py-1 font-medium rounded-full ${
    priority === 'High'
      ? 'bg-red-100 text-red-700'
      : priority === 'Medium'
      ? 'bg-yellow-100 text-yellow-700'
      : 'bg-blue-100 text-blue-700'
  }`;
};

const priorityIcon = (priority) => {
  return priority === 'High' ? '🔥' : priority === 'Medium' ? '⚠️' : '🐢';
};

// Due Date Label
const dateLabel = (due) => {
  if (!due) return 'No Due Date';
  const today = new Date();
  const dueDate = new Date(due);
  const diff = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));

  if (diff < 0) return 'Overdue';
  if (diff === 0) return 'Due Today';
  return `${diff} day${diff > 1 ? 's' : ''} left`;
};

const dateBadge = (due) => {
  const today = new Date();
  const dueDate = new Date(due);
  const diff = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
  return `text-xs font-medium px-2 py-1 rounded-full ${
    diff < 0
      ? 'bg-red-100 text-red-700'
      : diff === 0
      ? 'bg-yellow-100 text-yellow-800'
      : 'bg-blue-100 text-blue-700'
  }`;
};

// Progress Bar Color
const progressColor = (progress) => {
  return progress <= 25
    ? 'bg-red-500'
    : progress <= 50
    ? 'bg-yellow-500'
    : progress <= 75
    ? 'bg-blue-500'
    : 'bg-green-500';
};

// Icons per task type
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
