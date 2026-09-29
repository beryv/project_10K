<template>
    <div>
        <h1>HEADER</h1>
        <NuxtLink to="/" class="mt-6 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded transition">
            Home
        </NuxtLink>
        <NuxtLink to="/about" class="mt-6 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded transition">
            About
        </NuxtLink>
        <!-- Si la langue actuelle est fr, on affiche le bouton pour passer en 'en' -->
        <NuxtLink 
        v-if="locale === 'fr'" 
        :to="switchLocalePath('en')" 
        class="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition"
      >
        {{ $t('switch_lang') }}
      </NuxtLink>

      <!-- Sinon, on affiche le bouton pour passer en 'fr' -->
      <NuxtLink 
        v-else 
        :to="switchLocalePath('fr')" 
        class="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition"
      >
        {{ $t('switch_lang') }}
      </NuxtLink>
    </div>
</template>
<script setup lang="ts">
const { locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
</script>