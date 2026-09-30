<script setup lang="ts">
const localePath = useLocalePath()
const clientId = useCookie<string | null>('pulse_client_id')
await navigateTo(localePath(clientId.value ? '/dashboard' : '/login'), { redirectCode: 302 })
</script>