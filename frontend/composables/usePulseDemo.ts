import { computed } from 'vue'

interface ApiClient {
  client_id: string
  first_name: string
  last_name: string
  display_name: string
  age: number
  persona_type: string
  civil_status: string
  profession: string
  monthly_net_income: number
  investor_profile: string
  kbc_segment: string
  ai_consent_active: boolean
}

interface ApiNudge {
  nudge_id: string
  priority: 'HIGH' | 'MEDIUM' | 'LOW'
  category: string
  title: string
  description: string
  explainability_reason: string
  confidence_score: number
  status: 'PENDING' | 'ACCEPTED' | 'DISMISSED'
}

interface DashboardResponse {
  client: ApiClient
  summary: {
    total_available_capital: number
    liquid_cash: number
    savings_account: number
    investments_value: number
    total_monthly_deficits_or_debts: number
    net_worth_trend_30d: string
  } | null
  upcoming_payments: { payment_id: number; label: string; amount: number; due_date: string; status: string }[]
  investments: { investment_id: number; holding_name: string; holding_type: string; asset_value: number; return_ytd: string }[]
  transactions: { transaction_id: string; tx_date: string; merchant: string; category: string; amount: number; tx_type: 'DEBIT' | 'CREDIT'; flag_ai_trigger: string | null }[]
  loans: { loan_id: number; loan_type: string; initial_amount: number; remaining_balance: number; monthly_payment: number; status: string; start_date: string; end_date: string }[]
  insurances: { insurance_id: number; contract_code: string; insurance_type: string; monthly_premium: number; status: string; start_date: string; end_date: string | null }[]
  nudges: ApiNudge[]
}

export interface PulseSuggestion {
  id: string
  priority: 'HAUTE' | 'MOYENNE' | 'BASSE'
  category: 'Assurance' | 'Prêt' | 'Investissement'
  sourceCategory: string
  title: string
  description: string
  explainability: string
  confidence: number
  cta: string
  status: 'active' | 'activated' | 'dismissed'
}

function categoryGroup(category: string): PulseSuggestion['category'] {
  if (category.toLocaleLowerCase('fr').includes('assurance')) return 'Assurance'
  if (category.toLocaleLowerCase('fr').includes('prêt')) return 'Prêt'
  return 'Investissement'
}

function ctaFor(category: PulseSuggestion['category']) {
  if (category === 'Assurance') return "Voir l'offre Auto"
  if (category === 'Prêt') return 'Simuler mon prêt'
  return 'Découvrir la solution'
}

export async function usePulseDemo() {
  const clientId = useCookie<string>('pulse_client_id', {
    default: () => 'kbc_user_2894',
    path: '/',
    sameSite: 'lax',
  })
  const { data, pending, error, refresh } = await useFetch<DashboardResponse>(
    () => `/api/pulse/clients/${encodeURIComponent(clientId.value)}/dashboard`,
    { key: `pulse-dashboard-${clientId.value}` },
  )

  const customer = computed(() => {
    const client = data.value?.client
    const summary = data.value?.summary
    const payments = data.value?.upcoming_payments ?? []
    const investments = data.value?.investments ?? []
    const insurances = data.value?.insurances ?? []
    return {
      id: client?.client_id ?? clientId.value,
      name: client?.display_name ?? 'Profil indisponible',
      age: client?.age ?? 0,
      profile: client?.persona_type ?? '',
      investorProfile: client?.investor_profile ?? '',
      profession: client?.profession ?? '',
      monthlyIncome: client?.monthly_net_income ?? 0,
      totalCapital: summary?.total_available_capital ?? 0,
      liquidCash: summary?.liquid_cash ?? 0,
      savings: summary?.savings_account ?? 0,
      investments: {
        total: investments.reduce((total, item) => total + item.asset_value, 0),
        trend30d: summary?.net_worth_trend_30d ?? '0%',
      },
      payments: payments.map((payment) => ({
        label: payment.label,
        amount: payment.amount,
        date: new Intl.DateTimeFormat('fr-BE', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(`${payment.due_date}T12:00:00`)),
      })),
      insurances: insurances.filter((item) => item.status === 'ACTIVE'),
      loans: data.value?.loans ?? [],
    }
  })

  const suggestions = computed<PulseSuggestion[]>(() => (data.value?.nudges ?? []).map((nudge) => {
    const category = categoryGroup(nudge.category)
    return {
      id: nudge.nudge_id,
      priority: nudge.priority === 'HIGH' ? 'HAUTE' : nudge.priority === 'MEDIUM' ? 'MOYENNE' : 'BASSE',
      category,
      sourceCategory: nudge.category,
      title: nudge.title,
      description: nudge.description,
      explainability: nudge.explainability_reason,
      confidence: nudge.confidence_score,
      cta: ctaFor(category),
      status: nudge.status === 'PENDING' ? 'active' : nudge.status === 'ACCEPTED' ? 'activated' : 'dismissed',
    }
  }))

  const activeSuggestionCount = computed(() => suggestions.value.filter((item) => item.status === 'active').length)
  const toastMessage = useState('pulse-toast', () => '')

  function notify(message: string) {
    toastMessage.value = message
    if (import.meta.client) {
      window.setTimeout(() => {
        if (toastMessage.value === message) toastMessage.value = ''
      }, 2800)
    }
  }

  async function updateSuggestion(id: string, status: 'ACCEPTED' | 'DISMISSED') {
    try {
      await $fetch(`/api/pulse/clients/${encodeURIComponent(clientId.value)}/nudges/${encodeURIComponent(id)}`, {
        method: 'PATCH',
        body: { status },
      })
      await refresh()
      notify(status === 'ACCEPTED' ? 'Suggestion enregistrée dans votre espace (démo).' : 'Suggestion ignorée')
    } catch {
      notify('Impossible de mettre à jour cette suggestion. Vérifiez la connexion à la base.')
    }
  }

  function activateSuggestion(id: string) {
    return updateSuggestion(id, 'ACCEPTED')
  }

  function dismissSuggestion(id: string) {
    return updateSuggestion(id, 'DISMISSED')
  }

  return { clientId, customer, dashboard: data, pending, error, refresh, suggestions, activeSuggestionCount, toastMessage, notify, activateSuggestion, dismissSuggestion }
}
