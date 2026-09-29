<template>
    <!-- Ajout de flex pour aligner proprement le header -->
    <div class="flex items-center gap-4 bg-slate-800 p-4 text-white">
        
        <!-- CORRECTION : :to="localePath(...)" pour que le lien s'adapte à la langue -->
        <NuxtLink :to="localePath('/')" class="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded transition">
            <!-- J'ai ajusté la taille (text-2xl) et laissé l'icône blanche pour un bon contraste -->
            <Icon name="mdi:home" class="text-2xl" /> 
            Home
        </NuxtLink>
        
        <NuxtLink :to="localePath('/about')" class="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded transition">
            <!-- J'ai ajouté une icône pour la page About aussi ! -->
            <Icon name="mdi:information-outline" class="text-2xl" /> 
            About
        </NuxtLink>

        <div class="ml-auto">
            <!-- Si la langue actuelle est fr, on affiche le bouton pour passer en 'en' -->
            <NuxtLink 
                v-if="locale === 'fr'" 
                :to="switchLocalePath('en')" 
                class="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition"
            >
                <Icon name="mdi:translate" class="text-xl text-slate-400" />
                {{ $t('switch_lang') }}
            </NuxtLink>

            <!-- Sinon, on affiche le bouton pour passer en 'fr' -->
            <NuxtLink 
                v-else 
                :to="switchLocalePath('fr')" 
                class="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition"
            >
                <Icon name="mdi:translate" class="text-xl text-slate-400" />
                {{ $t('switch_lang') }}
            </NuxtLink>
        </div>
    </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
// INDISPENSABLE : On importe useLocalePath pour que les liens Home et About fonctionnent dans toutes les langues
const localePath = useLocalePath() 
</script>