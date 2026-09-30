<script setup lang="ts">
const config = useRuntimeConfig();
const { isAuthenticated, logout } = useAuth();

const handleLogout = async () => {
  const token = useCookie('auth_token');
  const apiBase = config.public.apiBase;

  if (token.value) {
    try {
      await fetch(`${apiBase}/logout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
      });
    } catch (error) {
      console.warn('Logout request failed, continuing client-side logout.', error);
    }
  }

  logout();
};
</script>

<template>
  <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm">
    <nav class="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
      <NuxtLink to="/" class="text-xl font-bold text-emerald-400">
        CoreBank
      </NuxtLink>
      <div class="flex items-center gap-3">
        <NuxtLink to="/" class="rounded px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-800">
          Home
        </NuxtLink>
        <NuxtLink to="/about" class="rounded px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-800">
          About
        </NuxtLink>
        <NuxtLink
          v-if="!isAuthenticated"
          to="/login"
          class="rounded bg-emerald-500 px-3 py-2 text-sm font-medium text-slate-950 transition hover:bg-emerald-400"
        >
          Login
        </NuxtLink>
        <button
          v-else
          type="button"
          class="rounded bg-red-500 px-3 py-2 text-sm font-medium text-white transition hover:bg-red-400"
          @click="handleLogout"
        >
          Logout
        </button>
      </div>
    </nav>
  </header>
</template>