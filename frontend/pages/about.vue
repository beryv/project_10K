<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />
    <main class="mx-auto max-w-4xl px-6 py-20">
      <h1 class="mb-6 text-4xl font-bold text-emerald-400">About this project</h1>
      <div class="space-y-4 text-slate-300">
        <p>
          This application demonstrates a simple core banking workflow built with FastAPI and Nuxt.
        </p>
        <p>
          The backend models accounts, branches, clients, employees, and transactions while the frontend provides a clean entry point for exploring the system.
        </p>
        <p>
          It is designed as a learning project and a foundation for a more production-ready financial platform.
        </p>
      </div>
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
</script>