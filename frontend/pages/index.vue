<template>
  <div class="min-h-screen bg-slate-950 text-white">
    <AppHeader />
    <main class="mx-auto flex max-w-5xl flex-col items-center px-6 py-20 text-center">
      <span class="mb-4 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-4 py-1 text-sm font-medium text-emerald-300">
        Banking demo dashboard
      </span>
      <h1 class="mb-6 text-5xl font-bold tracking-tight text-white sm:text-6xl">
        Secure Core Banking API
      </h1>
      <p class="max-w-2xl text-lg text-slate-300">
        Manage branches, clients, accounts, and transactions through a clean FastAPI backend and a modern Nuxt frontend.
      </p>
      <div class="mt-10 flex flex-wrap items-center justify-center gap-4">
        <a href="/docs" target="_blank" class="rounded-lg bg-emerald-500 px-6 py-3 font-semibold text-slate-950 transition hover:bg-emerald-400">
          Open API Docs
        </a>
        <NuxtLink to="/about" class="rounded-lg border border-slate-700 px-6 py-3 font-semibold text-white transition hover:border-slate-500 hover:bg-slate-800">
          About the project
        </NuxtLink>
      </div>
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
</script>