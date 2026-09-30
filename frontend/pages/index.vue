<script setup lang="ts">
const localePath = useLocalePath()
const token = useCookie<string | null>('admin_access_token')
await navigateTo(localePath(token.value ? '/dashboard' : '/login'), { redirectCode: 302 })
</script>