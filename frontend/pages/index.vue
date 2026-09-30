<template>
  <div class="bank-shell">
    <aside class="sidebar">
      <NuxtLink to="/" class="brand" aria-label="Aster Bank home">
        <span class="brand-mark"><Icon name="mdi:asterisk" /></span>
        <span class="brand-name">aster<span>bank</span></span>
      </NuxtLink>

      <div class="environment-tag"><span></span> SIMULATION ENVIRONMENT</div>

      <nav class="side-nav" aria-label="Main navigation">
        <p class="nav-label">YOUR MONEY</p>
        <a class="nav-link active" href="#overview"><Icon name="mdi:view-dashboard-outline" /> Overview</a>
        <a class="nav-link" href="#accounts"><Icon name="mdi:wallet-outline" /> Accounts</a>
        <a class="nav-link" href="#activity"><Icon name="mdi:swap-horizontal" /> Activity</a>
      </nav>

      <div class="sidebar-bottom">
        <div class="help-line"><Icon name="mdi:shield-check-outline" /><span>Sandbox mode<br /><small>No real money moves</small></span></div>
        <div class="profile">
          <div class="avatar">{{ initials }}</div>
          <div class="profile-copy"><strong>{{ customerName }}</strong><span>Personal account</span></div>
          <Icon name="mdi:chevron-down" class="profile-chevron" />
        </div>
      </div>
    </aside>

    <main class="main-content">
      <header class="topbar">
        <div class="breadcrumbs">Personal banking <Icon name="mdi:chevron-right" /> <strong>Overview</strong></div>
        <div class="topbar-right">
          <span class="sandbox-pill"><span></span> Demo workspace</span>
          <button class="icon-button" type="button" aria-label="Notifications"><Icon name="mdi:bell-outline" /><i></i></button>
        </div>
      </header>

      <div class="content-wrap" id="overview">
        <div class="welcome-row">
          <div>
            <p class="eyebrow">MONDAY, {{ todayLabel }}</p>
            <h1>Welcome back, {{ firstName }}<span class="heading-dot">.</span></h1>
            <p class="welcome-subtitle">Here’s what’s happening with your money.</p>
          </div>
          <button class="open-account-button" type="button" @click="openAction('account')">
            <Icon name="mdi:plus" /> Open an account
          </button>
        </div>

        <p v-if="loadError" class="banner error-banner" role="alert"><Icon name="mdi:alert-circle-outline" /> {{ loadError }}</p>

        <section class="balance-panel" aria-label="Total balance">
          <div class="balance-main">
            <div class="balance-label"><span class="balance-spark"><Icon name="mdi:chart-line-variant" /></span> TOTAL BALANCE <span class="balance-period">ACROSS {{ accounts.length }} ACCOUNTS</span></div>
            <div v-if="pending" class="balance-value loading-value">Loading balance…</div>
            <div v-else class="balance-value">{{ money(totalBalance) }}</div>
            <div class="balance-footnote"><span class="positive-mark"><Icon name="mdi:arrow-top-right" /></span> Your accounts are up to date</div>
          </div>
          <div class="balance-divider"></div>
          <div class="balance-stat">
            <span class="stat-icon incoming"><Icon name="mdi:arrow-bottom-left" /></span>
            <div><span class="stat-label">Money in</span><strong>{{ money(totalIncoming) }}</strong><small>This month</small></div>
          </div>
          <div class="balance-stat">
            <span class="stat-icon outgoing"><Icon name="mdi:arrow-top-right" /></span>
            <div><span class="stat-label">Money out</span><strong>{{ money(totalOutgoing) }}</strong><small>This month</small></div>
          </div>
          <div class="balance-pattern" aria-hidden="true"></div>
        </section>

        <section class="quick-actions" aria-label="Quick actions">
          <button class="action-button action-primary" type="button" @click="openAction('deposit')"><span class="action-icon"><Icon name="mdi:arrow-down-left" /></span><span>Add money</span></button>
          <button class="action-button" type="button" @click="openAction('payment')"><span class="action-icon"><Icon name="mdi:arrow-up-right" /></span><span>Pay someone</span></button>
          <button class="action-button" type="button" :disabled="accounts.length < 2" @click="openAction('transfer')"><span class="action-icon"><Icon name="mdi:swap-horizontal" /></span><span>Move between accounts</span></button>
          <span class="action-note"><Icon name="mdi:lock-outline" /> All activity is simulated</span>
        </section>

        <section id="accounts" class="section-block">
          <div class="section-heading">
            <div><p class="eyebrow">YOUR PORTFOLIO</p><h2>Your accounts <span class="count-badge">{{ accounts.length }}</span></h2></div>
            <button class="text-link" type="button" @click="openAction('account')">Add account <Icon name="mdi:arrow-right" /></button>
          </div>
          <div v-if="pending" class="account-grid"><div v-for="index in 2" :key="index" class="account-card skeleton-card"></div></div>
          <div v-else-if="accounts.length" class="account-grid">
            <article v-for="account in accounts" :key="account.id" class="account-card" :class="accountTone(account.account_type)">
              <div class="account-card-top">
                <span class="account-icon"><Icon :name="accountIcon(account.account_type)" /></span>
                <span class="account-kind">{{ accountLabel(account.account_type) }}</span>
                <button class="more-button" type="button" :aria-label="`More options for ${accountLabel(account.account_type)}`"><Icon name="mdi:dots-horizontal" /></button>
              </div>
              <p class="account-balance">{{ money(account.balance) }}</p>
              <div class="account-card-bottom"><span>ACCOUNT NUMBER</span><span>•••• {{ account.account_number.slice(-4) }}</span></div>
            </article>
          </div>
          <div v-else class="empty-state">No accounts yet. Open an account to get started.</div>
        </section>

        <section id="cards" class="section-block cards-section">
          <div class="section-heading">
            <div><p class="eyebrow">PAYMENTS, YOUR WAY</p><h2>Virtual cards <span class="count-badge">{{ cards.length }}</span></h2></div>
            <button class="text-link" type="button" :disabled="accounts.length === 0" @click="openAction('card')"><Icon name="mdi:plus" /> Create card</button>
          </div>
          <div v-if="pending" class="card-grid"><div v-for="index in 2" :key="index" class="virtual-card skeleton-card"></div></div>
          <div v-else-if="cards.length" class="card-grid">
            <article v-for="card in cards" :key="card.id" class="virtual-card" :class="card.card_type.toLowerCase()">
              <div class="virtual-card-face" :class="{ 'face-frozen': card.status !== 'Active' }">
                <div class="virtual-card-head"><span class="card-brand">aster<span>bank</span></span><span class="card-type-label">VIRTUAL · {{ card.card_type.toUpperCase() }}</span></div>
                <div class="card-chip-row"><span class="card-chip" aria-hidden="true"></span><Icon name="mdi:contactless-payment" class="contactless-icon" /></div>
                <div class="card-number">•••• &nbsp;•••• &nbsp;•••• &nbsp;{{ card.last_four }}</div>
                <div class="virtual-card-foot"><span><small>CARDHOLDER</small>{{ card.cardholder_name }}</span><span><small>VALID THRU</small>{{ expiryLabel(card) }}</span><strong>SIM</strong></div>
                <span class="card-state" :class="`state-${card.status.toLowerCase()}`">{{ card.status }}</span>
              </div>
              <div class="card-info-row">
                <span>{{ accountLabel(accountFor(card.account_id)?.account_type || 'Account') }}</span>
                <strong v-if="card.card_type === 'Credit'">{{ money(Number(card.credit_limit) - Number(card.outstanding_balance)) }} available</strong>
                <strong v-else>Purchase limit {{ money(card.spending_limit) }}</strong>
              </div>
              <div v-if="card.card_type === 'Credit'" class="credit-balance-row"><span>Outstanding balance</span><strong>{{ money(card.outstanding_balance) }}</strong></div>
              <div class="card-actions">
                <button type="button" @click="openCardDetails(card)"><Icon name="mdi:eye-outline" /> View details</button>
                <button type="button" :disabled="card.status === 'Closed'" @click="openAction('cardPurchase', card)"><Icon name="mdi:cart-outline" /> Purchase</button>
                <button type="button" :disabled="card.status === 'Closed'" @click="openAction('cardControls', card)"><Icon name="mdi:tune-variant" /> Controls</button>
                <button type="button" :disabled="card.status === 'Closed'" @click="changeCardStatus(card, card.status === 'Active' ? 'Frozen' : 'Active')"><Icon :name="card.status === 'Active' ? 'mdi:snowflake' : 'mdi:play-circle-outline'" /> {{ card.status === 'Active' ? 'Freeze' : 'Unfreeze' }}</button>
                <button v-if="card.card_type === 'Credit' && Number(card.outstanding_balance) > 0" type="button" @click="openAction('cardPayment', card)"><Icon name="mdi:cash-check" /> Pay balance</button>
                <button type="button" class="close-card-action" :disabled="card.status === 'Closed'" @click="changeCardStatus(card, 'Closed')"><Icon name="mdi:close-circle-outline" /> Close</button>
              </div>
            </article>
          </div>
          <div v-else class="card-empty-state"><span class="card-empty-icon"><Icon name="mdi:credit-card-plus-outline" /></span><strong>No virtual cards yet</strong><span>Create a debit card for everyday spending or a credit card for simulated purchases.</span><button class="text-link" type="button" :disabled="accounts.length === 0" @click="openAction('card')">Create your first card <Icon name="mdi:arrow-right" /></button></div>

          <div v-if="cardTransactions.length" class="card-activity">
            <div class="card-activity-heading"><h3>Card activity</h3><span>Latest simulated purchases and payments</span></div>
            <div v-for="activity in cardTransactions.slice(0, 4)" :key="activity.id" class="card-activity-row">
              <span class="card-activity-icon" :class="activity.transaction_type.toLowerCase()"><Icon :name="activity.transaction_type === 'Payment' ? 'mdi:arrow-bottom-left' : 'mdi:shopping-outline'" /></span>
              <span class="card-activity-copy"><strong>{{ activity.merchant }}</strong><small>{{ cardById(activity.card_id)?.card_type || 'Virtual' }} card · {{ dateLabel(activity.timestamp) }}</small></span>
              <strong class="card-activity-amount" :class="activity.transaction_type === 'Payment' ? 'amount-positive' : 'amount-negative'">{{ activity.transaction_type === 'Payment' ? '+' : '' }}{{ money(activity.amount) }}</strong>
            </div>
          </div>
        </section>

        <section id="activity" class="section-block activity-section">
          <div class="section-heading activity-heading">
            <div><p class="eyebrow">THE LATEST</p><h2>Recent activity</h2></div>
            <button class="filter-button" type="button" @click="showAllActivity = !showAllActivity"><Icon name="mdi:tune-variant" /> {{ showAllActivity ? 'Recent' : 'All activity' }} <Icon name="mdi:chevron-down" /></button>
          </div>
          <div class="activity-table-wrap">
            <table class="activity-table">
              <thead><tr><th>TRANSACTION</th><th>ACCOUNT</th><th>DATE</th><th class="amount-column">AMOUNT</th></tr></thead>
              <tbody>
                <tr v-for="transaction in displayedTransactions" :key="transaction.id">
                  <td><div class="transaction-cell"><span class="transaction-icon" :class="isCredit(transaction.transaction_type) ? 'credit' : 'debit'"><Icon :name="transactionIcon(transaction.transaction_type)" /></span><span><strong>{{ transaction.description || transaction.transaction_type }}</strong><small>{{ transaction.transaction_type }}</small></span></div></td>
                  <td><span class="table-account">{{ accountLabel(accountFor(transaction.account_id)?.account_type || 'Account') }}</span></td>
                  <td class="date-cell">{{ dateLabel(transaction.timestamp) }}</td>
                  <td class="amount-column"><strong :class="isCredit(transaction.transaction_type) ? 'amount-positive' : 'amount-negative'">{{ isCredit(transaction.transaction_type) ? '+' : '−' }}{{ money(transaction.amount) }}</strong></td>
                </tr>
              </tbody>
            </table>
            <div v-if="!pending && transactions.length === 0" class="empty-activity"><span class="empty-icon"><Icon name="mdi:swap-horizontal" /></span><strong>Your activity will show here</strong><span>Simulate a deposit or payment to get started.</span></div>
          </div>
        </section>

        <footer class="page-footer"><span>ASTER BANK · SIMULATION ONLY</span><span>Accounts and payments are fictional and have no real-world value.</span></footer>
      </div>
    </main>

    <Transition name="toast"><div v-if="toastMessage" class="toast-message" role="status"><Icon name="mdi:check-circle" /> {{ toastMessage }}</div></Transition>

    <div v-if="activeAction" class="modal-backdrop" @click.self="closeAction">
      <section class="action-modal" role="dialog" aria-modal="true" :aria-labelledby="'modal-title'">
        <div class="modal-topline"><span class="modal-icon"><Icon :name="modalIcon" /></span><button class="icon-button modal-close" type="button" aria-label="Close" @click="closeAction"><Icon name="mdi:close" /></button></div>
        <p class="eyebrow">SIMULATED TRANSACTION</p>
        <h2 id="modal-title">{{ modalTitle }}</h2>
        <p class="modal-description">{{ modalDescription }}</p>

        <form class="action-form" @submit.prevent="submitAction">
          <template v-if="activeAction === 'card'">
            <label>Card type<select v-model="cardForm.card_type"><option value="Debit">Debit card</option><option value="Credit">Credit card</option></select></label>
            <label>Link to account<select v-model.number="cardForm.account_id" required><option v-for="account in accounts" :key="account.id" :value="account.id">{{ accountLabel(account.account_type) }} · {{ money(account.balance) }}</option></select></label>
            <label v-if="cardForm.card_type === 'Credit'">Credit limit<div class="amount-input"><span>$</span><input v-model="cardForm.credit_limit" type="number" min="100" max="50000" step="100" required /></div></label>
            <label>Maximum per purchase<div class="amount-input"><span>$</span><input v-model="cardForm.spending_limit" type="number" min="0.01" max="1000000" step="0.01" required /></div></label>
            <p class="modal-notice"><Icon name="mdi:shield-check-outline" /> This simulator stores no full card number or security code. Card details are fictional.</p>
          </template>
          <template v-else-if="activeAction === 'cardPurchase'">
            <p class="selected-card-note"><Icon name="mdi:credit-card-outline" /> {{ selectedCard?.card_type }} ·•••• {{ selectedCard?.last_four }}</p>
            <label>Merchant<input v-model.trim="cardPurchaseForm.merchant" type="text" maxlength="80" placeholder="Coffee shop" required /></label>
            <label>Purchase amount<div class="amount-input"><span>$</span><input v-model="amountValue" type="number" min="0.01" :max="selectedCard?.spending_limit || 1000000" step="0.01" placeholder="0.00" required /></div></label>
          </template>
          <template v-else-if="activeAction === 'cardControls'">
            <p class="selected-card-note"><Icon name="mdi:credit-card-outline" /> {{ selectedCard?.card_type }} ·•••• {{ selectedCard?.last_four }}</p>
            <label>Maximum per purchase<div class="amount-input"><span>$</span><input v-model="cardControlsForm.spending_limit" type="number" min="0.01" :max="selectedCard?.card_type === 'Credit' ? selectedCard.credit_limit : 1000000" step="0.01" required /></div></label>
            <p v-if="selectedCard?.card_type === 'Credit'" class="modal-notice"><Icon name="mdi:information-outline" /> Your purchase limit can’t exceed the {{ money(selectedCard.credit_limit) }} credit line.</p>
          </template>
          <template v-else-if="activeAction === 'cardPayment'">
            <p class="selected-card-note"><Icon name="mdi:credit-card-outline" /> Pay {{ selectedCard?.card_type }} ·•••• {{ selectedCard?.last_four }} · {{ money(selectedCard?.outstanding_balance || 0) }} owed</p>
            <label>Pay from<select v-model.number="cardPaymentAccountId" required><option v-for="account in accounts" :key="account.id" :value="account.id">{{ accountLabel(account.account_type) }} · {{ money(account.balance) }}</option></select></label>
            <label>Payment amount<div class="amount-input"><span>$</span><input v-model="amountValue" type="number" min="0.01" :max="selectedCard?.outstanding_balance || 0" step="0.01" placeholder="0.00" required /></div></label>
          </template>
          <template v-else-if="activeAction === 'account'">
            <label>Account type<select v-model="accountForm.account_type" required><option v-for="type in availableAccountTypes" :key="type" :value="type">{{ type }} account</option></select></label>
            <div class="modal-notice"><Icon name="mdi:information-outline" /> This account will be created with a zero balance.</div>
          </template>
          <template v-else>
            <label v-if="activeAction !== 'transfer'">{{ activeAction === 'payment' ? 'Pay from' : 'Deposit to' }}<select v-model.number="singleAccountId" required><option v-for="account in accounts" :key="account.id" :value="account.id">{{ accountLabel(account.account_type) }} · {{ money(account.balance) }}</option></select></label>
            <template v-else>
              <label>From<select v-model.number="transferForm.source_account_id" required><option v-for="account in accounts" :key="account.id" :value="account.id">{{ accountLabel(account.account_type) }} · {{ money(account.balance) }}</option></select></label>
              <button class="swap-accounts" type="button" aria-label="Swap accounts" @click="swapAccounts"><Icon name="mdi:swap-vertical" /></button>
              <label>To<select v-model.number="transferForm.destination_account_id" required><option v-for="account in accounts" :key="account.id" :value="account.id" :disabled="account.id === transferForm.source_account_id">{{ accountLabel(account.account_type) }} · {{ money(account.balance) }}</option></select></label>
            </template>
            <label v-if="activeAction === 'payment'">Recipient<input v-model.trim="paymentForm.recipient" type="text" maxlength="80" placeholder="Name or business" required /></label>
            <label>Amount<div class="amount-input"><span>$</span><input v-model="amountValue" type="number" min="0.01" max="1000000" step="0.01" placeholder="0.00" required /></div></label>
            <p v-if="activeAction === 'payment'" class="modal-notice"><Icon name="mdi:information-outline" /> This payment is a simulation. No money will leave this app.</p>
          </template>
          <p v-if="actionError" class="form-error" role="alert"><Icon name="mdi:alert-circle-outline" /> {{ actionError }}</p>
          <div class="modal-actions"><button class="cancel-button" type="button" @click="closeAction">Cancel</button><button class="submit-button" type="submit" :disabled="isSubmitting"><Icon v-if="isSubmitting" name="mdi:loading" class="spin" />{{ isSubmitting ? 'Processing…' : modalSubmitLabel }}</button></div>
        </form>
      </section>
    </div>

    <div v-if="showCardDetails" class="modal-backdrop" @click.self="closeCardDetails">
      <section class="action-modal card-details-modal" role="dialog" aria-modal="true" aria-labelledby="card-details-title">
        <div class="modal-topline"><span class="modal-icon"><Icon name="mdi:credit-card-outline" /></span><button class="icon-button modal-close" type="button" aria-label="Close card details" @click="closeCardDetails"><Icon name="mdi:close" /></button></div>
        <p class="eyebrow">SIMULATED CARD DETAILS</p>
        <h2 id="card-details-title">{{ detailsCard?.card_type }} card</h2>
        <p class="modal-description">Fictional details for this simulator only. This number cannot be used for payments.</p>
        <p v-if="cardDetailsError" class="form-error" role="alert"><Icon name="mdi:alert-circle-outline" /> {{ cardDetailsError }}</p>
        <p v-else-if="isLoadingCardDetails" class="details-loading"><Icon name="mdi:loading" class="spin" /> Loading card details…</p>
        <div v-else-if="cardDetails" class="card-details-list">
          <div class="card-detail-row"><div><span>Card number</span><strong class="detail-number">{{ cardDetails.card_number }}</strong></div><button class="detail-copy" type="button" aria-label="Copy demo card number" title="Copy demo card number" @click="copyCardDetail(cardDetails.card_number, 'Demo card number')"><Icon name="mdi:content-copy" /></button></div>
          <div class="card-details-pair">
            <div class="card-detail-row"><div><span>Expiry date</span><strong>{{ expiryLabel(cardDetails) }}</strong></div></div>
            <div class="card-detail-row"><div><span>Security code</span><strong class="detail-number">{{ cardDetails.security_code }}</strong></div><button class="detail-copy" type="button" aria-label="Copy demo security code" title="Copy demo security code" @click="copyCardDetail(cardDetails.security_code, 'Demo security code')"><Icon name="mdi:content-copy" /></button></div>
          </div>
          <div class="card-detail-row"><div><span>Cardholder</span><strong>{{ cardDetails.cardholder_name }}</strong></div><span class="detail-status">{{ cardDetails.status }}</span></div>
          <div class="modal-notice"><Icon name="mdi:shield-alert-outline" /> Starts with 0000 and uses a 000 security code. These details are deliberately invalid and never sent to payment networks.</div>
        </div>
        <div class="modal-actions"><button class="cancel-button" type="button" @click="closeCardDetails">Close</button></div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

