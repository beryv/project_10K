<template>
  <AppHeader></AppHeader>
  <div class="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white">
    <h1 class="text-5xl font-bold text-emerald-400 mb-4">
      {{ $t('welcome') }}
    </h1>
    <div>
      <h1>List of all accounts</h1>
      <ul>
        <li v-if="data" v-for="account in data" >{{ account.account_number }}</li>
        <li v-else >No data Found!</li>
      </ul>
    </div>
  </div>
  <AppFooter></AppFooter>
</template> 

<script setup lang=ts>
// Fetch all accounts from the api
const { data } = await useFetch('/api/accounts')

</script>