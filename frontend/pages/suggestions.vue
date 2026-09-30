<template>
  <div class="pulse-app">
    <KbcHeader />
    <main class="pulse-main suggestions-main">
      <div class="dashboard-title-row suggestions-title-row"><div><p class="eyebrow">KBC PULSE AI <span class="live-dot"></span> {{ activeSuggestionCount }} OPPORTUNITÉS ACTIVES</p><h1>Vos prochaines décisions,<br class="mobile-break" /> en toute clarté<span class="title-period">.</span></h1><p class="page-subtitle">Des pistes personnalisées, expliquées et toujours à votre rythme.</p></div><span class="suggestions-title-mark"><Icon name="mdi:creation" /></span></div>

      <section class="suggestions-overview"><div class="overview-icon"><Icon name="mdi:lightbulb-on-outline" /></div><div><strong>Chaque suggestion a une raison d’être.</strong><span>Explorez les signaux qui ont guidé les recommandations. Vous gardez le contrôle sur chaque étape.</span></div><span class="overview-security"><Icon name="mdi:shield-check-outline" /> Vos données sont protégées</span></section>

      <div class="suggestion-toolbar"><div class="filter-tabs" role="group" aria-label="Filtrer les suggestions"><button v-for="filter in filters" :key="filter.value" type="button" :class="{ selected: activeFilter === filter.value }" @click="activeFilter = filter.value">{{ filter.label }}<span v-if="filter.value === 'all'">{{ activeSuggestionCount }}</span></button></div><button type="button" class="sort-control" @click="sortDescending = !sortDescending"><Icon name="mdi:sort-variant" /> Priorité <Icon :name="sortDescending ? 'mdi:arrow-down' : 'mdi:arrow-up'" /></button></div>

      <section v-if="visibleSuggestions.length" class="suggestions-grid" aria-label="Recommandations personnalisées">
        <article v-for="suggestion in visibleSuggestions" :key="suggestion.id" class="suggestion-card" :class="[`suggestion-${suggestion.priority.toLowerCase()}`, { 'suggestion-featured': suggestion.id === 'sug-01' }]">
          <div class="suggestion-card-head"><span class="suggestion-category"><Icon :name="categoryIcon(suggestion.category)" />{{ suggestion.category }}</span><span class="priority-badge" :class="priorityClass(suggestion.priority)"><i></i>{{ priorityLabel(suggestion.priority) }}</span></div>
          <div class="suggestion-card-icon" :class="categoryTone(suggestion.category)"><Icon :name="categoryIcon(suggestion.category)" /></div>
          <p class="suggestion-index">OPPORTUNITÉ 0{{ suggestion.id.slice(-1) }}</p>
          <h2>{{ suggestion.title }}</h2>
          <p class="suggestion-description">{{ suggestion.description }}</p>
          <div class="why-box"><div class="why-heading"><Icon name="mdi:creation" /> POURQUOI CETTE SUGGESTION ?</div><p>{{ suggestion.explainability }}</p></div>
          <div class="suggestion-card-actions"><button type="button" class="button-primary" @click="activateSuggestion(suggestion.id)">{{ suggestion.cta }} <Icon name="mdi:arrow-right" /></button><button type="button" class="ignore-button" @click="dismissSuggestion(suggestion.id)"><Icon name="mdi:close" /> Ignorer</button></div>
          <p class="suggestion-disclaimer"><Icon name="mdi:information-outline" /> Confiance {{ suggestion.confidence.toLocaleString('fr-BE', { style: 'percent', maximumFractionDigits: 0 }) }} · Recommandation simulée</p>
        </article>
      </section>
      <section v-else class="empty-suggestions"><span><Icon name="mdi:check-circle-outline" /></span><h2>Tout est à jour</h2><p>Aucune suggestion ne correspond à ce filtre. Revenez explorer vos opportunités plus tard.</p><button type="button" class="button-secondary" @click="activeFilter = 'all'">Voir toutes les suggestions</button></section>

      <section class="suggestions-privacy"><span><Icon name="mdi:lock-check-outline" /></span><div><strong>Vous gardez la main</strong><p>Une suggestion est une piste, pas une décision. Vous pouvez l’explorer, l’ignorer ou demander l’avis d’un conseiller.</p></div><button type="button" class="text-button" @click="notify('Centre de confidentialité (démo)')">En savoir plus <Icon name="mdi:arrow-right" /></button></section>
      <footer class="pulse-footer"><span><Icon name="mdi:shield-check-outline" /> Vos données restent protégées</span><span>Simulation basée sur des données fictives · Aucun conseil financier</span></footer>
    </main>
    <Transition name="toast"><div v-if="toastMessage" class="pulse-toast" role="status"><Icon name="mdi:check-circle-outline" />{{ toastMessage }}</div></Transition>
    <PulseChat />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const { suggestions, activeSuggestionCount, toastMessage, activateSuggestion, dismissSuggestion, notify } = await usePulseDemo()
const activeFilter = ref('all')
const sortDescending = ref(true)
const filters = [
  { value: 'all', label: 'Tout' },
  { value: 'high', label: 'Priorité haute' },
  { value: 'Assurance', label: 'Assurances' },
  { value: 'Prêt', label: 'Prêts & crédits' },
  { value: 'Investissement', label: 'Épargne & investissement' },
]
const visibleSuggestions = computed(() => {
  const active = suggestions.value.filter((item) => item.status === 'active')
  const filtered = activeFilter.value === 'all' ? active : activeFilter.value === 'high' ? active.filter((item) => item.priority === 'HAUTE') : active.filter((item) => item.category === activeFilter.value)
  return [...filtered].sort((a, b) => sortDescending.value ? priorityRank(a.priority) - priorityRank(b.priority) : priorityRank(b.priority) - priorityRank(a.priority))
})

function priorityRank(priority: string) { return priority === 'HAUTE' ? 0 : priority === 'MOYENNE' ? 1 : 2 }
function priorityClass(priority: string) { return priority === 'HAUTE' ? 'priority-high' : priority === 'MOYENNE' ? 'priority-medium' : 'priority-low' }
function priorityLabel(priority: string) { return priority === 'HAUTE' ? 'PRIORITÉ HAUTE' : priority === 'MOYENNE' ? 'PRIORITÉ MOYENNE' : 'PRIORITÉ BASSE' }
function categoryIcon(category: string) { return category === 'Assurance' ? 'mdi:shield-check-outline' : category === 'Prêt' ? 'mdi:home-city-outline' : 'mdi:chart-line' }
function categoryTone(category: string) { return category === 'Assurance' ? 'tone-cyan' : category === 'Prêt' ? 'tone-blue' : 'tone-green' }
</script>