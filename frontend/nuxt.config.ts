export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n'
  ],
  i18n: {
    locales: [
      { code: 'fr', iso: 'fr-FR', file: 'fr.json', name: 'Français' },
      { code: 'en', iso: 'en-US', file: 'en.json', name: 'English' }
    ],
    defaultLocale: 'fr',
    lazy: true,
    langDir: 'locales/', // Dossier où seront stockées les traductions
    strategy: 'prefix_except_default' // Les URLs en anglais auront /en/
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