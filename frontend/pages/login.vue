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
        <div class="story-signals"><span><Icon name="mdi:shield-check-outline" /> Données protégées</span><span><Icon name="mdi:chart-timeline-variant" /> Conseils contextualisés</span></div>
        <div class="story-art" aria-hidden="true"><span class="orbit orbit-one"></span><span class="orbit orbit-two"></span><span class="orbit orbit-three"></span><span class="art-center"><Icon name="mdi:creation" /></span><span class="art-node node-one"><Icon name="mdi:home-outline" /></span><span class="art-node node-two"><Icon name="mdi:car-outline" /></span><span class="art-node node-three"><Icon name="mdi:chart-line" /></span></div>
      </section>

      <section class="login-card" aria-labelledby="login-heading">
        <div class="login-card-icon"><Icon name="mdi:lock-outline" /></div>
        <p class="eyebrow">ESPACE PERSONNEL</p>
        <h2 id="login-heading">Content de vous revoir</h2>
        <p class="login-intro">Connectez-vous pour retrouver votre aperçu financier.</p>
        <form class="login-form" @submit.prevent="login">
          <label for="username">Identifiant ou numéro client</label>
          <div class="login-input"><Icon name="mdi:account-outline" /><input id="username" v-model.trim="credentials.username" autocomplete="username" required /></div>
          <label for="password">Mot de passe</label>
          <div class="login-input"><Icon name="mdi:lock-outline" /><input id="password" v-model="credentials.password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" required /><button type="button" class="password-toggle" :aria-label="showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'" @click="showPassword = !showPassword"><Icon :name="showPassword ? 'mdi:eye-off-outline' : 'mdi:eye-outline'" /></button></div>
          <p v-if="errorMessage" class="login-error" role="alert"><Icon name="mdi:alert-circle-outline" />{{ errorMessage }}</p>
          <button class="button-primary login-submit" type="submit" :disabled="isSubmitting"><Icon :name="isSubmitting ? 'mdi:loading' : 'mdi:lock-check-outline'" :class="{ 'spin-icon': isSubmitting }" />{{ isSubmitting ? 'Connexion…' : 'Connexion sécurisée' }}<Icon v-if="!isSubmitting" name="mdi:arrow-right" /></button>
        </form>
        <button class="demo-entry" type="button" @click="enterDemo">Explorer la démo sans identifiants <Icon name="mdi:arrow-up-right" /></button>
        <div class="security-note"><Icon name="mdi:shield-check" /><span><strong>Protection & Security Verified</strong><small>by Aikido Security</small></span><Icon name="mdi:check-decagram" class="verified-mark" /></div>
      </section>
    </div>
    <footer class="login-footer"><span>© 2026 KBC Pulse AI · Simulation uniquement</span><span>Vos actions dans cette démo n’entraînent aucune opération financière.</span></footer>
    <PulseChat />
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

definePageMeta({ layout: false })
const localePath = useLocalePath()
const credentials = reactive({ username: 'client@kbc.be', password: '' })
const isSubmitting = ref(false)
const showPassword = ref(false)
const errorMessage = ref('')
const token = useCookie<string | null>('admin_access_token', { maxAge: 30 * 60, path: '/', sameSite: 'lax' })

async function login() {
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    const form = new URLSearchParams()
    form.set('username', credentials.username)
    form.set('password', credentials.password)
    const result = await $fetch<{ access_token: string }>('/api/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    })
    token.value = result.access_token
    await navigateTo(localePath('/dashboard'))
  } catch {
    errorMessage.value = 'Identifiant ou mot de passe incorrect. Vous pouvez aussi explorer la démo.'
  } finally {
    isSubmitting.value = false
  }
}

async function enterDemo() {
  await navigateTo(localePath('/dashboard'))
}
</script>