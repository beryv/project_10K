<template>
  <div class="pulse-app">
    <KbcHeader />
    <main class="pulse-main">
      <div class="dashboard-title-row">
        <div><p class="eyebrow">VOTRE ESPACE PERSONNEL <span class="live-dot"></span> MIS À JOUR À L’INSTANT</p><h1>Bonjour {{ firstName }}<span class="title-period">.</span></h1><p class="page-subtitle">Votre situation financière, et les opportunités qui comptent aujourd’hui.</p></div>
        <button type="button" class="date-selector"><Icon name="mdi:calendar-month-outline" /> 30 septembre 2026 <Icon name="mdi:chevron-down" /></button>
      </div>

      <p v-if="error" class="data-error" role="alert"><Icon name="mdi:database-alert-outline" /> Données KBC indisponibles. Vérifiez que MariaDB et l’API backend sont démarrés.</p>

      <section v-if="topSuggestion" class="hero-suggestion">
        <div class="hero-copy">
          <div class="hero-kicker"><span><Icon name="mdi:creation" /> SUGGESTION IA · N° 1</span><span class="priority-badge" :class="priorityClass(topSuggestion.priority)"><i></i> {{ priorityLabel(topSuggestion.priority) }}</span></div>
          <p class="hero-detected"><span class="detected-icon"><Icon :name="topSuggestion.category === 'Assurance' ? 'mdi:car-outline' : topSuggestion.category === 'Prêt' ? 'mdi:home-city-outline' : 'mdi:chart-line'" /></span> {{ topSuggestion.sourceCategory }} <b>· {{ topSuggestion.confidence.toLocaleString('fr-BE', { style: 'percent', maximumFractionDigits: 0 }) }} de confiance</b></p>
          <h2>{{ topSuggestion.title }}</h2>
          <p class="hero-description">{{ topSuggestion.description }}</p>
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
            <div class="cashflow-summary"><div><span class="flow-dot income-dot"></span><span>Revenus</span><strong>{{ money(totalIncoming) }}</strong></div><div><span class="flow-dot expense-dot"></span><span>Dépenses</span><strong>{{ money(totalOutgoing) }}</strong></div><span class="flow-net" :class="{ 'flow-negative': monthlyNet < 0 }"><Icon :name="monthlyNet < 0 ? 'mdi:arrow-bottom-right' : 'mdi:arrow-top-right'" /> {{ money(monthlyNet) }} net</span></div>
            <div class="chart-area" role="img" aria-label="Graphique comparant les revenus et dépenses sur les six derniers mois">
              <div class="chart-guides"><span>{{ money(flowMax) }}</span><span>{{ money(flowMax * .75) }}</span><span>{{ money(flowMax * .5) }}</span><span>{{ money(flowMax * .25) }}</span><span>0 €</span></div>
              <div class="chart-columns"><div v-for="month in cashflow" :key="month.label" class="chart-month"><div class="bars"><span class="income-bar" :style="{ height: `${month.income}%` }"></span><span class="expense-bar" :style="{ height: `${month.expense}%` }"></span></div><small>{{ month.label }}</small></div></div>
            </div>
          </section>
        </div>

        <aside class="dashboard-secondary-column">
          <section class="surface-card payment-card">
            <div class="card-heading"><div><p class="eyebrow">À ANTICIPER</p><h2>Prochaines échéances</h2></div><span class="small-count">{{ customer.payments.length }}</span></div>
            <div class="payment-list"><article v-for="(payment, index) in customer.payments" :key="payment.label" class="payment-row"><span class="payment-icon" :class="`payment-tone-${index + 1}`"><Icon :name="paymentIcon(payment.label)" /></span><span class="payment-copy"><strong>{{ payment.label }}</strong><small>{{ payment.date }}</small></span><strong class="payment-amount">−{{ money(payment.amount) }}</strong></article><p v-if="!customer.payments.length" class="no-payments">Aucune échéance à venir.</p></div>
            <button type="button" class="card-bottom-link" @click="notify('Liste complète des échéances (démo)')">Voir toutes les échéances <Icon name="mdi:arrow-right" /></button>
          </section>

          <section class="suggestion-shortcut"><div class="shortcut-top"><span class="shortcut-icon"><Icon name="mdi:creation" /></span><span class="new-suggestions">{{ activeSuggestionCount }} nouvelles</span></div><h2>Des idées pour la suite ?</h2><p>Vos suggestions personnalisées sont prêtes à être explorées.</p><NuxtLink :to="localePath('/suggestions')">Voir toutes les suggestions <Icon name="mdi:arrow-right" /></NuxtLink><div class="shortcut-orbit" aria-hidden="true"></div></section>
        </aside>
      </div>

      <section id="accounts" class="account-strip"><div class="account-strip-copy"><span class="account-strip-icon"><Icon name="mdi:shield-account-outline" /></span><span><strong>Comptes & assurances</strong><small>{{ customer.insurances.length }} contrat(s) actif(s) · {{ customer.loans.filter((loan) => loan.status === 'ACTIVE').length }} prêt(s) actif(s)</small></span></div><span v-for="insurance in customer.insurances.slice(0, 2)" :key="insurance.contract_code" class="product-chip"><Icon :name="insuranceIcon(insurance.insurance_type)" /> {{ insurance.insurance_type }} <i class="product-active"></i></span><span v-if="!hasAutoInsurance" class="product-chip muted-chip"><Icon name="mdi:car-outline" /> Auto <span>À découvrir</span></span><button type="button" class="icon-link" title="Voir les produits" aria-label="Voir les produits" @click="notify('Produits chargés depuis le profil client.')"><Icon name="mdi:arrow-right" /></button></section>

      <footer class="pulse-footer"><span><Icon name="mdi:shield-check-outline" /> Vos données restent protégées</span><span>Simulation basée sur des données fictives · Aucun conseil financier</span></footer>
    </main>

    <div v-if="showExplanation && topSuggestion" class="dialog-backdrop" @click.self="showExplanation = false"><section class="explanation-dialog" role="dialog" aria-modal="true" aria-labelledby="explanation-title"><div class="dialog-heading"><span class="dialog-icon"><Icon name="mdi:creation" /></span><button type="button" aria-label="Fermer" @click="showExplanation = false"><Icon name="mdi:close" /></button></div><p class="eyebrow">TRANSPARENCE DE LA RECOMMANDATION</p><h2 id="explanation-title">Pourquoi cette suggestion ?</h2><p class="dialog-lead">{{ topSuggestion.description }}</p><div class="explanation-source"><span><Icon name="mdi:receipt-text-check-outline" /></span><div><strong>Signaux analysés</strong><p>{{ topSuggestion.explainability }}</p></div></div><div class="explanation-source"><span><Icon name="mdi:chart-donut" /></span><div><strong>Niveau de confiance</strong><p>{{ topSuggestion.confidence.toLocaleString('fr-BE', { style: 'percent', maximumFractionDigits: 0 }) }} · profil {{ customer.profile }}</p></div></div><p class="explanation-note"><Icon name="mdi:information-outline" /> Cette recommandation est basée sur les données seedées de démonstration. Elle ne constitue pas un conseil personnalisé.</p><button class="button-primary dialog-done" type="button" @click="showExplanation = false">J’ai compris</button></section></div>

    <Transition name="toast"><div v-if="toastMessage" class="pulse-toast" role="status"><Icon name="mdi:check-circle-outline" />{{ toastMessage }}</div></Transition>
    <PulseChat />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const localePath = useLocalePath()
