<script setup lang="ts">
const config = useRuntimeConfig();
const { login } = useAuth();
const username = ref('');
const password = ref('');
const error = ref('');
const isSubmitting = ref(false);

const hashPassword = async (value: string) => {
  const encoded = new TextEncoder().encode(value);
  const hashBuffer = await crypto.subtle.digest('SHA-256', encoded);
  return [...new Uint8Array(hashBuffer)]
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
};

const handleLogin = async () => {
  isSubmitting.value = true;
  error.value = '';

  try {
    const form = new URLSearchParams();
    form.append('username', username.value);
    form.append('password', await hashPassword(password.value));

    const response = await fetch(`${config.public.apiBase}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: form.toString(),
    });

    if (!response.ok) {
      throw new Error('Invalid username or password');
    }

    const data = await response.json();
    login(data.access_token);
    await navigateTo('/');
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Login failed';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-slate-950 px-6 py-20 text-white">
    <div class="mx-auto max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
      <h1 class="mb-6 text-3xl font-bold text-emerald-400">Admin Login</h1>

      <form class="space-y-5" @submit.prevent="handleLogin">
        <div>
          <label for="username" class="mb-2 block text-sm font-medium text-slate-200">Username</label>
          <input
            id="username"
            v-model="username"
            class="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white outline-none ring-0 transition focus:border-emerald-400"
            type="text"
          />
        </div>

        <div>
          <label for="password" class="mb-2 block text-sm font-medium text-slate-200">Password</label>
          <input
            id="password"
            v-model="password"
            class="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white outline-none ring-0 transition focus:border-emerald-400"
            type="password"
          />
        </div>

        <p v-if="error" class="text-sm text-red-400">{{ error }}</p>

        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full rounded-lg bg-emerald-500 px-4 py-3 font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {{ isSubmitting ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>
