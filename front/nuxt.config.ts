export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss'
  ],
  vite: {
    server: {
      watch: {
        usePolling: true
      }
    }
  }
})