interface BankAccount {
  id: number
  account_number: string
  balance: number
  account_type: string
  client_id: number
}

interface BankTransaction {
  id: number
  amount: number
  transaction_type: string
  description: string | null
  timestamp: string
  account_id: number
}

interface VirtualCard {
  id: number
  last_four: string
  card_type: 'Debit' | 'Credit'
  cardholder_name: string
  status: 'Active' | 'Frozen' | 'Closed'
  expiration_month: number
  expiration_year: number
  spending_limit: number
  credit_limit: number
  outstanding_balance: number
  account_id: number
}

interface CardActivity {
  id: number
  amount: number
  transaction_type: 'Purchase' | 'Payment'
  merchant: string
  timestamp: string
  card_id: number
}

interface CardDetails {
  card_number: string
  cardholder_name: string
  expiration_month: number
  expiration_year: number
  security_code: string
  status: string
  simulation_only: boolean
}

interface Dashboard {
  client: { id: number; name: string; email: string }
  accounts: BankAccount[]
  transactions: BankTransaction[]
  cards: VirtualCard[]
  card_transactions: CardActivity[]
}

type ActionType = 'deposit' | 'payment' | 'transfer' | 'account' | 'card' | 'cardPurchase' | 'cardPayment' | 'cardControls'

const { data: dashboard, pending, error, refresh } = await useFetch<Dashboard>('/api/demo/dashboard')
const activeAction = ref<ActionType | null>(null)
const isSubmitting = ref(false)
const actionError = ref('')
const loadError = computed(() => error.value ? 'Could not reach the demo banking service. Check that the backend is running.' : '')
const toastMessage = ref('')
const amountValue = ref('')
const singleAccountId = ref<number>()
const showAllActivity = ref(false)
const paymentForm = reactive({ recipient: '' })
const transferForm = reactive({ source_account_id: 0, destination_account_id: 0 })
const accountForm = reactive<{ account_type: 'Current' | 'Savings' }>({ account_type: 'Current' })
const cardForm = reactive<{ account_id: number; card_type: 'Debit' | 'Credit'; spending_limit: string; credit_limit: string }>({ account_id: 0, card_type: 'Debit', spending_limit: '500.00', credit_limit: '1000.00' })
const cardPurchaseForm = reactive({ merchant: '' })
const cardControlsForm = reactive({ spending_limit: '' })
const cardPaymentAccountId = ref(0)
const selectedCardId = ref<number | null>(null)
const showCardDetails = ref(false)
const isLoadingCardDetails = ref(false)
const cardDetailsError = ref('')
const cardDetails = ref<CardDetails | null>(null)
const detailsCard = ref<VirtualCard | null>(null)

