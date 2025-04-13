<template>
    <div class="bg-white shadow-md p-4 rounded-lg text-center">
      <i :class="icon" class="text-4xl mb-2 text-blue-500"></i>
      <h2 class="font-bold text-lg">{{ title }}</h2>
      <p class="text-gray-700 text-2xl">{{ count }}</p>
    </div>
  </template>
  
  <script setup>
  defineProps({
    title: String,
    count: Number,
    icon: String,
  });
  </script>
  
  <style scoped>
  div {
    transition: transform 0.3s ease-in-out;
  }
  div:hover {
    transform: scale(1.05);
  }
  </style>
  