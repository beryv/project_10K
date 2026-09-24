export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss'
  ],
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
  }
})