const accounts = computed(() => dashboard.value?.accounts ?? [])
const transactions = computed(() => dashboard.value?.transactions ?? [])
const cards = computed(() => dashboard.value?.cards ?? [])
const cardTransactions = computed(() => dashboard.value?.card_transactions ?? [])
const selectedCard = computed(() => cards.value.find((card) => card.id === selectedCardId.value))
const customerName = computed(() => dashboard.value?.client.name || 'Demo Customer')
const firstName = computed(() => customerName.value.split(' ')[0])
const initials = computed(() => customerName.value.split(' ').slice(0, 2).map((part) => part[0]).join('').toUpperCase())
const totalBalance = computed(() => accounts.value.reduce((sum, account) => sum + Number(account.balance), 0))
const currentMonthTransactions = computed(() => transactions.value.filter((transaction) => {
  const transactionDate = new Date(transaction.timestamp)
  const currentDate = new Date()
  return transactionDate.getMonth() === currentDate.getMonth() && transactionDate.getFullYear() === currentDate.getFullYear()
}))
const totalIncoming = computed(() => currentMonthTransactions.value.filter((item) => isCredit(item.transaction_type)).reduce((sum, item) => sum + Number(item.amount), 0))
const totalOutgoing = computed(() => currentMonthTransactions.value.filter((item) => !isCredit(item.transaction_type)).reduce((sum, item) => sum + Number(item.amount), 0))
const displayedTransactions = computed(() => showAllActivity.value ? transactions.value : transactions.value.slice(0, 6))
const availableAccountTypes = computed(() => {
  return ['Current', 'Savings'] as const
})
const todayLabel = new Intl.DateTimeFormat('en-US', { month: 'long', day: 'numeric', year: 'numeric' }).format(new Date()).toUpperCase()

