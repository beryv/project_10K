<template>
  <div class="pulse-app">
    <KbcHeader />
    <main class="pulse-main">
      <div class="dashboard-title-row">
        <div><p class="eyebrow">VOTRE ESPACE PERSONNEL <span class="live-dot"></span> MIS À JOUR À L’INSTANT</p><h1>Bonjour {{ firstName }}<span class="title-period">.</span></h1><p class="page-subtitle">Votre situation financière, et les opportunités qui comptent aujourd’hui.</p></div>
        <button type="button" class="date-selector"><Icon name="mdi:calendar-month-outline" /> 30 septembre 2026 <Icon name="mdi:chevron-down" /></button>
      </div>

      <section v-if="topSuggestion" class="hero-suggestion">
        <div class="hero-copy">
          <div class="hero-kicker"><span><Icon name="mdi:creation" /> SUGGESTION IA · N° 1</span><span class="priority-badge priority-high"><i></i> PRIORITÉ HAUTE</span></div>
          <p class="hero-detected"><span class="detected-icon"><Icon name="mdi:car-outline" /></span> Achat véhicule détecté <b>· 28 sept.</b></p>
          <h2>Votre nouveau véhicule mérite<br class="desktop-break" /> la bonne protection.</h2>
          <p class="hero-description">Une assurance auto KBC adaptée à votre achat, avec <strong>15 % de réduction client</strong>.</p>
          <div class="hero-actions"><button type="button" class="button-primary" @click="activateSuggestion(topSuggestion.id)">{{ topSuggestion.cta }} <Icon name="mdi:arrow-right" /></button><button type="button" class="button-quiet" @click="showExplanation = true"><Icon name="mdi:help-circle-outline" /> Pourquoi cette suggestion ?</button></div>
          <p class="hero-footnote"><Icon name="mdi:information-outline" /> Décision à votre rythme, sans engagement.</p>
        </div>
        <div class="hero-visual" aria-label="Illustration d'assurance auto"><div class="visual-grid"></div><div class="visual-sun"></div><div class="visual-road"></div><div class="visual-car"><span class="car-window"></span><span class="car-wheel wheel-left"></span><span class="car-wheel wheel-right"></span><span class="car-light"></span></div><div class="visual-shield"><Icon name="mdi:shield-check" /></div><div class="visual-caption"><span>Protection Auto KBC</span><strong>Prête pour la route.</strong></div></div>
      </section>

      <div class="dashboard-columns">
        <div class="dashboard-primary-column">
          <section class="metric-grid" aria-label="Indicateurs financiers">
            <article class="metric-card capital-card"><div class="metric-card-heading"><span class="metric-icon cyan-icon"><Icon name="mdi:wallet-outline" /></span><span class="metric-menu"><Icon name="mdi:dots-horizontal" /></span></div><p class="metric-label">Capital disponible</p><strong class="metric-value">{{ money(customer.totalCapital) }}</strong><div class="metric-foot"><span class="metric-status"><i></i> Comptes + épargne</span><span class="metric-period">TOTAL</span></div></article>
            <article class="metric-card investment-card"><div class="metric-card-heading"><span class="metric-icon blue-icon"><Icon name="mdi:chart-box-outline" /></span><span class="trend-tag"><Icon name="mdi:trending-up" /> {{ customer.investments.trend30d }}</span></div><p class="metric-label">Investissements</p><strong class="metric-value">{{ money(customer.investments.total) }}</strong><div class="metric-foot"><span class="metric-status">Portefeuille KBC</span><span class="metric-period">30 JOURS</span></div></article>
          </section>

          <section class="surface-card cashflow-card">
            <div class="card-heading"><div><p class="eyebrow">VUE MENSUELLE</p><h2>Vos flux financiers</h2></div><button class="select-compact" type="button">Ce mois <Icon name="mdi:chevron-down" /></button></div>
            <div class="cashflow-summary"><div><span class="flow-dot income-dot"></span><span>Revenus</span><strong>3 850 €</strong></div><div><span class="flow-dot expense-dot"></span><span>Dépenses</span><strong>2 460 €</strong></div><span class="flow-net"><Icon name="mdi:arrow-top-right" /> +1 390 € net</span></div>
            <div class="chart-area" role="img" aria-label="Graphique comparant les revenus et dépenses sur les six derniers mois">
              <div class="chart-guides"><span>4k</span><span>3k</span><span>2k</span><span>1k</span><span>0</span></div>
              <div class="chart-columns"><div v-for="month in cashflow" :key="month.label" class="chart-month"><div class="bars"><span class="income-bar" :style="{ height: `${month.income}%` }"></span><span class="expense-bar" :style="{ height: `${month.expense}%` }"></span></div><small>{{ month.label }}</small></div></div>
            </div>
          </section>
        </div>

        <aside class="dashboard-secondary-column">
          <section class="surface-card payment-card">
            <div class="card-heading"><div><p class="eyebrow">À ANTICIPER</p><h2>Prochaines échéances</h2></div><span class="small-count">{{ customer.payments.length }}</span></div>
            <div class="payment-list"><article v-for="(payment, index) in customer.payments" :key="payment.label" class="payment-row"><span class="payment-icon" :class="`payment-tone-${index + 1}`"><Icon :name="index === 0 ? 'mdi:home-outline' : index === 1 ? 'mdi:shield-home-outline' : 'mdi:car-clock'" /></span><span class="payment-copy"><strong>{{ payment.label }}</strong><small>{{ payment.date }}</small></span><strong class="payment-amount">−{{ money(payment.amount) }}</strong></article></div>
            <button type="button" class="card-bottom-link" @click="notify('Liste complète des échéances (démo)')">Voir toutes les échéances <Icon name="mdi:arrow-right" /></button>
          </section>

          <section class="suggestion-shortcut"><div class="shortcut-top"><span class="shortcut-icon"><Icon name="mdi:creation" /></span><span class="new-suggestions">{{ activeSuggestionCount }} nouvelles</span></div><h2>Des idées pour la suite ?</h2><p>Vos suggestions personnalisées sont prêtes à être explorées.</p><NuxtLink :to="localePath('/suggestions')">Voir toutes les suggestions <Icon name="mdi:arrow-right" /></NuxtLink><div class="shortcut-orbit" aria-hidden="true"></div></section>
        </aside>
      </div>

      <section id="accounts" class="account-strip"><div class="account-strip-copy"><span class="account-strip-icon"><Icon name="mdi:shield-account-outline" /></span><span><strong>Comptes & assurances</strong><small>Un aperçu unifié de vos produits KBC</small></span></div><span class="product-chip"><Icon name="mdi:home-outline" /> Habitation <i class="product-active"></i></span><span class="product-chip muted-chip"><Icon name="mdi:car-outline" /> Auto <span>À découvrir</span></span><button type="button" class="icon-link" title="Voir les produits" aria-label="Voir les produits" @click="notify('Vue produits disponible bientôt (démo)')"><Icon name="mdi:arrow-right" /></button></section>

      <footer class="pulse-footer"><span><Icon name="mdi:shield-check-outline" /> Vos données restent protégées</span><span>Simulation basée sur des données fictives · Aucun conseil financier</span></footer>
    </main>

    <div v-if="showExplanation && topSuggestion" class="dialog-backdrop" @click.self="showExplanation = false"><section class="explanation-dialog" role="dialog" aria-modal="true" aria-labelledby="explanation-title"><div class="dialog-heading"><span class="dialog-icon"><Icon name="mdi:creation" /></span><button type="button" aria-label="Fermer" @click="showExplanation = false"><Icon name="mdi:close" /></button></div><p class="eyebrow">TRANSPARENCE DE LA RECOMMANDATION</p><h2 id="explanation-title">Pourquoi cette suggestion ?</h2><p class="dialog-lead">Votre achat récent pourrait signaler un nouveau besoin de couverture.</p><div class="explanation-source"><span><Icon name="mdi:receipt-text-check-outline" /></span><div><strong>Signal détecté</strong><p>{{ topSuggestion.explainability }}</p></div></div><div class="explanation-source"><span><Icon name="mdi:shield-search-outline" /></span><div><strong>Vérification portefeuille</strong><p>Aucun contrat auto actif trouvé dans les données de cette démonstration.</p></div></div><p class="explanation-note"><Icon name="mdi:information-outline" /> Cette recommandation est générée à partir de données fictives. Elle ne constitue pas une décision de crédit ou un conseil personnalisé.</p><button class="button-primary dialog-done" type="button" @click="showExplanation = false">J’ai compris</button></section></div>

    <Transition name="toast"><div v-if="toastMessage" class="pulse-toast" role="status"><Icon name="mdi:check-circle-outline" />{{ toastMessage }}</div></Transition>
    <PulseChat />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const localePath = useLocalePath()
const { customer, suggestions, activeSuggestionCount, toastMessage, notify, activateSuggestion } = usePulseDemo()
const firstName = computed(() => customer.value.name.split(' ')[0])
const topSuggestion = computed(() => suggestions.value.find((item) => item.id === 'sug-01' && item.status === 'active'))
const showExplanation = ref(false)
const cashflow = [
  { label: 'Avr', income: 69, expense: 46 },
  { label: 'Mai', income: 77, expense: 52 },
  { label: 'Juin', income: 72, expense: 58 },
  { label: 'Juil', income: 86, expense: 50 },
  { label: 'Août', income: 75, expense: 44 },
  { label: 'Sept', income: 92, expense: 59 },
]

function money(value: number) {
  return new Intl.NumberFormat('fr-BE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(value)
}
</script>