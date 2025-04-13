<template>
  <div class="bg-white p-4 rounded-lg shadow-md">
    <h2 class="font-bold text-lg mb-2">Assigned Tasks</h2>
    <table class="w-full border-collapse border border-gray-300">
      <thead>
        <tr class="bg-gray-100">
          <th class="border px-4 py-2">Task</th>
          <th class="border px-4 py-2">Status</th>
          <th class="border px-4 py-2">Due Date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.name">
          <td class="border px-4 py-2">{{ task.name }}</td>
          <td class="border px-4 py-2">{{ task.status }}</td>
          <td class="border px-4 py-2">{{ task.due_date }}</td>
        </tr>
        <tr v-if="tasks.length === 0">
          <td colspan="3" class="text-center py-4 text-gray-500">No tasks assigned.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

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
</script>
