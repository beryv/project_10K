<template>
  <div class="chat-dock">
    <Transition name="chat-rise">
      <section v-if="isOpen" class="chat-panel" aria-label="KBC Pulse Copilot">
        <header class="chat-header">
          <span class="chat-orb"><Icon name="mdi:creation" /></span>
          <span class="chat-heading"><strong>KBC Pulse Copilot</strong><small>Chatbot 360° · En ligne</small></span>
          <button type="button" aria-label="Fermer le chat" @click="isOpen = false"><Icon name="mdi:close" /></button>
        </header>
        <div ref="messageList" class="chat-messages" aria-live="polite">
          <div class="chat-date">AUJOURD'HUI</div>
          <article v-for="(message, index) in messages" :key="index" class="chat-message" :class="message.role">
            <span v-if="message.role === 'assistant'" class="chat-mini-mark"><Icon name="mdi:creation" /></span>
            <p>{{ message.text }}</p>
          </article>
          <p v-if="isThinking" class="chat-thinking" role="status"><Icon name="mdi:loading" /> KBC Pulse AI analyse vos données bancaires…</p>
          <div v-if="messages.length === 1" class="chat-suggestions">
            <button v-for="prompt in prompts" :key="prompt" type="button" @click="send(prompt)">{{ prompt }}</button>
          </div>
        </div>
        <form class="chat-entry" @submit.prevent="send(draft)">
          <input v-model="draft" aria-label="Votre message" placeholder="Posez votre question…" :disabled="isThinking" />
          <button type="submit" :disabled="!draft.trim() || isThinking" aria-label="Envoyer"><Icon name="mdi:arrow-up" /></button>
        </form>
        <p class="chat-disclaimer">Données de démonstration · Vérifiez les décisions auprès de KBC.</p>
      </section>
    </Transition>
    <button class="chat-launcher" type="button" :aria-label="isOpen ? 'Fermer le chat' : 'Ouvrir KBC Pulse Copilot'" :aria-expanded="isOpen" @click="isOpen = !isOpen">
      <Icon :name="isOpen ? 'mdi:close' : 'mdi:message-processing-outline'" />
      <span v-if="!isOpen" class="chat-notification"></span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'

const { clientId, customer } = await usePulseDemo()
interface ChatMessage { role: 'assistant' | 'user'; text: string }
const isOpen = ref(false)
const draft = ref('')
const isThinking = ref(false)
const requestSequence = ref(0)
const messageList = ref<HTMLElement | null>(null)
const messages = ref<ChatMessage[]>([
  { role: 'assistant', text: `Bonjour ${customer.value.name}, je suis votre copilote financier. Comment puis-je vous aider aujourd’hui ?` },
])
const prompts = [
  'Puis-je financer un appartement à 300k € ?',
  'Quelle est ma couverture assurance actuelle ?',
]

watch([clientId, () => customer.value.name], () => {
  requestSequence.value += 1
  isThinking.value = false
  draft.value = ''
  messages.value = [{ role: 'assistant', text: `Bonjour ${customer.value.name}, je suis votre copilote financier. Comment puis-je vous aider aujourd’hui ?` }]
})

function replyTo(question: string) {
  const normalized = question.toLocaleLowerCase('fr')
  if (normalized.includes('appartement') || normalized.includes('financer') || normalized.includes('prêt')) {
    return `Avec ${new Intl.NumberFormat('fr-BE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(customer.value.totalCapital)} de capital disponible, une simulation de prêt immobilier pourrait être pertinente. Le montant accordé dépendra toutefois de vos revenus, charges et de l’analyse complète de votre dossier.`
  }
  if (normalized.includes('assurance') || normalized.includes('couverture')) {
    const contracts = customer.value.insurances.map((insurance) => insurance.insurance_type).join(', ')
    return `Votre portefeuille indique : ${contracts || 'aucune assurance active'}. Ces informations proviennent du profil de démonstration sélectionné.`
  }
  if (normalized.includes('invest') || normalized.includes('épargne')) {
    return `Votre portefeuille affiche ${new Intl.NumberFormat('fr-BE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(customer.value.investments.total)}, en évolution de ${customer.value.investments.trend30d} sur 30 jours. Cette information ne constitue pas un conseil en investissement.`
  }
  return 'Je peux vous aider à explorer vos comptes, vos assurances ou vos possibilités de financement. Ces réponses sont simulées et ne remplacent pas un conseil personnalisé.'
}

async function send(value: string) {
  const question = value.trim()
  if (!question || isThinking.value) return
  const requestId = ++requestSequence.value
  const selectedClientId = clientId.value
  draft.value = ''
  messages.value.push({ role: 'user', text: question })
  isThinking.value = true
  await nextTick()
  if (messageList.value) messageList.value.scrollTop = messageList.value.scrollHeight
  try {
    const result = await $fetch<{ response: string }>('/api/chat', {
      method: 'POST',
      body: { client_id: selectedClientId, message: question },
    })
    if (requestId !== requestSequence.value || selectedClientId !== clientId.value) return
    messages.value.push({ role: 'assistant', text: result.response })
  } catch {
    if (requestId !== requestSequence.value || selectedClientId !== clientId.value) return
    messages.value.push({ role: 'assistant', text: replyTo(question) })
  } finally {
    if (requestId === requestSequence.value) isThinking.value = false
    await nextTick()
    if (messageList.value) messageList.value.scrollTop = messageList.value.scrollHeight
  }
}
</script>