<template>
  <main class="login-page">
    <div class="login-topline">
      <NuxtLink :to="localePath('/dashboard')" class="pulse-brand" aria-label="KBC Pulse AI">
        <span class="kbc-mark" aria-hidden="true"><i></i><i></i><i></i></span>
        <span class="pulse-brand-word">KBC <b>Pulse AI</b></span>
      </NuxtLink>
      <span class="login-demo-label"><i></i> ENVIRONNEMENT DE DÉMONSTRATION</span>
    </div>

    <div class="login-layout">
      <section class="login-story">
        <span class="story-overline"><Icon name="mdi:shield-check-outline" /> BANQUE & ASSURANCE, EN AVANCE</span>
        <h1>Votre avenir financier,<br /><em>en mouvement.</em></h1>
        <p>Des recommandations utiles, au bon moment. Découvrez une nouvelle façon d’anticiper vos projets financiers.</p>
        <div class="story-signals"><span><Icon name="mdi:database-check-outline" /> Données MariaDB de démo</span><span><Icon name="mdi:chart-timeline-variant" /> Conseils contextualisés</span></div>
        <div class="story-art" aria-hidden="true"><span class="orbit orbit-one"></span><span class="orbit orbit-two"></span><span class="orbit orbit-three"></span><span class="art-center"><Icon name="mdi:creation" /></span><span class="art-node node-one"><Icon name="mdi:home-outline" /></span><span class="art-node node-two"><Icon name="mdi:car-outline" /></span><span class="art-node node-three"><Icon name="mdi:chart-line" /></span></div>
      </section>

      <section class="login-card" aria-labelledby="login-heading">
        <div class="login-card-icon"><Icon name="mdi:account-switch-outline" /></div>
        <p class="eyebrow">ESPACE DE DÉMONSTRATION</p>
        <h2 id="login-heading">Choisissez un profil</h2>
        <p class="login-intro">Les profils disponibles sont chargés depuis la base KBC Pulse.</p>
        <form class="login-form" @submit.prevent="enterDemo">
          <label for="client-profile">Profil client</label>
          <div class="login-input"><Icon name="mdi:account-outline" /><select id="client-profile" v-model="selectedClientId" required><option v-for="profile in profileOptions" :key="profile.client_id" :value="profile.client_id">{{ profile.display_name }} · {{ profile.age }} ans</option></select></div>
          <p v-if="isLoading" class="profile-loading"><Icon name="mdi:loading" class="spin-icon" /> Chargement des profils…</p>
          <p v-if="errorMessage" class="login-error" role="alert"><Icon name="mdi:alert-circle-outline" />{{ errorMessage }}</p>
          <button class="button-primary login-submit" type="submit" :disabled="isSubmitting"><Icon :name="isSubmitting ? 'mdi:loading' : 'mdi:arrow-right-circle-outline'" :class="{ 'spin-icon': isSubmitting }" />{{ isSubmitting ? 'Ouverture…' : 'Accéder à la démonstration' }}<Icon v-if="!isSubmitting" name="mdi:arrow-right" /></button>
        </form>
        <div class="security-note"><Icon name="mdi:information-outline" /><span><strong>Accès de démonstration</strong><small>Aucune authentification bancaire ni opération réelle.</small></span></div>
      </section>
    </div>
    <footer class="login-footer"><span>© 2026 KBC Pulse AI · Simulation uniquement</span><span>Vos actions dans cette démo n’entraînent aucune opération financière.</span></footer>
    <PulseChat />
  </main>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import fallbackDb from '../data/clients_db.json'

interface DemoClient {
  client_id: string
  display_name: string
  age: number
}

definePageMeta({ layout: false })
const localePath = useLocalePath()
const clientId = useCookie<string | null>('pulse_client_id', { maxAge: 30 * 60, path: '/', sameSite: 'lax' })
const activeClientId = useState<string | null>('pulse-selected-client', () => clientId.value || 'kbc_user_2894')
const { data: profiles, pending: isLoading, error } = await useFetch<DemoClient[]>('/api/v1/clients', { key: 'pulse-demo-clients' })
const profileOptions = computed(() => profiles.value?.length ? profiles.value : fallbackDb.clients.map((item) => item.client))
const selectedClientId = ref(clientId.value || profileOptions.value[0]?.client_id || '')
const isSubmitting = ref(false)
const errorMessage = ref('')

async function enterDemo() {
  errorMessage.value = ''
  if (!profileOptions.value.some((profile) => profile.client_id === selectedClientId.value)) {
    errorMessage.value = 'Ce profil de démonstration est indisponible.'
    return
  }
  isSubmitting.value = true
  activeClientId.value = selectedClientId.value
  clientId.value = selectedClientId.value
  await navigateTo(localePath('/dashboard'))
  isSubmitting.value = false
}
</script>
