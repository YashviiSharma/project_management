<template>
    <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-blue-100 p-6">
      <div class="bg-white rounded-2xl shadow-xl p-10 max-w-xl text-center">
        <svg
          class="mx-auto h-20 w-20 text-green-500 mb-6"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        <h1 class="text-3xl font-bold text-gray-800 mb-4">Thank You!</h1>
        <p class="text-gray-600 text-lg mb-6">
          Your deliverable has been submitted successfully. Our team will review it and get back to you shortly.
        </p>
        <router-link
          to="/vendor/dashboard"
          class="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200"
        >
          Back to Dashboard
        </router-link>
      </div>
    </div>
  </template>
  