const { customer, dashboard, pending, error, suggestions, activeSuggestionCount, toastMessage, notify, activateSuggestion } = await usePulseDemo()
const firstName = computed(() => customer.value.name.split(' ')[0])
const topSuggestion = computed(() => suggestions.value.find((item) => item.status === 'active'))
const showExplanation = ref(false)
const monthlyTransactions = computed(() => (dashboard.value?.transactions ?? []).filter((transaction) => transaction.tx_date.startsWith('2026-09')))
const totalIncoming = computed(() => monthlyTransactions.value.filter((transaction) => transaction.tx_type === 'CREDIT').reduce((sum, transaction) => sum + transaction.amount, 0))
const totalOutgoing = computed(() => monthlyTransactions.value.filter((transaction) => transaction.tx_type === 'DEBIT').reduce((sum, transaction) => sum + transaction.amount, 0))
const monthlyNet = computed(() => totalIncoming.value - totalOutgoing.value)
const flowMax = computed(() => Math.ceil(Math.max(totalIncoming.value, totalOutgoing.value, 1) / 5000) * 5000)
const cashflow = computed(() => [{ label: 'Sept', income: Math.max(5, (totalIncoming.value / flowMax.value) * 90), expense: Math.max(5, (totalOutgoing.value / flowMax.value) * 90) }])
const hasAutoInsurance = computed(() => customer.value.insurances.some((insurance) => insurance.insurance_type.toLocaleLowerCase('fr').includes('auto')))

function money(value: number) {
  return new Intl.NumberFormat('fr-BE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(value)
}

function priorityClass(priority: string) { return priority === 'HAUTE' ? 'priority-high' : priority === 'MOYENNE' ? 'priority-medium' : 'priority-low' }
function priorityLabel(priority: string) { return priority === 'HAUTE' ? 'PRIORITÉ HAUTE' : priority === 'MOYENNE' ? 'PRIORITÉ MOYENNE' : 'PRIORITÉ BASSE' }
function paymentIcon(label: string) {
  const value = label.toLocaleLowerCase('fr')
  if (value.includes('loyer')) return 'mdi:home-outline'
  if (value.includes('assurance')) return 'mdi:shield-home-outline'
  if (value.includes('prêt')) return 'mdi:bank-outline'
  return 'mdi:calendar-clock-outline'
}
function insuranceIcon(label: string) { return label.toLocaleLowerCase('fr').includes('auto') ? 'mdi:car-outline' : 'mdi:home-outline' }
</script>