const modalTitle = computed(() => ({ deposit: 'Add money', payment: 'Pay someone', transfer: 'Move money', account: 'Open an account', card: 'Create a virtual card', cardPurchase: 'Simulate a card purchase', cardPayment: 'Pay credit balance', cardControls: 'Card spending controls' }[activeAction.value || 'deposit']))
const modalDescription = computed(() => ({
  deposit: 'Simulate an incoming payment to one of your accounts.',
  payment: 'Create a simulated payment to an external recipient.',
  transfer: 'Move funds between your current and savings accounts.',
  account: 'Choose an account type to add to your portfolio.',
  card: 'Issue a virtual debit or credit card linked to one of your accounts.',
  cardPurchase: 'Simulate a purchase using this virtual card.',
  cardPayment: 'Pay down this card’s balance from one of your accounts.',
  cardControls: 'Set the maximum amount allowed for a single purchase.',
}[activeAction.value || 'deposit']))
const modalSubmitLabel = computed(() => ({ deposit: 'Add money', payment: 'Review payment', transfer: 'Transfer funds', account: 'Open account', card: 'Issue card', cardPurchase: 'Simulate purchase', cardPayment: 'Pay balance', cardControls: 'Save controls' }[activeAction.value || 'deposit']))
const modalIcon = computed(() => ({ deposit: 'mdi:arrow-down-left', payment: 'mdi:arrow-top-right', transfer: 'mdi:swap-horizontal', account: 'mdi:wallet-plus-outline', card: 'mdi:credit-card-plus-outline', cardPurchase: 'mdi:cart-outline', cardPayment: 'mdi:cash-check', cardControls: 'mdi:tune-variant' }[activeAction.value || 'deposit']))

function money(value: number | string) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(value || 0))
}

function accountLabel(type: string) {
  if (type.toLowerCase() === 'checking') return 'Current account'
  if (type.toLowerCase() === 'current') return 'Current account'
  if (type.toLowerCase() === 'savings') return 'Savings account'
  return type
}

function accountTone(type: string) {
  return type.toLowerCase() === 'savings' ? 'savings-card' : 'current-card'
}

function accountIcon(type: string) {
  return type.toLowerCase() === 'savings' ? 'mdi:bank-outline' : 'mdi:credit-card-outline'
}

function accountFor(id: number) {
  return accounts.value.find((account) => account.id === id)
}

function cardById(id: number) {
  return cards.value.find((card) => card.id === id)
}

function expiryLabel(card: VirtualCard | CardDetails) {
  return `${String(card.expiration_month).padStart(2, '0')}/${String(card.expiration_year).slice(-2)}`
}

async function openCardDetails(card: VirtualCard) {
  detailsCard.value = card
  cardDetails.value = null
  cardDetailsError.value = ''
  showCardDetails.value = true
  isLoadingCardDetails.value = true
  try {
    cardDetails.value = await $fetch<CardDetails>(`/api/demo/cards/${card.id}/details`)
  } catch (caughtError: unknown) {
    const apiError = caughtError as { data?: { detail?: string }; message?: string }
    cardDetailsError.value = apiError.data?.detail || apiError.message || 'Card details could not be loaded.'
  } finally {
    isLoadingCardDetails.value = false
  }
}

function closeCardDetails() {
  showCardDetails.value = false
  cardDetails.value = null
  cardDetailsError.value = ''
}

async function copyCardDetail(value: string, label: string) {
  try {
    await navigator.clipboard.writeText(value.replace(/\s/g, ''))
    toastMessage.value = `${label} copied`
    window.setTimeout(() => { toastMessage.value = '' }, 2500)
  } catch {
    cardDetailsError.value = 'Clipboard access is unavailable in this browser.'
  }
}

function isCredit(type: string) {
  return type.toLowerCase().includes('deposit') || type.toLowerCase().includes('transfer in')
}

function transactionIcon(type: string) {
  if (type.toLowerCase().includes('deposit') || type.toLowerCase().includes('transfer in')) return 'mdi:arrow-bottom-left'
  if (type.toLowerCase().includes('transfer')) return 'mdi:swap-horizontal'
  return 'mdi:arrow-top-right'
}

function dateLabel(timestamp: string) {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(timestamp))
}

function openAction(action: ActionType, card?: VirtualCard) {
  actionError.value = ''
  amountValue.value = ''
  paymentForm.recipient = ''
  cardPurchaseForm.merchant = ''
  selectedCardId.value = card?.id ?? null
  singleAccountId.value = accounts.value[0]?.id
  transferForm.source_account_id = accounts.value[0]?.id ?? 0
  transferForm.destination_account_id = accounts.value[1]?.id ?? 0
  accountForm.account_type = availableAccountTypes.value[0] ?? 'Current'
  cardForm.account_id = card?.account_id ?? accounts.value[0]?.id ?? 0
  cardForm.card_type = 'Debit'
  cardForm.spending_limit = '500.00'
  cardForm.credit_limit = '1000.00'
  cardControlsForm.spending_limit = String(card?.spending_limit ?? '')
  cardPaymentAccountId.value = card?.account_id ?? accounts.value[0]?.id ?? 0
  activeAction.value = action
}

function closeAction() {
  if (isSubmitting.value) return
  activeAction.value = null
  actionError.value = ''
}

function swapAccounts() {
  const previousSource = transferForm.source_account_id
  transferForm.source_account_id = transferForm.destination_account_id
  transferForm.destination_account_id = previousSource
}

async function submitAction() {
  if (!activeAction.value) return
  isSubmitting.value = true
  actionError.value = ''
  try {
    if (activeAction.value === 'card') {
      await $fetch('/api/demo/cards', { method: 'POST', body: { ...cardForm, spending_limit: Number(cardForm.spending_limit), credit_limit: Number(cardForm.credit_limit) } })
    } else if (activeAction.value === 'cardPurchase') {
      if (!selectedCard.value) throw new Error('Select a virtual card first.')
      await $fetch(`/api/demo/cards/${selectedCard.value.id}/purchases`, { method: 'POST', body: { amount: Number(amountValue.value), merchant: cardPurchaseForm.merchant } })
    } else if (activeAction.value === 'cardPayment') {
      if (!selectedCard.value) throw new Error('Select a virtual card first.')
      await $fetch(`/api/demo/cards/${selectedCard.value.id}/payments`, { method: 'POST', body: { account_id: cardPaymentAccountId.value, amount: Number(amountValue.value) } })
    } else if (activeAction.value === 'cardControls') {
      if (!selectedCard.value) throw new Error('Select a virtual card first.')
      await $fetch(`/api/demo/cards/${selectedCard.value.id}/controls`, { method: 'PATCH', body: { spending_limit: Number(cardControlsForm.spending_limit) } })
    } else if (activeAction.value === 'account') {
      await $fetch('/api/demo/accounts', { method: 'POST', body: accountForm })
    } else if (activeAction.value === 'deposit') {
      await $fetch('/api/demo/deposits', { method: 'POST', body: { account_id: singleAccountId.value, amount: Number(amountValue.value) } })
    } else if (activeAction.value === 'payment') {
      await $fetch('/api/demo/payments', { method: 'POST', body: { account_id: singleAccountId.value, amount: Number(amountValue.value), recipient: paymentForm.recipient } })
    } else {
      await $fetch('/api/demo/transfers', { method: 'POST', body: { ...transferForm, amount: Number(amountValue.value) } })
    }
    const successMessages: Record<ActionType, string> = {
      deposit: 'Simulated deposit added',
      payment: 'Simulated payment complete',
      transfer: 'Your transfer is complete',
      account: 'Your new account is ready',
      card: 'Your virtual card is ready',
      cardPurchase: 'Simulated purchase complete',
      cardPayment: 'Credit balance payment complete',
      cardControls: 'Card controls updated',
    }
    toastMessage.value = successMessages[activeAction.value]
    activeAction.value = null
    await refresh()
    window.setTimeout(() => { toastMessage.value = '' }, 3500)
  } catch (caughtError: unknown) {
    const apiError = caughtError as { data?: { detail?: string }; message?: string }
    actionError.value = apiError.data?.detail || apiError.message || 'That action could not be completed. Try again.'
  } finally {
    isSubmitting.value = false
  }
}

