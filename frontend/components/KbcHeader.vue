<template>
  <header class="pulse-header">
    <NuxtLink :to="localePath('/dashboard')" class="pulse-brand" aria-label="KBC Pulse AI, accueil">
      <span class="kbc-mark" aria-hidden="true"><i></i><i></i><i></i></span>
      <span class="pulse-brand-word">KBC <b>Pulse AI</b></span>
    </NuxtLink>

    <nav class="pulse-nav" aria-label="Navigation principale">
      <NuxtLink :to="localePath('/dashboard')" :class="{ 'is-current': route.path.endsWith('/dashboard') }"><Icon name="mdi:view-dashboard-outline" />Dashboard</NuxtLink>
      <NuxtLink :to="localePath('/suggestions')" :class="{ 'is-current': route.path.endsWith('/suggestions') }"><Icon name="mdi:lightning-bolt-outline" />Suggestions IA<span class="nav-count">{{ activeSuggestionCount }}</span></NuxtLink>
      <NuxtLink :to="localePath('/dashboard#accounts')"><Icon name="mdi:shield-account-outline" />Comptes & assurances</NuxtLink>
    </nav>

    <div class="header-profile">
      <span class="security-indicator"><i></i><span>Sécurité active</span></span>
      <span class="header-divider"></span>
      <div class="header-person"><span class="person-avatar">{{ initials }}</span><span><b>{{ customer.name }}</b><small>{{ customer.age }} ans · {{ customer.investorProfile }}</small></span></div>
      <button class="header-logout" type="button" title="Se déconnecter" aria-label="Se déconnecter" @click="logout"><Icon name="mdi:logout" /></button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const route = useRoute()
const localePath = useLocalePath()
const { customer, activeSuggestionCount } = await usePulseDemo()
const clientId = useCookie<string | null>('pulse_client_id')
const initials = computed(() => customer.value.name.split(' ').slice(0, 2).map((part) => part[0]).join('').toUpperCase())

async function logout() {
  clientId.value = null
  await navigateTo(localePath('/login'))
}
</script>