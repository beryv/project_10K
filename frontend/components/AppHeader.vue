<template>
    <!-- Ajout de flex pour aligner proprement le header -->
    <div class="flex flex-wrap items-center gap-4 bg-slate-800 p-4 text-white">
        
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

        <div class="ml-auto flex items-center gap-2">
            <button
                v-if="!accessToken"
                type="button"
                class="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded transition"
                @click="loginDialogOpen = true"
            >
                <Icon name="mdi:login" class="text-xl" />
                {{ t('login') }}
            </button>
            <button
                v-else
                type="button"
                class="flex items-center gap-2 px-4 py-2 bg-rose-700 hover:bg-rose-600 rounded transition"
                @click="logout"
            >
                <Icon name="mdi:logout" class="text-xl" />
                {{ t('logout') }}
            </button>

            <!-- Si la langue actuelle est fr, on affiche le bouton pour passer en 'en' -->
            <NuxtLink
                v-if="locale === 'fr'" 
                :to="switchLocalePath('en')" 
                class="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition"
            >
                <Icon name="mdi:translate" class="text-xl text-slate-400" />
                {{ t('switch_lang') }}
            </NuxtLink>

            <!-- Sinon, on affiche le bouton pour passer en 'fr' -->
            <NuxtLink 
                v-else 
                :to="switchLocalePath('fr')" 
                class="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded transition"
            >
                <Icon name="mdi:translate" class="text-xl text-slate-400" />
                {{ t('switch_lang') }}
            </NuxtLink>
        </div>
    </div>

    <div
        v-if="loginDialogOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
        @click.self="loginDialogOpen = false"
    >
        <form
            role="dialog"
            aria-modal="true"
            aria-labelledby="login-title"
            class="w-full max-w-sm space-y-4 rounded bg-slate-800 p-6 text-white shadow-xl"
            @submit.prevent="login"
        >
            <div class="flex items-center justify-between">
                <h2 id="login-title" class="text-xl font-semibold">{{ t('login') }}</h2>
                <button type="button" class="text-slate-300 hover:text-white" :aria-label="t('close')" @click="loginDialogOpen = false">
                    <Icon name="mdi:close" class="text-xl" />
                </button>
            </div>
            <label class="block space-y-1">
                <span class="text-sm text-slate-300">{{ t('username') }}</span>
                <input v-model="credentials.username" name="username" autocomplete="username" required class="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 text-white" />
            </label>
            <label class="block space-y-1">
                <span class="text-sm text-slate-300">{{ t('password') }}</span>
                <input v-model="credentials.password" name="password" type="password" autocomplete="current-password" required class="w-full rounded border border-slate-600 bg-slate-900 px-3 py-2 text-white" />
            </label>
            <p v-if="loginError" role="alert" class="text-sm text-rose-300">{{ loginError }}</p>
            <button type="submit" :disabled="isLoggingIn" class="w-full rounded bg-emerald-600 px-4 py-2 font-medium hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60">
                {{ isLoggingIn ? t('logging_in') : t('login') }}
            </button>
        </form>
    </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

const { locale, t } = useI18n()
const switchLocalePath = useSwitchLocalePath()
// INDISPENSABLE : On importe useLocalePath pour que les liens Home et About fonctionnent dans toutes les langues
const localePath = useLocalePath()
const accessToken = useCookie<string | null>('admin_access_token', {
    default: () => null,
    maxAge: 30 * 60,
    path: '/',
    sameSite: 'lax',
})
const loginDialogOpen = ref(false)
const isLoggingIn = ref(false)
const loginError = ref('')
const credentials = reactive({ username: '', password: '' })

async function login() {
    isLoggingIn.value = true
    loginError.value = ''

    try {
        const form = new URLSearchParams()
        form.set('username', credentials.username)
        form.set('password', credentials.password)
        const result = await $fetch<{ access_token: string }>('/api/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: form.toString(),
        })

        accessToken.value = result.access_token
        credentials.password = ''
        loginDialogOpen.value = false
    } catch {
        loginError.value = t('login_error')
    } finally {
        isLoggingIn.value = false
    }
}

function logout() {
    accessToken.value = null
}
</script>