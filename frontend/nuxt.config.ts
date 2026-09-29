export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n',
    '@nuxt/icon',
  ],
  icon: {
    serverBundle: {
      collections: ['mdi']
    },
    fallbackToApi: false, // Interdit à Nuxt de chercher sur Internet (évite les erreurs)
    clientBundle: {
      scan: true,
    }
  },
  i18n: {
    locales: [
      { code: 'fr', iso: 'fr-FR', file: 'fr.json', name: 'Français' },
      { code: 'en', iso: 'en-US', file: 'en.json', name: 'English' }
    ],
    defaultLocale: 'fr',
     detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root'
    },
    lazy: true,
    langDir: 'locales/', // Dossier où sont stockées les traductions
    strategy: 'prefix'
  },
  vite: {
    server: {
      watch: {
        usePolling: true,
        interval: 1000 // Vérifie les changements toutes les secondes
      },
      hmr: {
        protocol: 'ws',
        clientPort: 3000
      }
    }
  },
  routeRules: {
    '/api/**': { proxy: 'http://host.docker.internal:8000/**' }
  }
})