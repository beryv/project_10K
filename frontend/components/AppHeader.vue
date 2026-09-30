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
    <div>
        <h1>HEADER</h1>
        <NuxtLink to="/" class="mt-6 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded transition">
            Home
        </NuxtLink>
        <NuxtLink to="/about" class="mt-6 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded transition">
            About
        </NuxtLink>
    </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
// INDISPENSABLE : On importe useLocalePath pour que les liens Home et About fonctionnent dans toutes les langues
const localePath = useLocalePath() 
</script>