async function changeCardStatus(card: VirtualCard, status: VirtualCard['status']) {
  if (status === 'Closed' && !window.confirm('Close this virtual card? It cannot be reactivated.')) return
  try {
    await $fetch(`/api/demo/cards/${card.id}/status`, { method: 'PATCH', body: { status } })
    await refresh()
    toastMessage.value = status === 'Closed' ? 'Virtual card closed' : `Virtual card ${status.toLowerCase()}`
    window.setTimeout(() => { toastMessage.value = '' }, 3500)
  } catch (caughtError: unknown) {
    const apiError = caughtError as { data?: { detail?: string }; message?: string }
    toastMessage.value = apiError.data?.detail || apiError.message || 'Card status could not be updated.'
  }
}
</script>

<style>
:root {
  --ink: #1c2925;
  --muted: #78837e;
  --line: #e7eae6;
  --paper: #f7f8f5;
  --white: #fff;
  --green: #19765f;
  --green-deep: #153f35;
  --green-soft: #e5f2ec;
  --orange: #c8794d;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: 'Avenir Next', Avenir, 'Segoe UI', sans-serif; font-size: 14px; -webkit-font-smoothing: antialiased; }
button, input, select { font: inherit; }
button { color: inherit; }
.bank-shell { min-height: 100vh; }
.sidebar { position: fixed; inset: 0 auto 0 0; z-index: 5; display: flex; width: 244px; flex-direction: column; border-right: 1px solid var(--line); background: #fff; padding: 27px 18px 17px; }
.brand { display: flex; width: fit-content; align-items: center; gap: 10px; color: var(--ink); text-decoration: none; }
.brand-mark { display: grid; width: 33px; height: 33px; place-items: center; border-radius: 10px; background: var(--green-deep); color: #d4e7d7; font-size: 21px; }
.brand-name { font-family: Georgia, 'Times New Roman', serif; font-size: 22px; letter-spacing: 0; }
.brand-name span { color: var(--green); }
.environment-tag { display: flex; align-items: center; gap: 7px; margin: 29px 5px 36px; color: #89918d; font-size: 9px; font-weight: 800; letter-spacing: 1px; }
.environment-tag > span, .sandbox-pill > span { width: 7px; height: 7px; flex: 0 0 auto; border-radius: 50%; background: #d09851; box-shadow: 0 0 0 3px #fbf2e3; }
.side-nav { display: grid; gap: 5px; }
.nav-label, .eyebrow { margin: 0; color: #87918c; font-size: 10px; font-weight: 800; letter-spacing: 1.15px; }
.nav-label { margin: 0 10px 11px; }
.nav-link { display: flex; align-items: center; gap: 12px; min-height: 42px; padding: 0 11px; border-radius: 6px; color: #68736e; font-size: 13px; font-weight: 600; text-decoration: none; transition: background .18s, color .18s; }
.nav-link .icon { font-size: 18px; }
.nav-link:hover, .nav-link.active { background: #edf5f0; color: var(--green-deep); }
.nav-link.active { font-weight: 750; }
.sidebar-bottom { margin-top: auto; }
.help-line { display: flex; align-items: center; gap: 10px; padding: 14px 9px 18px; color: #567268; font-size: 11px; font-weight: 700; line-height: 1.55; }
.help-line > .icon { color: var(--green); font-size: 20px; }
.help-line small { color: #89918d; font-size: 10px; font-weight: 500; }
.profile { display: flex; align-items: center; gap: 10px; border-top: 1px solid var(--line); padding: 16px 3px 0; }
.avatar { display: grid; width: 33px; height: 33px; flex: 0 0 auto; place-items: center; border-radius: 50%; background: #e9d7c1; color: #6b523a; font-size: 11px; font-weight: 800; }
.profile-copy { display: grid; min-width: 0; gap: 3px; }
.profile-copy strong { overflow: hidden; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.profile-copy span { color: #89918d; font-size: 10px; }
.profile-chevron { margin-left: auto; color: #929b96; }
.main-content { min-height: 100vh; margin-left: 244px; }
.topbar { display: flex; height: 65px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); background: rgba(255,255,255,.86); padding: 0 42px; }
.breadcrumbs, .topbar-right { display: flex; align-items: center; gap: 10px; }
.breadcrumbs { color: #858f8a; font-size: 11px; }
.breadcrumbs .icon { font-size: 15px; }
.breadcrumbs strong { color: #47524d; font-weight: 700; }
.topbar-right { gap: 21px; }
.sandbox-pill { display: flex; align-items: center; gap: 9px; color: #68746e; font-size: 11px; }
.sandbox-pill > span { width: 6px; height: 6px; background: #55a47e; box-shadow: 0 0 0 3px #e5f1e9; }
.icon-button { position: relative; display: grid; width: 34px; height: 34px; place-items: center; border: 1px solid transparent; border-radius: 6px; background: transparent; color: #65716b; cursor: pointer; font-size: 19px; }
.icon-button:hover { border-color: var(--line); background: #fff; }
.icon-button i { position: absolute; top: 6px; right: 6px; width: 5px; height: 5px; border-radius: 50%; background: var(--orange); }
.content-wrap { width: min(1120px, 100%); margin: 0 auto; padding: 42px 42px 25px; }
.welcome-row { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin-bottom: 25px; }
.welcome-row .eyebrow { margin-bottom: 9px; }
h1, h2, p { margin-top: 0; }
h1 { margin-bottom: 5px; font-family: Georgia, 'Times New Roman', serif; font-size: 34px; font-weight: 400; letter-spacing: 0; line-height: 1.15; }
.heading-dot { color: #bf8056; }
.welcome-subtitle { margin: 0; color: var(--muted); font-size: 12px; }
.open-account-button { display: inline-flex; min-height: 38px; align-items: center; justify-content: center; gap: 7px; border: 1px solid #dce4de; border-radius: 5px; background: #fff; padding: 0 13px; color: #385b4f; font-size: 11px; font-weight: 700; cursor: pointer; transition: background .2s, border-color .2s; }
.open-account-button:hover { border-color: #aac7b8; background: #f2f8f4; }
.open-account-button:disabled { cursor: not-allowed; opacity: .48; }
.open-account-button .icon { font-size: 17px; }
.banner { display: flex; align-items: center; gap: 8px; margin: 0 0 16px; border-radius: 5px; padding: 11px 13px; font-size: 12px; }
.error-banner { border: 1px solid #f0c7bc; background: #fff4f1; color: #9b4c3a; }
.balance-panel { position: relative; display: flex; min-height: 179px; align-items: center; overflow: hidden; border-radius: 8px; background: var(--green-deep); padding: 27px 31px; color: #fff; }
.balance-main { position: relative; z-index: 1; min-width: 40%; }
.balance-label { display: flex; align-items: center; gap: 8px; color: #b4c9be; font-size: 9px; font-weight: 800; letter-spacing: 1px; }
.balance-spark { display: grid; width: 23px; height: 23px; place-items: center; border: 1px solid rgba(207,229,216,.24); border-radius: 5px; color: #c8dfd1; font-size: 14px; }
.balance-period { margin-left: 4px; color: #89a79a; font-size: 8px; letter-spacing: .65px; }
.balance-value { margin: 13px 0 9px; font-family: Georgia, 'Times New Roman', serif; font-size: 37px; font-weight: 400; letter-spacing: 0; }
.loading-value { color: #a7bcb2; font-size: 23px; }
.balance-footnote { display: flex; align-items: center; gap: 5px; color: #a6beb1; font-size: 10px; }
.positive-mark { display: grid; width: 15px; height: 15px; place-items: center; border-radius: 50%; background: rgba(160,211,176,.18); color: #a9d8b4; font-size: 12px; }
.balance-divider { position: relative; z-index: 1; width: 1px; height: 82px; margin: 0 34px 0 15px; background: rgba(221,240,227,.16); }
.balance-stat { position: relative; z-index: 1; display: flex; flex: 1; align-items: flex-start; gap: 11px; padding-right: 15px; }
.stat-icon { display: grid; width: 30px; height: 30px; flex: 0 0 auto; place-items: center; border-radius: 7px; font-size: 17px; }
.stat-icon.incoming { background: rgba(163,215,177,.16); color: #b1dfbc; }
.stat-icon.outgoing { background: rgba(221,162,131,.16); color: #e9b69b; }
.balance-stat > div { display: grid; gap: 6px; }
.stat-label { color: #afc4b8; font-size: 10px; }
.balance-stat strong { font-size: 15px; font-weight: 700; }
.balance-stat small { color: #85a195; font-size: 9px; }
.balance-pattern { position: absolute; top: -75px; right: -45px; width: 300px; height: 300px; border: 1px solid rgba(219,239,224,.08); border-radius: 50%; box-shadow: 0 0 0 25px rgba(219,239,224,.025), 0 0 0 55px rgba(219,239,224,.02), 0 0 0 90px rgba(219,239,224,.016); }
.quick-actions { display: flex; align-items: center; gap: 10px; margin: 15px 0 32px; }
.action-button { display: flex; min-height: 49px; align-items: center; gap: 10px; border: 1px solid #e3e8e3; border-radius: 6px; background: #fff; padding: 0 14px 0 10px; color: #394741; font-size: 11px; font-weight: 700; cursor: pointer; transition: border-color .15s, transform .15s, background .15s; }
.action-button:hover { transform: translateY(-1px); border-color: #b9cec2; background: #fbfdfb; }
.action-button:disabled { cursor: not-allowed; opacity: .5; transform: none; }
.action-button.action-primary { border-color: var(--green); background: var(--green); color: #fff; }
.action-button.action-primary:hover { background: #12674f; }
.action-icon { display: grid; width: 27px; height: 27px; place-items: center; border-radius: 5px; background: #edf3ef; color: var(--green); font-size: 16px; }
.action-primary .action-icon { background: rgba(255,255,255,.14); color: #fff; }
.action-note { display: flex; align-items: center; gap: 5px; margin-left: auto; color: #87918c; font-size: 10px; }
.action-note .icon { font-size: 14px; }
.section-block { margin-top: 31px; }
.section-heading { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 14px; }
.section-heading .eyebrow { margin-bottom: 5px; }
h2 { display: flex; align-items: center; gap: 9px; margin: 0; font-family: Georgia, 'Times New Roman', serif; font-size: 22px; font-weight: 400; letter-spacing: 0; }
.count-badge { display: grid; min-width: 20px; height: 20px; place-items: center; border-radius: 50%; background: #e9efea; color: #557064; font-family: 'Avenir Next', Avenir, 'Segoe UI', sans-serif; font-size: 9px; font-weight: 700; }
.text-link { display: inline-flex; align-items: center; gap: 5px; border: 0; background: transparent; color: var(--green); font-size: 11px; font-weight: 700; cursor: pointer; }
.text-link:hover { color: #11563f; }
.text-link:disabled { cursor: not-allowed; opacity: .45; }
.text-link .icon { font-size: 15px; }
.account-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 13px; }
.account-card { min-width: 0; min-height: 151px; border: 1px solid #e6e9e5; border-radius: 7px; background: #fff; padding: 17px 18px 14px; }
.account-card.savings-card { background: #fff; }
.account-card-top { display: flex; align-items: center; gap: 9px; }
.account-icon { display: grid; width: 31px; height: 31px; place-items: center; border-radius: 7px; background: #eaf3ee; color: #36775e; font-size: 18px; }
.savings-card .account-icon { background: #f7efe4; color: #a87945; }
.account-kind { color: #52615a; font-size: 11px; font-weight: 700; }
.more-button { display: grid; width: 28px; height: 28px; place-items: center; margin-left: auto; border: 0; border-radius: 4px; background: transparent; color: #8b9690; cursor: pointer; font-size: 19px; }
.more-button:hover { background: #f2f5f2; }
.account-balance { margin: 15px 0 13px; font-family: Georgia, 'Times New Roman', serif; font-size: 25px; letter-spacing: 0; }
.account-card-bottom { display: flex; justify-content: space-between; border-top: 1px solid #eff1ee; padding-top: 10px; color: #8b9690; font-size: 8px; font-weight: 700; letter-spacing: .75px; }
.account-card-bottom span:last-child { color: #52615a; font-family: 'Avenir Next', Avenir, 'Segoe UI', sans-serif; font-size: 9px; letter-spacing: 1.3px; }
.skeleton-card { min-height: 151px; background: linear-gradient(100deg, #fff 25%, #f3f5f2 45%, #fff 65%); background-size: 200% 100%; animation: shimmer 1.5s linear infinite; }
@keyframes shimmer { to { background-position-x: -200%; } }
.empty-state { border: 1px dashed #d4ddd6; border-radius: 7px; padding: 24px; color: #7a8580; text-align: center; }
.cards-section { margin-top: 36px; }
.card-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 13px; }
.virtual-card { min-width: 0; overflow: hidden; border: 1px solid #e4e9e4; border-radius: 8px; background: #fff; }
.virtual-card-face { position: relative; display: flex; min-height: 188px; flex-direction: column; justify-content: space-between; overflow: hidden; aspect-ratio: 1.83; border-radius: 7px; padding: 17px 19px 14px; color: #f8fbf8; }
.virtual-card-face::after { position: absolute; inset: 0; background: repeating-linear-gradient(132deg, transparent 0 27px, rgba(255,255,255,.035) 28px 29px); content: ''; pointer-events: none; }
.virtual-card.debit .virtual-card-face { background: linear-gradient(125deg, #173d34, #216b54 65%, #438768); }
.virtual-card.credit .virtual-card-face { background: linear-gradient(125deg, #603b30, #9a5942 63%, #bd7951); }
.virtual-card-face.face-frozen { filter: saturate(.36); }
.virtual-card-head, .virtual-card-foot { position: relative; z-index: 1; display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.card-brand { font-family: Georgia, 'Times New Roman', serif; font-size: 17px; }
.card-brand span { color: #bdd6c4; }
.credit .card-brand span { color: #f0c2a4; }
.card-type-label { border: 1px solid rgba(255,255,255,.25); border-radius: 20px; padding: 5px 7px; color: rgba(255,255,255,.85); font-size: 7px; font-weight: 800; letter-spacing: .8px; white-space: nowrap; }
.card-chip-row { position: relative; z-index: 1; display: flex; align-items: center; justify-content: space-between; margin-top: 11px; }
.card-chip { position: relative; width: 30px; height: 23px; overflow: hidden; border: 1px solid rgba(81,65,39,.4); border-radius: 5px; background: linear-gradient(135deg, #d9c59b, #b59a68); }
.card-chip::before, .card-chip::after { position: absolute; background: rgba(93,75,45,.34); content: ''; }
.card-chip::before { top: 0; bottom: 0; left: 9px; width: 1px; box-shadow: 10px 0 rgba(93,75,45,.34); }
.card-chip::after { top: 10px; right: 0; left: 0; height: 1px; }
.contactless-icon { color: rgba(255,255,255,.7); font-size: 18px; }
.card-number { position: relative; z-index: 1; margin: 1px 0 0; font-family: Consolas, 'Courier New', monospace; font-size: 14px; letter-spacing: 1px; white-space: nowrap; }
.virtual-card-foot { align-items: flex-end; margin-top: 9px; }
.virtual-card-foot > span { display: grid; gap: 4px; overflow: hidden; font-size: 9px; font-weight: 700; text-overflow: ellipsis; text-transform: uppercase; white-space: nowrap; }
.virtual-card-foot small { color: rgba(255,255,255,.62); font-size: 6px; font-weight: 700; letter-spacing: .8px; }
.virtual-card-foot strong { color: rgba(255,255,255,.88); font-size: 14px; letter-spacing: 1px; }
.card-state { position: absolute; z-index: 2; top: 47px; right: 19px; border-radius: 10px; background: rgba(255,255,255,.15); padding: 4px 7px; color: #fff; font-size: 7px; font-weight: 800; text-transform: uppercase; }
.card-state.state-frozen { background: #fff0cf; color: #715522; }
.card-state.state-closed { background: #f8dcd7; color: #853f33; }
.card-info-row, .credit-balance-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 12px 14px 0; color: #849089; font-size: 9px; }
.card-info-row strong, .credit-balance-row strong { color: #52615a; font-size: 10px; text-align: right; }
.credit-balance-row { padding-top: 8px; }
.card-actions { display: flex; flex-wrap: wrap; gap: 6px; padding: 12px 12px 13px; }
.card-actions button { display: inline-flex; min-height: 30px; flex: 1 1 auto; align-items: center; justify-content: center; gap: 5px; border: 1px solid #e7ebe7; border-radius: 5px; background: #fff; padding: 0 8px; color: #596760; font-size: 9px; font-weight: 700; cursor: pointer; }
.card-actions button:hover { border-color: #b6cbbd; background: #f7faf7; color: #28614b; }
.card-actions button:disabled { cursor: not-allowed; opacity: .45; }
.card-actions button .icon { font-size: 14px; }
.card-actions button.close-card-action { flex: 0 0 auto; color: #9c6255; }
.card-empty-state { display: grid; justify-items: center; gap: 8px; border: 1px dashed #d4ddd6; border-radius: 7px; padding: 24px 18px; color: #87918c; text-align: center; }
.card-empty-state strong { color: #4b5b53; font-size: 12px; }
.card-empty-state > span:not(.card-empty-icon) { max-width: 360px; font-size: 10px; line-height: 1.5; }
.card-empty-icon { display: grid; width: 36px; height: 36px; place-items: center; border-radius: 50%; background: #edf4ef; color: var(--green); font-size: 19px; }
.card-activity { margin-top: 15px; border: 1px solid #e6e9e5; border-radius: 7px; background: #fff; padding: 13px 15px 2px; }
.card-activity-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; border-bottom: 1px solid #edf0ec; padding-bottom: 10px; }
.card-activity-heading h3 { margin: 0; color: #4b5a53; font-family: Georgia, 'Times New Roman', serif; font-size: 15px; font-weight: 400; }
.card-activity-heading > span { color: #929b96; font-size: 9px; }
.card-activity-row { display: flex; min-height: 47px; align-items: center; gap: 9px; border-bottom: 1px solid #f0f2ef; }
.card-activity-row:last-child { border-bottom: 0; }
.card-activity-icon { display: grid; width: 27px; height: 27px; flex: 0 0 auto; place-items: center; border-radius: 50%; background: #f8eee9; color: #b96e4f; font-size: 14px; }
.card-activity-icon.payment { background: #eaf4ec; color: #378256; }
.card-activity-copy { display: grid; min-width: 0; flex: 1; gap: 3px; }
.card-activity-copy strong { overflow: hidden; color: #45534c; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
.card-activity-copy small { color: #929b96; font-size: 8px; }
.card-activity-amount { font-size: 9px; white-space: nowrap; }
.selected-card-note { display: flex; align-items: center; gap: 7px; margin: -3px 0 0; border-radius: 5px; background: #f3f7f3; padding: 9px 10px; color: #5c7065; font-size: 10px; }
.selected-card-note .icon { font-size: 15px; }
.card-details-modal { max-width: 470px; }
.details-loading { display: flex; align-items: center; gap: 8px; color: #728078; font-size: 12px; }
.card-details-list { display: grid; gap: 10px; }
.card-detail-row { display: flex; min-width: 0; align-items: center; justify-content: space-between; gap: 10px; border: 1px solid #e8ece8; border-radius: 6px; background: #fbfcfb; padding: 11px 12px; }
.card-detail-row > div { display: grid; min-width: 0; gap: 6px; }
.card-detail-row span { color: #87918c; font-size: 9px; }
.card-detail-row strong { overflow-wrap: anywhere; color: #33443b; font-size: 12px; }
.card-detail-row strong.detail-number { font-family: Consolas, 'Courier New', monospace; font-size: 13px; letter-spacing: 1px; }
.card-details-pair { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }
.detail-copy { display: grid; width: 31px; height: 31px; flex: 0 0 auto; place-items: center; border: 1px solid #e2e8e2; border-radius: 5px; background: #fff; color: #4d7060; cursor: pointer; font-size: 15px; }
.detail-copy:hover { border-color: #aac7b8; background: #f3f8f4; }
.detail-status { border-radius: 12px; background: #e6f3e9; padding: 5px 8px; color: #397153 !important; font-size: 8px !important; font-weight: 800; text-transform: uppercase; }
.activity-section { margin-top: 36px; }
.activity-heading { margin-bottom: 10px; }
.filter-button { display: flex; align-items: center; gap: 7px; min-height: 32px; border: 1px solid #e2e7e2; border-radius: 5px; background: #fff; padding: 0 9px; color: #68746e; font-size: 10px; cursor: pointer; }
.filter-button:hover { border-color: #b7cbbd; }
.filter-button .icon { font-size: 14px; }
.activity-table-wrap { overflow: hidden; border: 1px solid #e6e9e5; border-radius: 7px; background: #fff; }
.activity-table { width: 100%; border-collapse: collapse; text-align: left; }
.activity-table th { height: 37px; border-bottom: 1px solid #edf0ec; padding: 0 16px; color: #909a95; font-size: 8px; font-weight: 800; letter-spacing: .8px; }
.activity-table td { height: 58px; border-bottom: 1px solid #f0f2ef; padding: 7px 16px; color: #52615a; font-size: 10px; }
.activity-table tbody tr:last-child td { border-bottom: 0; }
.transaction-cell { display: flex; align-items: center; gap: 10px; }
.transaction-cell > span:last-child { display: grid; gap: 4px; }
.transaction-cell strong { max-width: 250px; overflow: hidden; color: #35423c; font-size: 10px; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.transaction-cell small { color: #929b96; font-size: 9px; }
.transaction-icon { display: grid; width: 30px; height: 30px; flex: 0 0 auto; place-items: center; border-radius: 50%; font-size: 15px; }
.transaction-icon.credit { background: #eaf4ec; color: #378256; }
.transaction-icon.debit { background: #f8eee9; color: #b96e4f; }
.table-account { display: inline-block; border-radius: 4px; background: #f3f5f2; padding: 5px 7px; color: #627068; font-size: 9px; }
.date-cell { color: #87918c !important; white-space: nowrap; }
.amount-column { text-align: right !important; white-space: nowrap; }
.amount-column strong { font-size: 10px; }
.amount-positive { color: #27805f; }
.amount-negative { color: #a35c43; }
.empty-activity { display: grid; justify-items: center; gap: 7px; padding: 34px 16px 38px; color: #8a948f; font-size: 10px; }
.empty-activity strong { color: #51615a; font-size: 12px; }
.empty-icon { display: grid; width: 36px; height: 36px; place-items: center; margin-bottom: 3px; border-radius: 50%; background: #edf4ef; color: var(--green); font-size: 19px; }
.page-footer { display: flex; justify-content: space-between; gap: 15px; margin-top: 22px; color: #9aa39e; font-size: 9px; }
.page-footer span:first-child { font-weight: 800; letter-spacing: .6px; }
.modal-backdrop { position: fixed; inset: 0; z-index: 20; display: grid; place-items: center; overflow-y: auto; background: rgba(20, 37, 31, .48); padding: 20px; animation: fade-in .16s ease-out; }
.action-modal { width: min(100%, 430px); border: 1px solid rgba(255,255,255,.6); border-radius: 9px; background: #fff; padding: 25px; box-shadow: 0 22px 80px rgba(20,37,31,.22); animation: modal-in .2s ease-out; }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes modal-in { from { transform: translateY(7px); opacity: .6; } to { transform: translateY(0); opacity: 1; } }
.modal-topline { display: flex; align-items: center; justify-content: space-between; margin-bottom: 17px; }
.modal-icon { display: grid; width: 39px; height: 39px; place-items: center; border-radius: 8px; background: #eaf3ee; color: var(--green); font-size: 21px; }
.modal-close { border-color: #edf0ed; }
.action-modal .eyebrow { margin-bottom: 7px; }
.action-modal h2 { font-size: 25px; }
.modal-description { margin: 7px 0 21px; color: #7f8984; font-size: 11px; line-height: 1.55; }
.action-form { display: grid; gap: 14px; }
.action-form label { display: grid; gap: 7px; color: #58655f; font-size: 10px; font-weight: 700; }
.action-form select, .action-form input { width: 100%; min-height: 42px; border: 1px solid #dfe5df; border-radius: 5px; outline: 0; background: #fff; padding: 0 11px; color: #35423c; font-size: 12px; }
.action-form select:focus, .action-form input:focus { border-color: #6b9e85; box-shadow: 0 0 0 3px #e9f3ed; }
.action-form input::placeholder { color: #adb5b0; }
.amount-input { position: relative; }
.amount-input > span { position: absolute; top: 50%; left: 12px; transform: translateY(-50%); color: #88938d; font-size: 13px; }
.amount-input input { padding-left: 27px; }
.swap-accounts { display: grid; width: 29px; height: 29px; place-items: center; justify-self: center; margin: -7px 0; border: 1px solid #e3e9e3; border-radius: 50%; background: #f8faf8; color: var(--green); cursor: pointer; font-size: 17px; }
.modal-notice { display: flex; align-items: flex-start; gap: 7px; margin: 0; border-radius: 5px; background: #f3f7f3; padding: 10px; color: #728078; font-size: 10px; line-height: 1.5; }
.modal-notice .icon { flex: 0 0 auto; color: #4b8a68; font-size: 15px; }
.form-error { display: flex; align-items: center; gap: 6px; margin: 0; color: #a34432; font-size: 11px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 5px; border-top: 1px solid #edf0ed; padding-top: 15px; }
.cancel-button, .submit-button { display: inline-flex; min-height: 38px; align-items: center; justify-content: center; gap: 7px; border-radius: 5px; padding: 0 13px; font-size: 11px; font-weight: 700; cursor: pointer; }
.cancel-button { border: 1px solid #e1e6e1; background: #fff; color: #65716b; }
.cancel-button:hover { background: #f8faf8; }
.submit-button { border: 1px solid var(--green); background: var(--green); color: #fff; }
.submit-button:hover { background: #12674f; }
.submit-button:disabled { cursor: wait; opacity: .65; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.toast-message { position: fixed; right: 24px; bottom: 24px; z-index: 30; display: flex; align-items: center; gap: 9px; border: 1px solid #cde2d2; border-radius: 6px; background: #fff; padding: 12px 16px; color: #376c4f; box-shadow: 0 8px 28px rgba(31,68,48,.12); font-size: 12px; font-weight: 700; }
.toast-message .icon { font-size: 17px; }
.toast-enter-active, .toast-leave-active { transition: opacity .18s, transform .18s; }
.toast-enter-from, .toast-leave-to { transform: translateY(6px); opacity: 0; }

@media (min-width: 1500px) { .content-wrap { padding-right: 60px; padding-left: 60px; } }
@media (max-width: 1100px) {
  .sidebar { width: 210px; }
  .main-content { margin-left: 210px; }
  .topbar { padding: 0 28px; }
  .content-wrap { padding: 34px 28px 24px; }
  .balance-panel { padding: 23px; }
  .balance-divider { margin-right: 22px; }
  .balance-main { min-width: 38%; }
  .balance-stat { gap: 8px; }
  .action-note { display: none; }
}
@media (max-width: 760px) {
  .sidebar { position: sticky; inset: 0 0 auto; width: 100%; height: auto; min-height: 58px; flex-direction: row; align-items: center; justify-content: space-between; border-right: 0; border-bottom: 1px solid var(--line); padding: 10px 17px; }
  .brand-mark { width: 30px; height: 30px; }
  .brand-name { font-size: 20px; }
  .environment-tag { margin: 0 0 0 auto; font-size: 8px; }
  .side-nav, .sidebar-bottom { display: none; }
  .main-content { margin-left: 0; }
  .topbar { height: 49px; padding: 0 18px; }
  .topbar-right { gap: 10px; }
  .content-wrap { padding: 29px 18px 22px; }
  .welcome-row { align-items: flex-start; margin-bottom: 20px; }
  h1 { font-size: 29px; }
  .welcome-subtitle { max-width: 240px; line-height: 1.5; }
  .open-account-button { min-height: 35px; padding: 0 9px; font-size: 10px; white-space: nowrap; }
  .balance-panel { min-height: unset; flex-wrap: wrap; gap: 17px 0; padding: 20px; }
  .balance-main { width: 100%; min-width: 100%; }
  .balance-divider { display: none; }
  .balance-value { font-size: 34px; }
  .balance-stat { flex: 1 1 50%; gap: 8px; }
  .balance-stat strong { font-size: 13px; }
  .balance-pattern { top: -160px; right: -110px; }
  .quick-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin: 12px 0 28px; }
  .action-button { justify-content: flex-start; min-height: 45px; gap: 7px; padding: 0 8px; font-size: 10px; }
  .action-button:last-of-type { grid-column: 1 / -1; }
  .action-icon { width: 25px; height: 25px; flex: 0 0 auto; }
  .section-block { margin-top: 27px; }
  .account-grid { gap: 9px; }
  .card-grid { grid-template-columns: 1fr; }
  .virtual-card-face { min-height: 180px; }
  .account-card { min-height: 137px; padding: 12px; }
  .account-balance { font-size: 21px; }
  .account-card-bottom { font-size: 7px; }
  .activity-section { margin-top: 30px; }
  .activity-table th, .activity-table td { padding-right: 9px; padding-left: 9px; }
  .activity-table th { font-size: 7px; letter-spacing: .4px; }
  .activity-table td { height: 55px; }
  .transaction-cell { gap: 7px; }
  .transaction-icon { width: 26px; height: 26px; }
  .transaction-cell strong { max-width: 145px; font-size: 9px; }
  .table-account { max-width: 88px; overflow: hidden; font-size: 8px; text-overflow: ellipsis; white-space: nowrap; }
  .date-cell { font-size: 9px !important; }
  .amount-column strong { font-size: 9px; }
  .page-footer { flex-direction: column; gap: 6px; font-size: 8px; }
}
@media (max-width: 430px) {
  .environment-tag { max-width: 128px; font-size: 7px; letter-spacing: .65px; }
  .breadcrumbs { gap: 5px; font-size: 10px; }
  .sandbox-pill { font-size: 0; gap: 0; }
  .sandbox-pill > span { width: 7px; height: 7px; }
  .welcome-row { gap: 8px; }
  h1 { font-size: 26px; }
  .open-account-button { width: 36px; height: 36px; min-height: 36px; overflow: hidden; gap: 10px; padding: 0 9px; font-size: 0; }
  .open-account-button .icon { flex: 0 0 auto; font-size: 18px; }
  .balance-panel { padding: 17px; }
  .balance-label { gap: 6px; font-size: 8px; }
  .balance-period { font-size: 7px; }
  .balance-stat { gap: 6px; }
  .stat-icon { width: 26px; height: 26px; font-size: 15px; }
  .balance-stat strong { font-size: 12px; }
  .account-grid { grid-template-columns: 1fr; }
  .account-card { min-height: 129px; padding: 13px 15px; }
  .activity-table th:nth-child(2), .activity-table td:nth-child(2) { display: none; }
  .activity-table th, .activity-table td { padding-right: 8px; padding-left: 8px; }
  .activity-table th { font-size: 7px; }
  .transaction-cell strong { max-width: 135px; }
  .date-cell { font-size: 8px !important; }
  .amount-column strong { font-size: 8px; }
  .action-modal { padding: 20px; }
}
</style>