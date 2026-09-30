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
          <div v-if="messages.length === 1" class="chat-suggestions">
            <button v-for="prompt in prompts" :key="prompt" type="button" @click="send(prompt)">{{ prompt }}</button>
          </div>
        </div>
        <form class="chat-entry" @submit.prevent="send(draft)">
          <input v-model="draft" aria-label="Votre message" placeholder="Posez votre question…" />
          <button type="submit" :disabled="!draft.trim()" aria-label="Envoyer"><Icon name="mdi:arrow-up" /></button>
        </form>
        <p class="chat-disclaimer">Réponses simulées pour cette démonstration.</p>
      </section>
    </Transition>
    <button class="chat-launcher" type="button" :aria-label="isOpen ? 'Fermer le chat' : 'Ouvrir KBC Pulse Copilot'" :aria-expanded="isOpen" @click="isOpen = !isOpen">
      <Icon :name="isOpen ? 'mdi:close' : 'mdi:message-processing-outline'" />
      <span v-if="!isOpen" class="chat-notification"></span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'

interface ChatMessage { role: 'assistant' | 'user'; text: string }
const isOpen = ref(false)
const draft = ref('')
const messageList = ref<HTMLElement | null>(null)
const messages = ref<ChatMessage[]>([
  { role: 'assistant', text: 'Bonjour Marc, je suis votre copilote financier. Comment puis-je vous aider aujourd’hui ?' },
])
const prompts = [
  'Puis-je financer un appartement à 300k € ?',
  'Quelle est ma couverture assurance actuelle ?',
]

function replyTo(question: string) {
  const normalized = question.toLocaleLowerCase('fr')
  if (normalized.includes('appartement') || normalized.includes('financer') || normalized.includes('prêt')) {
    return 'Avec 45 000 € de capital disponible, une simulation de prêt immobilier pourrait être pertinente. Le montant accordé dépendra toutefois de vos revenus, charges et de l’analyse complète de votre dossier.'
  }
  if (normalized.includes('assurance') || normalized.includes('couverture')) {
    return 'Votre aperçu de démonstration affiche une assurance habitation KBC. Aucun contrat auto actif n’est associé au profil mock; vous pouvez consulter la suggestion Auto pour découvrir cette recommandation.'
  }
  if (normalized.includes('invest') || normalized.includes('épargne')) {
    return 'Votre portefeuille mock affiche 12 400 €, en hausse de 4,2 % sur 30 jours. Ce chiffre est fourni à titre illustratif et ne constitue pas un conseil en investissement.'
  }
  return 'Je peux vous aider à explorer vos comptes, vos assurances ou vos possibilités de financement. Ces réponses sont simulées et ne remplacent pas un conseil personnalisé.'
}

async function send(value: string) {
  const question = value.trim()
  if (!question) return
  draft.value = ''
  messages.value.push({ role: 'user', text: question })
  await nextTick()
  if (messageList.value) messageList.value.scrollTop = messageList.value.scrollHeight
  window.setTimeout(async () => {
    messages.value.push({ role: 'assistant', text: replyTo(question) })
    await nextTick()
    if (messageList.value) messageList.value.scrollTop = messageList.value.scrollHeight
  }, 450)
}
</script>